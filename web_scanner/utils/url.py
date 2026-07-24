import random
import string
from datetime import datetime
from urllib.parse import urlparse


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
