import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import ResultPage from "./pages/ResultPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/result/:requestId" element={<ResultPage />} />
      </Routes>
    </BrowserRouter>
  );
}
