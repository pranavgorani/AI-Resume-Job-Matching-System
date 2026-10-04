import os
import sys
from pathlib import Path

# Configure paths so all backend imports (app.*, services.*) resolve cleanly in Vercel Serverless
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent if current_dir.name == "api" else current_dir
backend_dir = root_dir / "backend"

for p in [str(backend_dir), str(backend_dir / "app"), str(root_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("VERCEL", "1")

from app.main import app  # noqa: E402
