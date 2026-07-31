import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config.settings import get_settings
from db.connection import get_connection
from db.migrations.runner import run_migrations
from db.repository import (
    create_scan_request,
    get_recent_scans,
    get_scan_request,
    get_scan_results_by_request,
    get_screenshot,
    get_urlscan_result_by_request,
)


class ScanRequest(BaseModel):
    url: str


class ScanResponse(BaseModel):
    request_id: str
    status: str


class ScanResultItem(BaseModel):
    id_scrap: str
    crawled_time: datetime
    website: str
    task_id: str
    classify_website: str
    has_screenshot: bool = False


class ScanResultResponse(BaseModel):
    request_id: str
    status: str
    error: str | None = None
    results: list[ScanResultItem]


class UrlScanResponse(BaseModel):
    uuid: str
    verdicts: dict = {}
    page: dict = {}
    lists: dict = {}
    stats: dict = {}
    visible: dict = {}
    network_requests: list[dict] = []
    security_details: dict = {}
    response_headers: dict = {}


class RecentScanItem(BaseModel):
    request_id: str
    status: str
    created_at: str | None = None
    url: str = ""
    classification: str = ""
    score: int = 0
    malicious: bool = False
    malicious_score: int = 0
    size: int = 0
    requests: int = 0
    ips: int = 0
    country: str = ""
    server_location: str = ""
    domain_age_days: int = 0
    brand_name: str = ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.conn = get_connection(settings)
    run_migrations(app.state.conn)
    yield
    app.state.conn.close()


app = FastAPI(title="Web Scanner API", lifespan=lifespan)

api_router = APIRouter(prefix="/api")


@api_router.get("/health")
def health():
    return {"status": "ok"}


@api_router.get("/scans", response_model=list[RecentScanItem])
async def list_scans():
    return get_recent_scans(app.state.conn)


@api_router.post("/scan", response_model=ScanResponse)
async def scan(request: ScanRequest):
    request_id = uuid.uuid4().hex[:12]

    create_scan_request(app.state.conn, request_id)

    import subprocess

    subprocess.Popen(
        [sys.executable, "scan_worker.py", request_id, request.url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return ScanResponse(request_id=request_id, status="pending")


@api_router.get("/result/{request_id}", response_model=ScanResultResponse)
async def get_result(request_id: str):
    request = get_scan_request(app.state.conn, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    results = []
    if request["status"] == "done":
        rows = get_scan_results_by_request(app.state.conn, request_id)
        results = [ScanResultItem(**row) for row in rows]

    return ScanResultResponse(
        request_id=request["request_id"],
        status=request["status"],
        error=request.get("error"),
        results=results,
    )


@api_router.get("/screenshot/{id_scrap}")
async def screenshot(id_scrap: str):
    data = get_screenshot(app.state.conn, id_scrap)
    if data is None:
        raise HTTPException(status_code=404, detail="Screenshot not found")
    return Response(content=data, media_type="image/png")


@api_router.get("/urlscan/{request_id}", response_model=UrlScanResponse | None)
async def urlscan_result(request_id: str):
    result = get_urlscan_result_by_request(app.state.conn, request_id)
    if result is None:
        return None
    return UrlScanResponse(**result)


app.include_router(api_router)

FRONTEND_DIR = Path(__file__).parent / "frontend" / "dist"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
