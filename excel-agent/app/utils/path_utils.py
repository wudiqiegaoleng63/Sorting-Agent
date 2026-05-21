from pathlib import Path

from app.core.config import settings


def safe_path(relative_path: str, base: Path | None = None) -> Path:
    """Resolve a relative path and ensure it stays within the base directory."""
    base = base or settings.base_dir
    resolved = (base / relative_path).resolve()
    if not str(resolved).startswith(str(base.resolve())):
        raise ValueError(f"Path traversal detected: {relative_path}")
    return resolved
