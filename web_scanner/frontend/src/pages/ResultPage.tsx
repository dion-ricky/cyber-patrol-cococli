import { useParams } from "react-router-dom";
import ScanResults from "../components/ScanResults";

export default function ResultPage() {
  const { requestId } = useParams<{ requestId: string }>();

  if (!requestId) {
    return <div className="card status status-error">Missing request ID</div>;
  }

  return <ScanResults requestId={requestId} />;
}
