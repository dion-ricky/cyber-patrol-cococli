import json
import logging

import psycopg

from models.scan import ScanResult
from scanner.urlscan import UrlScanData
from utils.url import sanitize_json

logger = logging.getLogger(__name__)


def create_scan_request(conn: psycopg.Connection, request_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO scan_requests (request_id, status) VALUES (%s, 'pending')",
            (request_id,),
        )
    conn.commit()


def update_scan_status(
    conn: psycopg.Connection,
    request_id: str,
    status: str,
    error: str | None = None,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE scan_requests
            SET status = %s, error = %s, updated_at = NOW()
            WHERE request_id = %s
            """,
            (status, error, request_id),
        )
    conn.commit()


def insert_scan_result(
    conn: psycopg.Connection, result: ScanResult, request_id: str
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO scan_results
                (id_scrap, request_id, crawled_time, website, task_id,
                 classify_website, screenshot)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_scrap) DO UPDATE SET
                request_id = EXCLUDED.request_id,
                crawled_time = EXCLUDED.crawled_time,
                website = EXCLUDED.website,
                task_id = EXCLUDED.task_id,
                classify_website = EXCLUDED.classify_website,
                screenshot = EXCLUDED.screenshot
            """,
            (
                result.scrap_id,
                request_id,
                result.crawled_time,
                result.website,
                result.task_id,
                result.classification,
                result.screenshot,
            ),
        )
    conn.commit()


def get_scan_request(conn: psycopg.Connection, request_id: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT request_id, status, error, created_at, updated_at
            FROM scan_requests
            WHERE request_id = %s
            """,
            (request_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "request_id": row[0],
            "status": row[1],
            "error": row[2],
            "created_at": row[3],
            "updated_at": row[4],
        }


def get_scan_results_by_request(
    conn: psycopg.Connection, request_id: str
) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_scrap, crawled_time, website, task_id, classify_website,
                   (screenshot IS NOT NULL) as has_screenshot
            FROM scan_results
            WHERE request_id = %s
            """,
            (request_id,),
        )
        rows = cur.fetchall()
        return [
            {
                "id_scrap": row[0],
                "crawled_time": row[1],
                "website": row[2],
                "task_id": row[3],
                "classify_website": row[4],
                "has_screenshot": row[5],
            }
            for row in rows
        ]


def get_screenshot(conn: psycopg.Connection, id_scrap: str) -> bytes | None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT screenshot FROM scan_results WHERE id_scrap = %s",
            (id_scrap,),
        )
        row = cur.fetchone()
        if not row or row[0] is None:
            return None
        return row[0]


def insert_urlscan_result(
    conn: psycopg.Connection, data: UrlScanData, request_id: str
) -> None:
    network_requests_json = json.dumps(
        [
            {
                "url": r.url,
                "method": r.method,
                "status": r.status,
                "type": r.request_type,
                "size": r.size,
                "mime_type": r.mime_type,
            }
            for r in data.result.network_requests
        ]
    )

    verdicts = sanitize_json(data.raw_verdicts)
    page = sanitize_json(data.raw_page)
    lists = sanitize_json(data.raw_lists)
    stats = sanitize_json(data.raw_stats)
    visible = sanitize_json(data.raw_visible)
    security = sanitize_json(data.raw_security_details)
    response_headers = sanitize_json(data.result.response_headers)
    network_requests = sanitize_json(json.loads(network_requests_json))

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO urlscan_results
                (request_id, uuid, verdicts, page, lists, stats, visible,
                 network_requests, security_details, response_headers)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (uuid) DO UPDATE SET
                request_id = EXCLUDED.request_id,
                verdicts = EXCLUDED.verdicts,
                page = EXCLUDED.page,
                lists = EXCLUDED.lists,
                stats = EXCLUDED.stats,
                visible = EXCLUDED.visible,
                network_requests = EXCLUDED.network_requests,
                security_details = EXCLUDED.security_details,
                response_headers = EXCLUDED.response_headers
            """,
            (
                request_id,
                data.result.uuid,
                json.dumps(verdicts),
                json.dumps(page),
                json.dumps(lists),
                json.dumps(stats),
                json.dumps(visible),
                json.dumps(network_requests),
                json.dumps(security),
                json.dumps(response_headers),
            ),
        )
    conn.commit()


def get_urlscan_result_by_request(
    conn: psycopg.Connection, request_id: str
) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT uuid, verdicts, page, lists, stats, visible,
                   network_requests, security_details, response_headers
            FROM urlscan_results
            WHERE request_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (request_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {
            "uuid": row[0],
            "verdicts": row[1]
            if isinstance(row[1], dict)
            else json.loads(row[1] or "{}"),
            "page": row[2] if isinstance(row[2], dict) else json.loads(row[2] or "{}"),
            "lists": row[3] if isinstance(row[3], dict) else json.loads(row[3] or "{}"),
            "stats": row[4] if isinstance(row[4], dict) else json.loads(row[4] or "{}"),
            "visible": row[5]
            if isinstance(row[5], dict)
            else json.loads(row[5] or "{}"),
            "network_requests": row[6]
            if isinstance(row[6], list)
            else json.loads(row[6] or "[]"),
            "security_details": row[7]
            if isinstance(row[7], dict)
            else json.loads(row[7] or "{}"),
            "response_headers": row[8]
            if isinstance(row[8], dict)
            else json.loads(row[8] or "{}"),
        }


def get_recent_scans(conn: psycopg.Connection, limit: int = 50) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                sr.request_id,
                sr.status,
                sr.created_at,
                res.website,
                res.classify_website,
                ur.verdicts,
                ur.stats,
                ur.page,
                ur.lists,
                ur.visible
            FROM scan_requests sr
            LEFT JOIN scan_results res ON res.request_id = sr.request_id
            LEFT JOIN urlscan_results ur ON ur.request_id = sr.request_id
            ORDER BY sr.created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
        results = []
        for row in rows:
            verdicts = (
                row[5] if isinstance(row[5], dict) else json.loads(row[5] or "{}")
            )
            stats = row[6] if isinstance(row[6], dict) else json.loads(row[6] or "{}")
            page = row[7] if isinstance(row[7], dict) else json.loads(row[7] or "{}")
            _lists = row[8] if isinstance(row[8], dict) else json.loads(row[8] or "{}")
            visible = row[9] if isinstance(row[9], dict) else json.loads(row[9] or "{}")

            urlscan_verdicts = verdicts.get("urlscan", {})
            engines_verdicts = verdicts.get("engines", {})

            domain_stats = stats.get("domainStats", [])
            total_requests = sum(d.get("count", 0) for d in domain_stats)
            total_data = sum(d.get("size", 0) for d in domain_stats)
            ip_stats = stats.get("ipStats", [])
            uniq_ips = len(ip_stats)

            city = page.get("city", "")
            country = page.get("country", "")
            server_location = ""
            if city and country:
                server_location = f"{city}, {country}"
            elif country:
                server_location = country

            domain_age_days = (
                page.get("apexDomainAgeDays") or page.get("domainAgeDays") or 0
            )

            results.append(
                {
                    "request_id": row[0],
                    "status": row[1],
                    "created_at": row[2].isoformat() if row[2] else None,
                    "url": page.get("url") or row[3] or "",
                    "classification": row[4] or "",
                    "score": urlscan_verdicts.get("score", 0),
                    "malicious": engines_verdicts.get("malicious", False),
                    "malicious_score": engines_verdicts.get("score", 0),
                    "size": total_data,
                    "requests": total_requests,
                    "ips": uniq_ips,
                    "country": country,
                    "server_location": server_location,
                    "domain_age_days": domain_age_days,
                    "brand_name": visible.get("brandname", ""),
                }
            )
        return results
