from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ClassificationLabel(str, Enum):
    GAMBLING_WEBSITE = "GAMBLING_WEBSITE"
    SCAM_WEBSITE = "SCAM_WEBSITE"
    SAFE_WEBSITE = "SAFE_WEBSITE"
    ERR_CONNECTION_RESET = "ERR_CONNECTION_RESET"
    BLOCKED_BY_NETWORK_FILTER = "BLOCKED_BY_NETWORK_FILTER"
    BLOCKED_BY_GOVERNMENT = "BLOCKED_BY_GOVERNMENT"
    CLOUDFLARE_BLOCKED = "CLOUDFLARE_BLOCKED"


@dataclass
class ScanResult:
    scrap_id: str
    crawled_time: datetime
    website: str
    task_id: str
    classification: str

    def to_dict(self) -> dict:
        return {
            "id_scrap": self.scrap_id,
            "crawled_time": self.crawled_time,
            "website": self.website,
            "task_id": self.task_id,
            "classify_website": self.classification,
        }


class ScanRequest(BaseModel):
    urls: list[str]


class ScanResultItem(BaseModel):
    id_scrap: str
    crawled_time: datetime
    website: str
    task_id: str
    classify_website: str


class ScanResponse(BaseModel):
    results: list[ScanResultItem]
