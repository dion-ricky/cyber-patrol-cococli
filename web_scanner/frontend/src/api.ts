export interface ScanResponse {
  request_id: string;
  status: string;
}

export interface ScanResultItem {
  id_scrap: string;
  crawled_time: string;
  website: string;
  task_id: string;
  classify_website: string;
  has_screenshot: boolean;
}

export interface ScanResultResponse {
  request_id: string;
  status: string;
  error: string | null;
  results: ScanResultItem[];
}

export interface UrlScanResult {
  uuid: string;
  verdicts: Record<string, unknown>;
  page: Record<string, unknown>;
  lists: Record<string, unknown>;
  stats: Record<string, unknown>;
  visible: Record<string, unknown>;
  network_requests: Record<string, unknown>[];
  security_details: Record<string, unknown>;
  response_headers: Record<string, string>;
}

export interface RecentScanItem {
  request_id: string;
  status: string;
  created_at: string | null;
  url: string;
  classification: string;
  score: number;
  malicious: boolean;
  malicious_score: number;
  size: number;
  requests: number;
  ips: number;
  country: string;
  server_location: string;
  domain_age_days: number;
  brand_name: string;
}

export async function startScan(url: string): Promise<ScanResponse> {
  const res = await fetch("/api/scan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) throw new Error(`Scan failed: ${res.statusText}`);
  return res.json();
}

export async function getResult(requestId: string): Promise<ScanResultResponse> {
  const res = await fetch(`/api/result/${requestId}`);
  if (!res.ok) throw new Error(`Result fetch failed: ${res.statusText}`);
  return res.json();
}

export async function getUrlScanResult(
  requestId: string,
): Promise<UrlScanResult | null> {
  const res = await fetch(`/api/urlscan/${requestId}`);
  if (!res.ok) return null;
  const data = await res.json();
  return data ?? null;
}

export async function getRecentScans(): Promise<RecentScanItem[]> {
  const res = await fetch("/api/scans");
  if (!res.ok) throw new Error(`Failed to fetch scans: ${res.statusText}`);
  return res.json();
}

export function getScreenshotUrl(idScrap: string): string {
  return `/api/screenshot/${idScrap}`;
}
