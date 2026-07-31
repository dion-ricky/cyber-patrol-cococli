import { useNavigate } from "react-router-dom";
import ScanForm from "../components/ScanForm";
import RecentScans from "../components/RecentScans";

export default function Home() {
  const navigate = useNavigate();

  const handleScanStarted = (requestId: string) => {
    navigate(`/result/${requestId}`);
  };

  return (
    <div className="layout-page">
      <div className="home">
        <div className="home__hero">
          <h1 className="home__title">Web Scanner</h1>
          <p className="home__subtitle">
            Analyze websites for threats, scams, and malicious content
          </p>
        </div>
        <ScanForm onScanStarted={handleScanStarted} />
        <RecentScans />
      </div>
    </div>
  );
}
