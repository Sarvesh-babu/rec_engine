import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import UploadPage from "./pages/UploadPage";
import EdaReviewPage from "./pages/EdaReviewPage";
import ModelSettingsPage from "./pages/ModelSettingsPage";
import ResultsPage from "./pages/ResultsPage";
import ValidationPage from "./pages/ValidationPage";

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/upload" replace />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/eda/:runId" element={<EdaReviewPage />} />
        <Route path="/models/:runId" element={<ModelSettingsPage />} />
        <Route path="/results/:runId" element={<ResultsPage />} />
        <Route path="/validation/:runId" element={<ValidationPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
