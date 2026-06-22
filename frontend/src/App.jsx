import { Navigate, Route, Routes } from "react-router-dom";
import UploadPage from "./pages/UploadPage";
import EdaReviewPage from "./pages/EdaReviewPage";
import ResultsPage from "./pages/ResultsPage";
import ValidationPage from "./pages/ValidationPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/upload" replace />} />
      <Route path="/upload" element={<UploadPage />} />
      <Route path="/eda/:runId" element={<EdaReviewPage />} />
      <Route path="/results/:runId" element={<ResultsPage />} />
      <Route path="/validation/:runId" element={<ValidationPage />} />
    </Routes>
  );
}

export default App;
