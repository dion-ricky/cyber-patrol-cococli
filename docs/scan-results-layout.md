# Scan Results Layout - Implementation Plan

## Goal
Recreate the scan results page layout integrating with existing backend data. Remove unused sections (visualization, DOM structure, Performance Metrics, Threat Summary). Extract missing data from urlscan.io raw response.

## Sections to Remove
- Chart/visualization area in Overview tab
- DOM Structure tree view
- Performance Metrics section
- Threat Summary sidebar panel

## Data Gap Analysis

### Available (no changes needed)
| Section | Source |
|---|---|
| Hero: request ID, status, timestamp | `ScanResultResponse` |
| Hero: score, malicious score, categories, brands, country, server | `UrlScanResult` |
| Info Grid: domain, network, stats | `UrlScanResult` |
| Tab: Technologies | `UrlScanResult.technologies` |
| Tab: Domains & IPs | `UrlScanResult.domains`, `.ips` |
| Tab: Screenshot | `getScreenshotUrl(id_scrap)` |
| Detection Results table | `ScanResultResponse.results[]` |

### Missing - Needs Backend Extraction
| Feature | Raw Source in urlscan JSON |
|---|---|
| **Requests tab** (URL, method, status, type, size) | `data.requests[].request.request.url/method/type`, `data.requests[].response.response.status/encodedDataLength/mimeType` |
| **Security Analysis** (TLS version, cipher, cert validity) | `data.requests[0].response.response.securityDetails.protocol/cipher/validFrom/validTo/issuer/sanList` |
| **HTTP Headers** (response headers from main doc) | `data.requests[0].response.response.headers` |

## Implementation Steps

### Phase 1: Backend - Extract New Data from urlscan

#### 1.1 Update `models/urlscan.py`
Add new dataclasses:
- `NetworkRequest`: url, method, status, type, size, mime_type
- `SecurityDetails`: protocol, cipher, issuer, valid_from, valid_to, san_list
- Add fields to `UrlScanResult`: `network_requests: list[NetworkRequest]`, `security_details: SecurityDetails`, `response_headers: dict[str, str]`

#### 1.2 Update `scanner/urlscan.py` `_extract()`
Extract from raw `data`:
- `data.requests[]` -> list of `NetworkRequest` (first 100 max)
- First request's `securityDetails` -> `SecurityDetails`
- First request's response `headers` -> `response_headers` dict

#### 1.3 Add DB migration `20260731_urlscan_extended.sql`
Add columns to `urlscan_results`:
- `network_requests` JSONB DEFAULT '[]'
- `security_protocol` TEXT
- `security_cipher` TEXT
- `security_issuer` TEXT
- `security_valid_from` BIGINT
- `security_valid_to` BIGINT
- `security_san_list` TEXT[]
- `response_headers` JSONB DEFAULT '{}'

#### 1.4 Update `db/repository.py`
- `insert_urlscan_result()`: insert new fields
- `get_urlscan_result_by_request()`: select new fields

#### 1.5 Update `main.py`
- Add new Pydantic models: `NetworkRequestResponse`, `SecurityDetailsResponse`
- Update `UrlScanResponse` with new fields
- Update `/api/urlscan/{request_id}` endpoint

### Phase 2: Frontend - Wire Up Real Data

#### 2.1 Update `api.ts`
- Add `NetworkRequest`, `SecurityDetails` TypeScript interfaces
- Update `UrlScanResult` with new fields

#### 2.2 Rewrite `ScanResults.tsx`
- Wire to existing API calls (fetchResult, getUrlScanResult, getScreenshotUrl)
- Map real data to all layout sections
- Remove 4 unwanted sections
- Show empty states where data unavailable

#### 2.3 Clean up `index.css`
- Remove unused CSS classes (visualization, DOM tree, performance, threat)
- Update `.container` max-width for wider layout

## Files to Modify
1. `web_scanner/models/urlscan.py` - add dataclasses
2. `web_scanner/scanner/urlscan.py` - update `_extract()`
3. `web_scanner/db/migrations/20260731_urlscan_extended.sql` - new migration
4. `web_scanner/db/repository.py` - update insert/get queries
5. `web_scanner/main.py` - update Pydantic models and endpoint
6. `web_scanner/frontend/src/api.ts` - update TypeScript types
7. `web_scanner/frontend/src/components/ScanResults.tsx` - rewrite component
8. `web_scanner/frontend/src/index.css` - clean up unused CSS
