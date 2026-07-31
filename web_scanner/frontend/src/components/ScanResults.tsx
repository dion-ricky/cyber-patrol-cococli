import { useEffect, useState } from "react";
import {
  getResult,
  getScreenshotUrl,
  getUrlScanResult,
  type ScanResultResponse,
  type UrlScanResult,
} from "../api";

interface Props {
  requestId: string;
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

function formatDate(ts: number): string {
  if (!ts) return "N/A";
  return new Date(ts * 1000).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function getScoreClass(score: number): string {
  if (score >= 50) return "high";
  if (score >= 0) return "medium";
  return "low";
}

function getClassificationBadge(label: string): { text: string; variant: string } {
  switch (label) {
    case "GAMBLING_WEBSITE":
      return { text: "Gambling", variant: "error" };
    case "SCAM_WEBSITE":
      return { text: "Scam", variant: "error" };
    case "UNCLASSIFIED":
      return { text: "Unclassified", variant: "neutral" };
    case "ERR_CONNECTION_RESET":
      return { text: "Connection Reset", variant: "warning" };
    case "BLOCKED_BY_NETWORK_FILTER":
      return { text: "Blocked", variant: "warning" };
    case "BLOCKED_BY_GOVERNMENT":
      return { text: "Blocked by Gov", variant: "warning" };
    case "CLOUDFLARE_BLOCKED":
      return { text: "Cloudflare Blocked", variant: "warning" };
    default:
      return { text: label, variant: "neutral" };
  }
}

function getVerdicts(us: UrlScanResult) {
  const v = us.verdicts || {};
  const urlscan = (v.urlscan || {}) as Record<string, unknown>;
  const engines = (v.engines || {}) as Record<string, unknown>;
  const overall = (v.overall || {}) as Record<string, unknown>;
  return { urlscan, engines, overall };
}

function getPage(us: UrlScanResult) {
  return (us.page || {}) as Record<string, unknown>;
}

function getLists(us: UrlScanResult) {
  const lists = us.lists || {};
  return {
    domains: (lists.domains || []) as string[],
    ips: (lists.ips || []) as string[],
  };
}

function getStats(us: UrlScanResult) {
  const stats = us.stats || {};
  const domainStats = (stats.domainStats || []) as Record<string, unknown>[];
  const ipStats = (stats.ipStats || []) as Record<string, unknown>[];

  const totalRequests = domainStats.reduce((sum: number, d) => sum + ((d.count as number) || 0), 0);
  const totalData = domainStats.reduce((sum: number, d) => sum + ((d.size as number) || 0), 0);
  const totalEncoded = domainStats.reduce((sum: number, d) => sum + ((d.encodedSize as number) || 0), 0);

  return {
    requests: totalRequests,
    data_length: totalData,
    encoded_data_length: totalEncoded,
    uniq_ips: ipStats.length,
    uniq_countries: (stats.uniqCountries as number) || 0,
  };
}

function getTechnologies(us: UrlScanResult): string[] {
  const meta = (us as unknown as Record<string, unknown>).meta as Record<string, unknown> | undefined;
  if (!meta) return [];
  const processors = (meta.processors || {}) as Record<string, unknown>;
  const wappa = (processors.wappa || {}) as Record<string, unknown>;
  const data = (wappa.data || []) as Record<string, unknown>[];
  return data
    .map((t) => t.app as string)
    .filter((name): name is string => !!name);
}

function getCountryFlag(country: string): string {
  if (!country || country.length !== 2) return "";
  const codePoints = country
    .toUpperCase()
    .split("")
    .map((char) => 127397 + char.charCodeAt(0));
  return String.fromCodePoint(...codePoints);
}

function getVisible(us: UrlScanResult) {
  return (us.visible || {}) as Record<string, unknown>;
}

function formatDomainAge(days: number): string {
  if (!days || days <= 0) return "";
  const years = Math.floor(days / 365);
  const months = Math.floor((days % 365) / 30);
  if (years > 0 && months > 0) return `${years}y ${months}m`;
  if (years > 0) return `${years} year${years !== 1 ? "s" : ""}`;
  if (months > 0) return `${months} month${months !== 1 ? "s" : ""}`;
  return `${days} day${days !== 1 ? "s" : ""}`;
}

export default function ScanResults({ requestId }: Props) {
  const [data, setData] = useState<ScanResultResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lightboxSrc, setLightboxSrc] = useState<string | null>(null);
  const [urlscan, setUrlscan] = useState<UrlScanResult | null>(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [copied, setCopied] = useState(false);

  const fetchResult = async () => {
    try {
      const result = await getResult(requestId);
      setData(result);
      setError(null);

      if (result.status === "done") {
        const us = await getUrlScanResult(requestId);
        setUrlscan(us);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch result");
    }
  };

  useEffect(() => {
    fetchResult();
  }, [requestId]);

  useEffect(() => {
    if (!data || data.status === "done" || data.status === "error") return;
    const interval = setInterval(fetchResult, 3000);
    return () => clearInterval(interval);
  }, [data?.status]);

  const copyShareLink = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (error) {
    return (
      <div className="layout-page">
        <div className="status status-error">{error}</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="layout-page">
        <div className="status status-pending">Loading...</div>
      </div>
    );
  }

  const firstResult = data.results[0];
  const scanTime = firstResult
    ? new Date(firstResult.crawled_time).toLocaleString()
    : "N/A";
  const classification = firstResult?.classify_website;
  const classBadge = classification
    ? getClassificationBadge(classification)
    : null;

  const page = urlscan ? getPage(urlscan) : {};
  const verdicts = urlscan ? getVerdicts(urlscan) : null;
  const visible = urlscan ? getVisible(urlscan) : {};
  const lists = urlscan ? getLists(urlscan) : { domains: [], ips: [] };
  const stats = urlscan ? getStats(urlscan) : null;
  const technologies = urlscan ? getTechnologies(urlscan) : [];
  const secDetails = (urlscan?.security_details || {}) as Record<string, unknown>;

  const isMalicious = (verdicts?.engines.malicious as boolean) ?? false;
  const maliciousScore = (verdicts?.engines.score as number) ?? 0;
  const categories = ((verdicts?.urlscan.categories as string[]) || []);
  const brands = ((verdicts?.urlscan.brands as string[]) || []);

  const pageUrl = (page.url as string) || "";
  const apexDomain = (page.apexDomain as string) || "";
  const pageTitle = (page.title as string) || "";
  const httpStatus = (page.status as string) || "";
  const ip = (page.ip as string) || "";
  const country = (page.country as string) || "";
  const city = (page.city as string) || "";
  const server = (page.server as string) || "";
  const tlsIssuer = (page.tlsIssuer as string) || "";
  const asn = (page.asn as string) || "";
  const asnName = (page.asnname as string) || "";
  const domainAgeDays = (page.apexDomainAgeDays as number) || (page.domainAgeDays as number) || 0;
  const brandName = (visible.brandname as string) || "";

  const serverLocation = city && country ? `${city}, ${country}` : country;

  const reportUrl = `https://urlscan.io/result/${urlscan?.uuid}/`;

  return (
    <div className="layout-page">
      {/* Back Navigation */}
      <a href="/" className="back-link">
        ← Home
      </a>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero__top">
          <div className="hero__left">
            <div className="hero__title">Scan Summary</div>
            <div className="hero__url">
              {pageUrl || firstResult?.website || "Unknown"}
            </div>
            <div className="hero__meta">
              <span className="hero__meta-item">
                <span className={`badge badge--${data.status === "done" ? "success" : data.status === "error" ? "error" : "warning"}`}>
                  {data.status === "done" ? "Completed" : data.status === "error" ? "Failed" : "In Progress"}
                </span>
              </span>
              {data.error && (
                <span className="hero__meta-item text-muted text-sm">
                  {data.error}
                </span>
              )}
              <span className="hero__meta-sep">|</span>
              <span className="hero__meta-item text-muted text-sm">
                {scanTime}
              </span>
              <span className="hero__meta-sep">|</span>
              <span className="hero__meta-item text-muted text-sm">
                ID: {requestId}
              </span>
            </div>
          </div>
          <div className="hero__actions">
            <button className="btn-action" onClick={copyShareLink}>
              {copied ? "Copied!" : "Copy Link"}
            </button>
            {urlscan && (
              <a
                className="btn-action"
                href={reportUrl}
                target="_blank"
                rel="noopener noreferrer"
              >
                urlscan.io
              </a>
            )}
          </div>
        </div>

        {/* Score Panel + Classification */}
        <div className="hero__bottom">
          {urlscan && verdicts && (
            <div className="score-panel">
              <div className="score-panel__main">
                <div className={`badge badge--${isMalicious ? "error" : "success"}`} style={{ fontSize: "1rem", padding: "0.375rem 0.875rem" }}>
                  {isMalicious ? "Malicious" : "Safe"}
                </div>
                <div className="score-panel__label">Verdict</div>
              </div>
              <div className="score-panel__divider" />
              <div className="score-panel__main">
                <div className={`score-panel__value score-panel__value--${getScoreClass(maliciousScore)}`}>
                  {maliciousScore}
                </div>
                <div className="score-panel__label">Score</div>
              </div>
              {classBadge && (
                <>
                  <div className="score-panel__divider" />
                  <div className="score-panel__main">
                    <div className={`badge badge--${classBadge.variant}`} style={{ fontSize: "1rem", padding: "0.375rem 0.875rem" }}>
                      {classBadge.text}
                    </div>
                    <div className="score-panel__label">Classification</div>
                  </div>
                </>
              )}
              <div className="score-panel__divider" />
              <div className="score-panel__details">
                {country && (
                  <div className="score-panel__detail">
                    <span className="score-panel__detail-label">Country</span>
                    <span className="score-panel__detail-value">
                      {getCountryFlag(country)} {country}
                    </span>
                  </div>
                )}
                {server && (
                  <div className="score-panel__detail">
                    <span className="score-panel__detail-label">Server</span>
                    <span className="score-panel__detail-value">{server}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {!urlscan && classBadge && (
            <div className={`badge badge--${classBadge.variant}`} style={{ fontSize: "1rem", padding: "0.375rem 0.875rem" }}>
              {classBadge.text}
            </div>
          )}
        </div>
      </section>

      {/* Metrics Bar */}
      {urlscan && stats && (
        <section className="metrics">
          <div className="metric">
            <div className="metric__value">{stats.requests}</div>
            <div className="metric__label">Requests</div>
          </div>
          <div className="metric">
            <div className="metric__value">{formatBytes(stats.encoded_data_length)}</div>
            <div className="metric__label">Transfer</div>
          </div>
          <div className="metric">
            <div className="metric__value">{formatBytes(stats.data_length)}</div>
            <div className="metric__label">Data Size</div>
          </div>
          <div className="metric">
            <div className="metric__value">{stats.uniq_countries}</div>
            <div className="metric__label">Countries</div>
          </div>
          <div className="metric">
            <div className="metric__value">{lists.domains.length}</div>
            <div className="metric__label">Domains</div>
          </div>
          <div className="metric">
            <div className="metric__value">{stats.uniq_ips}</div>
            <div className="metric__label">IPs</div>
          </div>
        </section>
      )}

      {/* Tabs */}
      {(urlscan || firstResult?.has_screenshot) && (
        <section className="tabs">
          <div className="tabs__nav">
            {urlscan && (
              <>
                <button
                  className={`tabs__tab ${activeTab === "overview" ? "tabs__tab--active" : ""}`}
                  onClick={() => setActiveTab("overview")}
                >
                  Overview
                </button>
                <button
                  className={`tabs__tab ${activeTab === "technologies" ? "tabs__tab--active" : ""}`}
                  onClick={() => setActiveTab("technologies")}
                >
                  Technologies
                </button>
                <button
                  className={`tabs__tab ${activeTab === "domains" ? "tabs__tab--active" : ""}`}
                  onClick={() => setActiveTab("domains")}
                >
                  Domains & IPs
                </button>
                <button
                  className={`tabs__tab ${activeTab === "requests" ? "tabs__tab--active" : ""}`}
                  onClick={() => setActiveTab("requests")}
                >
                  Requests
                </button>
              </>
            )}
            {firstResult?.has_screenshot && (
              <button
                className={`tabs__tab ${activeTab === "screenshot" ? "tabs__tab--active" : ""}`}
                onClick={() => setActiveTab("screenshot")}
              >
                Screenshot
              </button>
            )}
          </div>

          <div className="tabs__content">
            {/* Overview Tab */}
            {activeTab === "overview" && urlscan && (
              <div className="info-grid">
                {/* Domain Information */}
                <div className="info-group">
                  <div className="info-group__header">Domain Information</div>
                  {brandName && (
                    <div className="info-row">
                      <span className="info-row__label">Brand</span>
                      <span className="info-row__value">{brandName}</span>
                    </div>
                  )}
                  {apexDomain && (
                    <div className="info-row">
                      <span className="info-row__label">Apex Domain</span>
                      <span className="info-row__value">{apexDomain}</span>
                    </div>
                  )}
                  {domainAgeDays > 0 && (
                    <div className="info-row">
                      <span className="info-row__label">Domain Age</span>
                      <span className="info-row__value">{formatDomainAge(domainAgeDays)}</span>
                    </div>
                  )}
                  {pageUrl && (
                    <div className="info-row">
                      <span className="info-row__label">Final URL</span>
                      <span className="info-row__value">{pageUrl}</span>
                    </div>
                  )}
                  {httpStatus && (
                    <div className="info-row">
                      <span className="info-row__label">HTTP Status</span>
                      <span className="info-row__value">{httpStatus}</span>
                    </div>
                  )}
                  {pageTitle && (
                    <div className="info-row">
                      <span className="info-row__label">Page Title</span>
                      <span className="info-row__value">{pageTitle}</span>
                    </div>
                  )}
                </div>

                {/* Network Information */}
                <div className="info-group">
                  <div className="info-group__header">Network Information</div>
                  {ip && (
                    <div className="info-row">
                      <span className="info-row__label">DNS A Record</span>
                      <span className="info-row__value">
                        {ip}
                        {asn && (
                          <span className="info-row__sub">
                            {asn}{asnName ? ` - ${asnName}` : ""}
                          </span>
                        )}
                      </span>
                    </div>
                  )}
                  {serverLocation && (
                    <div className="info-row">
                      <span className="info-row__label">Server Location</span>
                      <span className="info-row__value">
                        {getCountryFlag(country)} {serverLocation}
                      </span>
                    </div>
                  )}
                  {server && (
                    <div className="info-row">
                      <span className="info-row__label">Server</span>
                      <span className="info-row__value">{server}</span>
                    </div>
                  )}
                  {tlsIssuer && (
                    <div className="info-row">
                      <span className="info-row__label">TLS Issuer</span>
                      <span className="info-row__value">{tlsIssuer}</span>
                    </div>
                  )}
                  {categories.length > 0 && (
                    <div className="info-row">
                      <span className="info-row__label">Categories</span>
                      <span className="info-row__value">{categories.join(", ")}</span>
                    </div>
                  )}
                  {brands.length > 0 && (
                    <div className="info-row">
                      <span className="info-row__label">Brands</span>
                      <span className="info-row__value">{brands.join(", ")}</span>
                    </div>
                  )}
                </div>

                {/* Security Analysis */}
                {(secDetails.protocol as string) && (
                  <div className="info-group">
                    <div className="info-group__header">Security Analysis</div>
                    <div className="info-row">
                      <span className="info-row__label">SSL/TLS Version</span>
                      <span className="info-row__value">{secDetails.protocol as string}</span>
                    </div>
                    {(secDetails.cipher as string) && (
                      <div className="info-row">
                        <span className="info-row__label">Cipher</span>
                        <span className="info-row__value">{secDetails.cipher as string}</span>
                      </div>
                    )}
                    {(secDetails.issuer as string) && (
                      <div className="info-row">
                        <span className="info-row__label">Certificate Issuer</span>
                        <span className="info-row__value">{secDetails.issuer as string}</span>
                      </div>
                    )}
                    {(secDetails.valid_from as number) > 0 && (
                      <div className="info-row">
                        <span className="info-row__label">Valid From</span>
                        <span className="info-row__value">{formatDate(secDetails.valid_from as number)}</span>
                      </div>
                    )}
                    {(secDetails.valid_to as number) > 0 && (
                      <div className="info-row">
                        <span className="info-row__label">Valid To</span>
                        <span className="info-row__value">{formatDate(secDetails.valid_to as number)}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Response Headers */}
                {Object.keys(urlscan.response_headers).length > 0 && (
                  <div className="info-group" style={{ gridColumn: "1 / -1" }}>
                    <div className="info-group__header">Response Headers</div>
                    {Object.entries(urlscan.response_headers).map(([key, value]) => (
                      <div key={key} className="info-row">
                        <span className="info-row__label">{key}</span>
                        <span className="info-row__value">{value}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Technologies Tab */}
            {activeTab === "technologies" && urlscan && (
              <div>
                {technologies.length > 0 ? (
                  <div className="tech-grid">
                    {technologies.map((tech) => (
                      <div key={tech} className="tech-item">{tech}</div>
                    ))}
                  </div>
                ) : (
                  <div className="empty">No technologies detected.</div>
                )}
              </div>
            )}

            {/* Domains & IPs Tab */}
            {activeTab === "domains" && urlscan && (
              <div className="info-grid">
                <div className="section">
                  <div className="section__header">
                    Contacted Domains ({lists.domains.length})
                  </div>
                  <div className="section__content">
                    {lists.domains.length > 0 ? (
                      <div className="list">
                        {lists.domains.slice(0, 50).map((domain) => (
                          <div key={domain} className="list-item">{domain}</div>
                        ))}
                        {lists.domains.length > 50 && (
                          <div className="list-item list-item--muted">
                            ... and {lists.domains.length - 50} more
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="empty">No domains contacted.</div>
                    )}
                  </div>
                </div>
                <div className="section">
                  <div className="section__header">
                    IP Addresses ({lists.ips.length})
                  </div>
                  <div className="section__content">
                    {lists.ips.length > 0 ? (
                      <div className="list">
                        {lists.ips.slice(0, 50).map((ip) => (
                          <div key={ip} className="list-item">{ip}</div>
                        ))}
                        {lists.ips.length > 50 && (
                          <div className="list-item list-item--muted">
                            ... and {lists.ips.length - 50} more
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="empty">No IPs recorded.</div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Requests Tab */}
            {activeTab === "requests" && urlscan && (
              <div className="section">
                <div className="section__header">
                  Network Requests ({urlscan.network_requests.length})
                </div>
                {urlscan.network_requests.length > 0 ? (
                  <div className="table-wrapper">
                    <table className="table">
                      <thead>
                        <tr>
                          <th>URL</th>
                          <th>Method</th>
                          <th>Status</th>
                          <th>Type</th>
                          <th>Size</th>
                        </tr>
                      </thead>
                      <tbody>
                        {urlscan.network_requests.map((req, i) => (
                          <tr key={i}>
                            <td className="table__url" title={req.url as string}>{req.url as string}</td>
                            <td className="table__method">{req.method as string}</td>
                            <td className="table__status">{req.status as number}</td>
                            <td>{req.type as string}</td>
                            <td>{formatBytes((req.size as number) || 0)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="section__content">
                    <div className="empty">Network request details not available.</div>
                  </div>
                )}
              </div>
            )}

            {/* Screenshot Tab */}
            {activeTab === "screenshot" && firstResult?.has_screenshot && (
              <div className="screenshot">
                <img
                  src={getScreenshotUrl(firstResult.id_scrap)}
                  alt={`Screenshot of ${firstResult.website}`}
                  className="screenshot__img"
                  onClick={() => setLightboxSrc(getScreenshotUrl(firstResult.id_scrap))}
                />
                <button onClick={() => setLightboxSrc(getScreenshotUrl(firstResult.id_scrap))}>
                  View Fullscreen
                </button>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Empty State */}
      {data.status === "done" && data.results.length === 0 && !urlscan && (
        <div className="empty">No results found.</div>
      )}

      {/* Lightbox */}
      {lightboxSrc && (
        <div className="lightbox-overlay" onClick={() => setLightboxSrc(null)}>
          <img
            src={lightboxSrc}
            alt="Full size screenshot"
            className="lightbox-img"
          />
        </div>
      )}
    </div>
  );
}
