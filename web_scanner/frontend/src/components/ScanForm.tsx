import { useState } from "react";
import { startScan } from "../api";

interface Props {
  onScanStarted: (requestId: string) => void;
}

export default function ScanForm({ onScanStarted }: Props) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const data = await startScan(url.trim());
      onScanStarted(data.request_id);
      setUrl("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan failed");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setUrl("");
    setError(null);
  };

  return (
    <div className="scan-form">
      <form onSubmit={handleSubmit}>
        <div className="scan-form__group">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter URL to scan (e.g. example.com)"
            disabled={loading}
            className="scan-form__input"
          />
          <button
            type="submit"
            className="btn-primary scan-form__button"
            disabled={loading || !url.trim()}
          >
            {loading ? "Scanning..." : "Scan"}
          </button>
          <button
            type="button"
            className="scan-form__button scan-form__button--secondary"
            onClick={handleClear}
            disabled={loading}
          >
            Clear
          </button>
        </div>
      </form>
      {error && <div className="status status-error">{error}</div>}
    </div>
  );
}
