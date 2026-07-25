import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config.settings import get_settings
from db.connection import get_connection
from db.migrations.runner import run_migrations
from db.repository import (
    create_scan_request,
    get_scan_request,
    get_scan_results_by_request,
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


class ScanResultResponse(BaseModel):
    request_id: str
    status: str
    error: str | None = None
    results: list[ScanResultItem]


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.conn = get_connection(settings)
    run_migrations(app.state.conn)
    yield
    app.state.conn.close()


app = FastAPI(title="Web Scanner API", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scan", response_model=ScanResponse)
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


@app.get("/result/{request_id}", response_model=ScanResultResponse)
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
