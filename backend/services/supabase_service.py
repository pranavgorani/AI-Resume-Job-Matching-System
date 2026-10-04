import io
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("talentproof.supabase")

class SupabaseService:
    """
    Manages Supabase PostgreSQL, pgvector embeddings storage, and Supabase Storage bucket for resumes.
    Includes graceful local fallback to ensure zero runtime disruptions.
    """
    def __init__(self):
        self._url = os.getenv("SUPABASE_URL", os.getenv("NEXT_PUBLIC_SUPABASE_URL", ""))
        self._key = os.getenv("SUPABASE_PUBLISHABLE_KEY", os.getenv("SUPABASE_KEY", os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY", "")))
        self._bucket_name = os.getenv("SUPABASE_STORAGE_BUCKET", "resumes")
        self._client = None

        if self._url and self._key:
            try:
                from supabase import create_client
                self._client = create_client(self._url, self._key)
                self._init_bucket()
            except Exception as e:
                logger.warning(f"Could not initialize Supabase client: {type(e).__name__}")
                self._client = None

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    def _init_bucket(self):
        """Attempts to verify or create the resumes storage bucket."""
        if not self._client:
            return
        try:
            # Check or create bucket
            buckets = self._client.storage.list_buckets()
            bucket_names = [b.name for b in buckets] if hasattr(buckets[0], 'name') else [b['name'] for b in buckets]
            if self._bucket_name not in bucket_names:
                self._client.storage.create_bucket(self._bucket_name, options={"public": True})
        except Exception as e:
            logger.debug(f"Bucket check note: {type(e).__name__}")

    def upload_resume_pdf(
        self,
        file_bytes: bytes,
        original_filename: str,
        content_type: str = "application/pdf"
    ) -> Dict[str, str]:
        """
        Uploads resume PDF file to Supabase Storage bucket 'resumes'.
        Returns storage path and URL. Falls back to local disk if Supabase Storage is offline.
        """
        unique_id = uuid.uuid4().hex[:12]
        sanitized = original_filename.replace(" ", "_")
        storage_path = f"resumes/{unique_id}_{sanitized}"

        # Try Supabase Storage upload
        if self._client:
            try:
                res = self._client.storage.from_(self._bucket_name).upload(
                    path=storage_path,
                    file=file_bytes,
                    file_options={"content-type": content_type, "upsert": "true"}
                )
                public_url = self._client.storage.from_(self._bucket_name).get_public_url(storage_path)
                return {
                    "storage_provider": "supabase",
                    "storage_path": storage_path,
                    "file_url": public_url,
                    "filename": original_filename
                }
            except Exception as e:
                logger.warning(f"Supabase Storage upload warning ({type(e).__name__}). Using local storage fallback.")

        # Local storage fallback
        local_dir = Path("uploads")
        local_dir.mkdir(parents=True, exist_ok=True)
        local_file_path = local_dir / f"{unique_id}_{sanitized}"
        with open(local_file_path, "wb") as f:
            f.write(file_bytes)

        return {
            "storage_provider": "local",
            "storage_path": str(local_file_path),
            "file_url": f"/uploads/{local_file_path.name}",
            "filename": original_filename
        }

    def store_embedding(
        self,
        entity_type: str,
        entity_id: str,
        content: str,
        embedding: List[float]
    ) -> bool:
        """Stores pgvector embedding in Supabase embeddings table if configured."""
        if not self._client:
            return False
        try:
            data = {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "content": content,
                "embedding": embedding
            }
            self._client.table("embeddings").upsert(data).execute()
            return True
        except Exception as e:
            logger.debug(f"pgvector storage note ({type(e).__name__}) - saved to local database.")
            return False

    def query_similar_embeddings(
        self,
        query_embedding: List[float],
        entity_type: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Queries pgvector embeddings using Supabase RPC if available."""
        if not self._client:
            return []
        try:
            params = {
                "query_embedding": query_embedding,
                "match_threshold": 0.5,
                "match_count": top_k
            }
            res = self._client.rpc("match_embeddings", params).execute()
            return res.data or []
        except Exception:
            return []


supabase_service = SupabaseService()

def get_supabase_service() -> SupabaseService:
    return supabase_service
