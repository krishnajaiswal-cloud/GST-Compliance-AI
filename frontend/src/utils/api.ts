// API Configuration - Centralized endpoint management
export const API_BASE_URL = "http://localhost:8000";

export const API_ENDPOINTS = {
  // Upload
  uploadInvoices: `${API_BASE_URL}/upload/`,

  // Processing
  processDocuments: `${API_BASE_URL}/process/process`,
  getProgress: (sessionId: string) => `${API_BASE_URL}/process/progress/${sessionId}`,
  getSessionData: (sessionId: string) => `${API_BASE_URL}/process/session/${sessionId}`,
  downloadExcel: (sessionId: string) => `${API_BASE_URL}/process/download-excel/${sessionId}`,
  updateExcel: (sessionId: string) => `${API_BASE_URL}/process/update-excel/${sessionId}`,
  uploadGstr2b: (sessionId: string) => `${API_BASE_URL}/process/upload-gstr2b/${sessionId}`,
  detectMismatches: (sessionId: string) => `${API_BASE_URL}/process/detect-mismatches/${sessionId}`,
  fetchGovtGstr2b: (gstin: string, period: string) => 
    `${API_BASE_URL}/process/govt-api/gstr2b?gstin=${gstin}&period=${period}`,

  // GSTR2B Comparison
  compareGstr2b: (sessionId: string) => `${API_BASE_URL}/process/compare-gstr2b?session_id=${sessionId}`,
  getComparisonResults: (sessionId: string) => `${API_BASE_URL}/process/comparison-results/${sessionId}`,
};
