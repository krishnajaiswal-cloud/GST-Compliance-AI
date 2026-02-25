import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import ExcelViewer from "../components/ExcelViewer";

const API_BASE = import.meta.env.VITE_API_BASE;

const Report = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { sessionId, clientName, month } = location.state || {};

  const [sessionData, setSessionData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stage, setStage] = useState("extracted");
  const [gstr2bInput, setGstr2bInput] = useState("manual");
  const [gstr2bFile, setGstr2bFile] = useState<File | null>(null);
  const [gstr2bLoading, setGstr2bLoading] = useState(false);
  const [gstr2bError, setGstr2bError] = useState<string | null>(null);
  const [mismatchRunning, setMismatchRunning] = useState(false);
  const [reportCard, setReportCard] = useState<any>(null);
  const [gstin, setGstin] = useState("");
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    if (!sessionId) {
      setError("No session found. Please upload documents first.");
      setLoading(false);
      return;
    }
    fetchSessionData();
  }, [sessionId]);

  const fetchSessionData = async () => {
    try {
      setLoading(true);

      const response = await fetch(
        `${API_BASE}/process/session/${sessionId}`
      );

      const text = await response.text();
      if (!response.ok) throw new Error(text);

      const data = JSON.parse(text);
      setSessionData(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load report");
      setSessionData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadExcel = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/process/download-excel/${sessionId}`
      );

      if (!response.ok) throw new Error("Failed to download Excel");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download =
        stage === "extracted"
          ? "invoices.xlsx"
          : "mismatch_report.xlsx";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleGstr2bSubmit = async () => {
    if (!gstr2bFile) {
      setGstr2bError("Please select an Excel file");
      return;
    }

    setGstr2bLoading(true);
    setGstr2bError(null);

    try {
      const formData = new FormData();
      formData.append("file", gstr2bFile);

      const response = await fetch(
        `${API_BASE}/process/upload-gstr2b/${sessionId}`,
        {
          method: "POST",
          body: formData,
        }
      );

      const text = await response.text();
      if (!response.ok) throw new Error(text);

      setStage("mismatch");
      setGstr2bFile(null);
      await fetchSessionData();
    } catch (err: any) {
      setGstr2bError(err.message);
    } finally {
      setGstr2bLoading(false);
    }
  };

  const handleFetchFromGovt = async () => {
    if (!gstin.trim()) {
      setGstr2bError("Please enter GSTIN");
      return;
    }

    setGstr2bLoading(true);
    setGstr2bError(null);

    try {
      const response = await fetch(
        `${API_BASE}/process/govt-api/gstr2b?gstin=${gstin}&period=${month}`
      );

      const text = await response.text();
      if (!response.ok) throw new Error(text);

      const data = JSON.parse(text);

      const uploadResponse = await fetch(
        `${API_BASE}/process/upload-gstr2b/${sessionId}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data.data),
        }
      );

      if (!uploadResponse.ok) throw new Error("Upload failed");

      setStage("mismatch");
      setGstin("");
      await fetchSessionData();
    } catch (err: any) {
      setGstr2bError(err.message);
    } finally {
      setGstr2bLoading(false);
    }
  };

  const handleRunMismatchDetection = async () => {
    setMismatchRunning(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE}/process/detect-mismatches/${sessionId}`,
        { method: "POST" }
      );

      const text = await response.text();
      if (!response.ok) throw new Error(text);

      const data = JSON.parse(text);
      setReportCard(data.report_card);
      setStage("report");
      await fetchSessionData();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setMismatchRunning(false);
    }
  };

  const handleEditAndUpdateExcel = async (updatedData: any) => {
    try {
      const response = await fetch(
        `${API_BASE}/process/update-excel/${sessionId}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ invoices: updatedData }),
        }
      );

      if (!response.ok) throw new Error("Failed to update Excel");
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleBackToHome = () => navigate("/");

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p>Loading report...</p>
        </div>
      </div>
    );
  }

  if (error && !sessionData) {
    return (
      <div className="p-6">
        <div className="bg-red-100 p-4 rounded">
          <p>{error}</p>
          <button
            onClick={handleBackToHome}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto bg-white p-6 rounded shadow">
        <h1 className="text-2xl font-bold mb-4">
          GST Report – {clientName} ({month})
        </h1>

        {sessionData?.extracted_invoices && (
          <ExcelViewer
            invoices={sessionData.extracted_invoices}
            isEditable={stage === "extracted"}
            onUpdate={handleEditAndUpdateExcel}
          />
        )}
      </div>
    </main>
  );
};

export default Report;