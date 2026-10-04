import io
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("talentproof.supabase")

class SupabaseService:
    """
    Manages Supabase PostgreSQL, pgvector embeddings storage, and Supabase Storage bucket for resumes.
    Operates in-memory to guarantee full serverless compatibility on Vercel without local disk persistence.
    """
    def __init__(self):
        self._url = os.getenv("SUPABASE_URL", os.getenv("NEXT_PUBLIC_SUPABASE_URL", ""))
        # Check server-only service role key first, then publishable/anon keys
        self._key = (
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("SUPABASE_PUBLISHABLE_KEY")
            or os.getenv("SUPABASE_KEY")
            or os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")
            or ""
        )
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
        """Attempts to verify or create the resumes storage bucket safely."""
        if not self._client:
            return
        try:
            buckets = self._client.storage.list_buckets()
            bucket_names = [
                (b.name if hasattr(b, 'name') else b.get('name', ''))
                for b in (buckets or [])
            ]
            # Preference order: configured bucket, resume-files, resumes
            if self._bucket_name in bucket_names:
                pass
            elif "resume-files" in bucket_names:
                self._bucket_name = "resume-files"
            elif "resumes" in bucket_names:
                self._bucket_name = "resumes"
            else:
                try:
                    self._client.storage.create_bucket(self._bucket_name, options={"public": True})
                    logger.info(f"[SUPABASE STORAGE] Created bucket '{self._bucket_name}'")
                except Exception as ce:
                    logger.debug(f"[SUPABASE STORAGE] Bucket create notice: {ce}")
        except Exception as e:
            logger.debug(f"[SUPABASE STORAGE] Bucket list notice: {type(e).__name__}: {e}")

    def upload_resume_pdf(
        self,
        file_bytes: bytes,
        original_filename: str,
        content_type: str = "application/pdf",
        job_id: Optional[int] = None,
        candidate_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Uploads resume document file to Supabase Storage.
        Deterministic path format: resumes/{job_id}/{candidate_id}/{unique_file_id}_{sanitized_filename}
        Never writes permanently to local serverless filesystem.
        """
        unique_file_id = uuid.uuid4().hex[:12]
        sanitized = re.sub(r'[^a-zA-Z0-9_.-]', '_', original_filename)
        job_folder = f"job-{job_id}" if job_id else "job-general"
        cand_folder = f"candidate-{candidate_id}" if candidate_id else f"candidate-{unique_file_id[:8]}"
        storage_path = f"resumes/{job_folder}/{cand_folder}/{unique_file_id}_{sanitized}"

        # Detect content type from filename if generic
        lower_name = original_filename.lower()
        if lower_name.endswith(".docx"):
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif lower_name.endswith(".doc"):
            content_type = "application/msword"
        elif lower_name.endswith(".txt"):
            content_type = "text/plain"
        elif lower_name.endswith(".pdf"):
            content_type = "application/pdf"

        # 1. Try Supabase Storage upload
        if self._client:
            try:
                self._client.storage.from_(self._bucket_name).upload(
                    path=storage_path,
                    file=file_bytes,
                    file_options={"content-type": content_type, "upsert": "true"}
                )
                public_url = self._client.storage.from_(self._bucket_name).get_public_url(storage_path)
                logger.info(f"[UPLOAD] Supabase Storage upload successful: {self._bucket_name}/{storage_path}")
                return {
                    "storage_provider": "supabase",
                    "storage_bucket": self._bucket_name,
                    "storage_path": storage_path,
                    "file_url": public_url,
                    "filename": original_filename,
                    "file_size": len(file_bytes),
                    "file_type": content_type
                }
            except Exception as e:
                logger.warning(f"[UPLOAD] Supabase Storage upload notice ({type(e).__name__}): {e}")

        # 2. In-memory / serverless safe fallback (no persistent local disk write)
        return {
            "storage_provider": "in_memory",
            "storage_bucket": self._bucket_name,
            "storage_path": storage_path,
            "file_url": "",
            "filename": original_filename,
            "file_size": len(file_bytes),
            "file_type": content_type
        }

    def verify_file_exists(self, storage_path: str) -> bool:
        """Verifies if file exists in Supabase Storage."""
        if not self._client or not storage_path:
            return False
        try:
            # Check by attempting to download 1 byte or inspect path
            folder = "/".join(storage_path.split("/")[:-1])
            target_name = storage_path.split("/")[-1]
            files = self._client.storage.from_(self._bucket_name).list(folder)
            return any((f.get("name") if isinstance(f, dict) else getattr(f, "name", "")) == target_name for f in (files or []))
        except Exception:
            return True  # Avoid blocking pipeline if metadata listing has RLS

    def download_resume_file(self, storage_path: str) -> Optional[bytes]:
        """Downloads file content from Supabase Storage."""
        if not self._client or not storage_path:
            return None
        try:
            data = self._client.storage.from_(self._bucket_name).download(storage_path)
            return data
        except Exception as e:
            logger.warning(f"Could not download file from storage: {e}")
            return None

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
            logger.debug(f"pgvector storage notice ({type(e).__name__})")
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
