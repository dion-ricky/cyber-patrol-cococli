import asyncio
import logging
from dataclasses import dataclass

import httpx

from models.urlscan import NetworkRequest, PageStats, SecurityDetails, UrlScanResult

logger = logging.getLogger(__name__)

SUBMIT_URL = "https://urlscan.io/api/v1/scan/"
RESULT_URL = "https://urlscan.io/api/v1/result/{uuid}/"
INITIAL_WAIT = 10
POLL_INTERVAL = 5
MAX_POLLS = 12


@dataclass
class UrlScanData:
    result: UrlScanResult
    raw_verdicts: dict
    raw_page: dict
    raw_lists: dict
    raw_stats: dict
    raw_security_details: dict
    raw_visible: dict


class UrlScanClient:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def scan(self, url: str) -> UrlScanData:
        uuid = await self._submit(url)
        await asyncio.sleep(INITIAL_WAIT)
        data = await self._poll(uuid)
        return self._extract(uuid, data)

    async def _submit(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                SUBMIT_URL,
                headers={
                    "API-Key": self._api_key,
                    "Content-Type": "application/json",
                },
                json={"url": url, "visibility": "public"},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["uuid"]

    async def _poll(self, uuid: str) -> dict:
        async with httpx.AsyncClient() as client:
            for _ in range(MAX_POLLS):
                resp = await client.get(
                    RESULT_URL.format(uuid=uuid),
                    headers={"API-Key": self._api_key},
                    timeout=30,
                )
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code == 404:
                    await asyncio.sleep(POLL_INTERVAL)
                    continue
                resp.raise_for_status()
            raise TimeoutError(f"urlscan result not ready after {MAX_POLLS} polls")

    @staticmethod
    def _extract(uuid: str, data: dict) -> UrlScanData:
        verdicts = data.get("verdicts", {})
        page = data.get("page", {})
        lists = data.get("lists", {})
        stats_raw = data.get("stats", {})
        meta = data.get("meta", {})
        visible = data.get("visible", {})
        raw_requests = data.get("data", {}).get("requests", [])

        urlscan_verdicts = verdicts.get("urlscan", {})
        verdicts_engines = verdicts.get("engines", {})
        brands_raw = urlscan_verdicts.get("brands", [])

        brands = []
        for b in brands_raw:
            if isinstance(b, dict):
                brands.append(b.get("name", ""))
            else:
                brands.append(str(b))

        malicious_score = verdicts_engines.get("score", 0)

        technologies = []
        processors = meta.get("processors", {})
        wappa = processors.get("wappa", {})
        for tech in wappa.get("data", []):
            name = tech.get("app", "")
            if name:
                technologies.append(name)

        domain_stats = stats_raw.get("domainStats", [])
        total_requests = sum(d.get("count", 0) for d in domain_stats)
        total_data = sum(d.get("size", 0) for d in domain_stats)
        total_encoded = sum(d.get("encodedSize", 0) for d in domain_stats)
        ip_stats = stats_raw.get("ipStats", [])
        uniq_ips = len(ip_stats)
        uniq_countries = stats_raw.get("uniqCountries", 0)

        network_requests = []
        for req in raw_requests[:100]:
            req_inner = req.get("request", {}).get("request", {})
            resp_inner = req.get("response", {}).get("response", {})
            req_type = req.get("request", {}).get("type", "")
            url = req_inner.get("url", "") or resp_inner.get("url", "")
            if not url:
                continue
            network_requests.append(
                NetworkRequest(
                    url=url,
                    method=req_inner.get("method", "GET"),
                    status=resp_inner.get("status", 0),
                    request_type=req_type,
                    size=resp_inner.get("encodedDataLength", 0),
                    mime_type=resp_inner.get("mimeType", ""),
                )
            )

        security_details = SecurityDetails()
        response_headers: dict[str, str] = {}
        raw_security: dict = {}
        if raw_requests:
            main_resp = raw_requests[0].get("response", {}).get("response", {})
            sec = main_resp.get("securityDetails", {})
            if sec:
                raw_security = sec
                security_details = SecurityDetails(
                    protocol=sec.get("protocol", ""),
                    cipher=sec.get("cipher", ""),
                    issuer=sec.get("issuer", ""),
                    valid_from=sec.get("validFrom", 0),
                    valid_to=sec.get("validTo", 0),
                    san_list=sec.get("sanList", []),
                )
            response_headers = main_resp.get("headers", {})

        result = UrlScanResult(
            uuid=uuid,
            score=urlscan_verdicts.get("score", 0),
            categories=urlscan_verdicts.get("categories", []),
            brands=[b for b in brands if b],
            ip=page.get("ip", ""),
            country=page.get("country", ""),
            server=page.get("server", ""),
            tls_issuer=page.get("tlsIssuer", ""),
            report_url=f"https://urlscan.io/result/{uuid}/",
            asn=page.get("asn", ""),
            asn_name=page.get("asnname", ""),
            malicious_score=malicious_score,
            page_url=page.get("url", ""),
            page_domain=page.get("domain", ""),
            apex_domain=page.get("apexDomain", ""),
            page_title=page.get("title", ""),
            http_status=str(page.get("status", "")),
            technologies=technologies,
            domains=lists.get("domains", []),
            ips=[str(ip) for ip in lists.get("ips", [])],
            stats=PageStats(
                data_length=total_data,
                encoded_data_length=total_encoded,
                requests=total_requests,
                uniq_ips=uniq_ips,
                uniq_countries=uniq_countries,
            ),
            network_requests=network_requests,
            security_details=security_details,
            response_headers=response_headers,
        )

        return UrlScanData(
            result=result,
            raw_verdicts=verdicts,
            raw_page=page,
            raw_lists=lists,
            raw_stats=stats_raw,
            raw_security_details=raw_security,
            raw_visible=visible,
        )
