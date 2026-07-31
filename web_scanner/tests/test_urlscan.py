import json
from pathlib import Path

from scanner.urlscan import UrlScanClient

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_extract_linkr():
    data = json.loads((FIXTURE_DIR / "urlscan_019fb859.json").read_text())
    scan_data = UrlScanClient._extract("019fb859-8a85-74d8-9b8b-0cde9bc4fa56", data)
    result = scan_data.result

    assert result.uuid == "019fb859-8a85-74d8-9b8b-0cde9bc4fa56"
    assert result.score == 0
    assert result.categories == []
    assert result.ip == "34.149.124.255"
    assert result.country == "US"
    assert result.server == "UploadServer"
    assert result.tls_issuer == "WR3"
    assert result.asn == "AS396982"
    assert "GOOGLE-CLOUD-PLATFORM" in result.asn_name
    assert result.malicious_score == 41
    assert result.page_url == "https://linkr.it/45Mu1o"
    assert result.page_domain == "linkr.it"
    assert result.apex_domain == "linkr.it"
    assert "Linkr" in result.page_title
    assert result.http_status == "404"


def test_extract_raw_data():
    data = json.loads((FIXTURE_DIR / "urlscan_019fb859.json").read_text())
    scan_data = UrlScanClient._extract("019fb859-8a85-74d8-9b8b-0cde9bc4fa56", data)

    assert "urlscan" in scan_data.raw_verdicts
    assert "engines" in scan_data.raw_verdicts
    assert scan_data.raw_verdicts["engines"]["score"] == 41
    assert scan_data.raw_verdicts["engines"]["malicious"] is True

    assert scan_data.raw_page["ip"] == "34.149.124.255"
    assert scan_data.raw_page["country"] == "US"
    assert scan_data.raw_page["server"] == "UploadServer"

    assert "domains" in scan_data.raw_lists
    assert "ips" in scan_data.raw_lists

    assert "domainStats" in scan_data.raw_stats
    assert "ipStats" in scan_data.raw_stats


def test_extract_technologies():
    data = json.loads((FIXTURE_DIR / "urlscan_019fb859.json").read_text())
    scan_data = UrlScanClient._extract("019fb859-8a85-74d8-9b8b-0cde9bc4fa56", data)
    result = scan_data.result

    assert "Bootstrap" in result.technologies
    assert "Stripe" in result.technologies
    assert "Google Tag Manager" in result.technologies
    assert "Tawk.to" in result.technologies
    assert len(result.technologies) == 10


def test_extract_stats():
    data = json.loads((FIXTURE_DIR / "urlscan_019fb859.json").read_text())
    scan_data = UrlScanClient._extract("019fb859-8a85-74d8-9b8b-0cde9bc4fa56", data)
    result = scan_data.result

    assert result.stats.requests == 104
    assert result.stats.uniq_ips == 28
    assert result.stats.uniq_countries == 5
    assert result.stats.data_length > 0
    assert result.stats.encoded_data_length > 0


def test_extract_domains_and_ips():
    data = json.loads((FIXTURE_DIR / "urlscan_019fb859.json").read_text())
    scan_data = UrlScanClient._extract("019fb859-8a85-74d8-9b8b-0cde9bc4fa56", data)
    result = scan_data.result

    assert "linkr.it" in result.domains
    assert "embed.tawk.to" in result.domains
    assert len(result.domains) == 30
    assert "34.149.124.255" in result.ips
    assert len(result.ips) == 28


def test_extract_empty_verdicts():
    data = {
        "verdicts": {"urlscan": {}},
        "page": {},
        "lists": {},
        "stats": {},
        "meta": {},
    }
    scan_data = UrlScanClient._extract("test-uuid", data)
    result = scan_data.result

    assert result.uuid == "test-uuid"
    assert result.score == 0
    assert result.categories == []
    assert result.brands == []
    assert result.malicious_score == 0
    assert result.technologies == []
    assert result.domains == []
    assert result.ips == []
    assert result.stats.requests == 0
