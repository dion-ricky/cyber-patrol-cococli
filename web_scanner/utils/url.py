import json
import random
import re
import string
from datetime import datetime
from urllib.parse import urlparse


def sanitize_json(data: dict | list) -> dict | list:
    """Sanitize data for safe JSONB storage in PostgreSQL.

    - Strips null bytes and problematic control characters
    - Validates JSON round-trip
    """
    cleaned = _strip_nulls(data)
    serialized = json.dumps(cleaned, ensure_ascii=False)
    return json.loads(serialized)


_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _strip_nulls(obj: object) -> object:
    if isinstance(obj, str):
        return _CONTROL_RE.sub("", obj)
    if isinstance(obj, dict):
        return {k: _strip_nulls(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_strip_nulls(v) for v in obj]
    return obj


def derive_site_name(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    parts = hostname.split(".")
    if len(parts) > 1:
        parts = parts[:-1]
    return ".".join(parts)


def generate_scrap_id(site_name: str) -> str:
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{site_name}_{timestamp}_{suffix}"
