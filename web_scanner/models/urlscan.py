from dataclasses import dataclass, field


@dataclass
class PageStats:
    data_length: int = 0
    encoded_data_length: int = 0
    requests: int = 0
    uniq_ips: int = 0
    uniq_countries: int = 0


@dataclass
class NetworkRequest:
    url: str
    method: str
    status: int
    request_type: str
    size: int
    mime_type: str


@dataclass
class SecurityDetails:
    protocol: str = ""
    cipher: str = ""
    issuer: str = ""
    valid_from: int = 0
    valid_to: int = 0
    san_list: list[str] = field(default_factory=list)


@dataclass
class UrlScanResult:
    uuid: str
    score: int
    categories: list[str]
    brands: list[str]
    ip: str
    country: str
    server: str
    tls_issuer: str
    report_url: str
    asn: str
    asn_name: str
    page_url: str
    page_domain: str
    apex_domain: str
    page_title: str
    http_status: str
    malicious_score: int = 0
    technologies: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    ips: list[str] = field(default_factory=list)
    stats: PageStats = field(default_factory=PageStats)
    network_requests: list[NetworkRequest] = field(default_factory=list)
    security_details: SecurityDetails = field(default_factory=SecurityDetails)
    response_headers: dict[str, str] = field(default_factory=dict)
