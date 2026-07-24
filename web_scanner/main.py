from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.settings import get_settings
from db.connection import get_connection
from db.repository import ensure_schema, insert_scan_result
from models.scan import ScanRequest, ScanResponse, ScanResultItem
from scanner.browser import BrowserAgent
from scanner.website import WebsiteScanner


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.conn = get_connection(settings)
    ensure_schema(app.state.conn)
    app.state.browser = BrowserAgent(settings)
    app.state.scanner = WebsiteScanner(app.state.browser, settings)
    yield
    app.state.conn.close()


app = FastAPI(title="Web Scanner API", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scan", response_model=ScanResponse)
async def scan(request: ScanRequest):
    scanner: WebsiteScanner = app.state.scanner
    results = []
    for url in request.urls:
        result = await scanner.scan(url)
        insert_scan_result(app.state.conn, result)
        item = ScanResultItem(**result.to_dict())
        results.append(item)
    return ScanResponse(results=results)
