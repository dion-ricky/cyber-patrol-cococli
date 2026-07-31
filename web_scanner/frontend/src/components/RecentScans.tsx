import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getRecentScans, type RecentScanItem } from "../api";

function formatBytes(bytes: number): string {
  if (bytes === 0) return "-";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

function formatAge(dateStr: string | null): string {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffDay > 0) return `${diffDay}d ago`;
  if (diffHour > 0) return `${diffHour}h ago`;
  if (diffMin > 0) return `${diffMin}m ago`;
  return "just now";
}

function getClassIndicator(classification: string): { label: string; variant: string } {
  switch (classification) {
    case "GAMBLING_WEBSITE":
      return { label: "Gambling", variant: "error" };
    case "SCAM_WEBSITE":
      return { label: "Scam", variant: "error" };
    case "UNCLASSIFIED":
      return { label: "Unclassified", variant: "neutral" };
    case "ERR_CONNECTION_RESET":
      return { label: "Reset", variant: "warning" };
    case "BLOCKED_BY_NETWORK_FILTER":
      return { label: "Blocked", variant: "warning" };
    case "BLOCKED_BY_GOVERNMENT":
      return { label: "Gov Block", variant: "warning" };
    case "CLOUDFLARE_BLOCKED":
      return { label: "CF Block", variant: "warning" };
    default:
      return { label: classification || "-", variant: "neutral" };
  }
}

function getCountryFlag(country: string): string {
  if (!country || country.length !== 2) return "";
  const codePoints = country
    .toUpperCase()
    .split("")
    .map((char) => 127397 + char.charCodeAt(0));
  return String.fromCodePoint(...codePoints);
}

export default function RecentScans() {
  const [scans, setScans] = useState<RecentScanItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchScans = async () => {
    try {
      const data = await getRecentScans();
      setScans(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch scans");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScans();
  }, []);

  if (loading) {
    return <div className="recent-scans__status">Loading scans...</div>;
  }

  if (error) {
    return <div className="recent-scans__status recent-scans__status--error">{error}</div>;
  }

  if (scans.length === 0) {
    return null;
  }

  return (
    <div className="recent-scans">
      <div className="recent-scans__header">
        <h2 className="recent-scans__title">Recent Scans</h2>
        <span className="recent-scans__count">{scans.length} scans</span>
      </div>
      <div className="recent-scans__table-wrapper">
        <table className="recent-scans__table">
          <thead>
            <tr>
              <th className="recent-scans__th recent-scans__th--url">URL</th>
              <th className="recent-scans__th">Age</th>
              <th className="recent-scans__th">Status</th>
              <th className="recent-scans__th recent-scans__th--num">Size</th>
              <th className="recent-scans__th recent-scans__th--num">Reqs</th>
              <th className="recent-scans__th recent-scans__th--num">IPs</th>
              <th className="recent-scans__th">Country</th>
            </tr>
          </thead>
          <tbody>
            {scans.map((scan) => {
              const indicator = getClassIndicator(scan.classification);
              return (
                <tr
                  key={scan.request_id}
                  className="recent-scans__row"
                  onClick={() => navigate(`/result/${scan.request_id}`)}
                >
                  <td className="recent-scans__td recent-scans__td--url">{scan.url}</td>
                  <td className="recent-scans__td">{formatAge(scan.created_at)}</td>
                  <td className="recent-scans__td">
                    <span className={`recent-scans__badge recent-scans__badge--${indicator.variant}`}>
                      {indicator.label}
                    </span>
                  </td>
                  <td className="recent-scans__td recent-scans__td--num">{formatBytes(scan.size)}</td>
                  <td className="recent-scans__td recent-scans__td--num">{scan.requests || "-"}</td>
                  <td className="recent-scans__td recent-scans__td--num">{scan.ips || "-"}</td>
                  <td className="recent-scans__td">
                    {scan.country && (
                      <span title={scan.country}>
                        {getCountryFlag(scan.country)} {scan.country}
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
