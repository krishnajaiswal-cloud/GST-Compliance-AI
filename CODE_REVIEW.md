# Code Review: AI-Driven GST Document Processing System

## 📋 Project Overview

**Purpose**: An intelligent system that processes GST invoices, detects mismatches with GSTR2B records, and generates professional compliance reports.

**Tech Stack**:
- **Backend**: Python FastAPI, OCR (Tesseract), Google Gemini AI, Pandas, OpenPyXL
- **Frontend**: React (TypeScript), Vite, Tailwind CSS, React Router
- **Data Processing**: Fuzzy matching algorithm, reconciliation engine

---

## 🏗️ Architecture Overview

```
User Interface (React/TypeScript)
         ↓
    FastAPI Backend
         ↓
    ┌────────────────────────────────────┐
    │  Document Processing Pipeline      │
    ├────────────────────────────────────┤
    │ 1. Extract (OCR + Gemini)          │
    │ 2. Parse GSTR2B (Excel upload)     │
    │ 3. Detect Mismatches (Fuzzy match) │
    │ 4. Generate Reports (Excel + UI)   │
    └────────────────────────────────────┘
```

---

## 📁 Backend Structure

### Core Files

#### **1. [app/main.py](app/main.py)** - Application Entry Point
- Initializes FastAPI application
- Configures CORS middleware for local development (ports 5173-5175)
- Routes:
  - `/upload` - Upload router for document ingestion
  - `/process` - Processing router for extraction & mismatch detection
- Health check endpoint: `GET /`

#### **2. [app/config.py](app/config.py)** - Configuration
- Manages environment variables
- Sets up upload directory paths
- Configures API keys (Gemini)

---

### Services Layer

#### **3. [app/services/document_processor.py](app/services/document_processor.py)** - OCR & AI Extraction
**Purpose**: Extract invoice data from PDFs and images using OCR + Google Gemini

**Key Methods**:
- `process_documents()` - Main async method to process multiple files with progress tracking
- `_extract_text_from_file()` - Detects file type and routes to appropriate extractor
- `_extract_text_from_pdf()` - Uses Tesseract OCR on PDF pages
- `_extract_text_from_image()` - Direct OCR on image files
- `_extract_structured_data()` - Uses Google Gemini to parse OCR output into JSON

**Output Format**:
```json
{
  "file": "invoice_001.pdf",
  "invoice_number": "INV-2024-001",
  "invoice_date": "2024-01-15",
  "gstin": "27ABCDE1234F1Z5",
  "amount": 50000.00,
  "status": "success"
}
```

**Error Handling**: Gracefully falls back to raw text if Gemini unavailable

---

#### **4. [app/services/mismatch_detector.py](app/services/mismatch_detector.py)** - Matching Algorithm
**Purpose**: Compare extracted invoices with GSTR2B records and identify discrepancies

**Key Methods**:
- `detect_mismatches()` - Main comparison logic
  - Parses GSTR2B data
  - Fuzzy matches extracted invoices (85% similarity threshold)
  - Generates detailed mismatch report
- `_calculate_match_score()` - Compares fields:
  - Invoice number (exact or fuzzy)
  - Invoice date (exact or within 3 days)
  - Amount (within 2% tolerance)
  - GSTIN (exact match required)
- `_parse_gstr2b()` - Extracts invoice list from GSTR2B Excel

**Output**:
```json
{
  "matched_pairs": [
    {
      "extracted": {...},
      "gstr2b": {...},
      "match_score": 0.95,
      "mismatches": ["amount_mismatch", "date_variance"]
    }
  ],
  "unmatched_extracted": [...],
  "unmatched_gstr2b": [...],
  "summary": {
    "matched": 45,
    "unmatched_extracted": 3,
    "unmatched_gstr2b": 2
  }
}
```

---

#### **5. [app/services/excel_generator.py](app/services/excel_generator.py)** - Report Generation
**Purpose**: Create professional Excel reports with formatting and highlighting

**Key Methods**:
- `generate_invoice_sheet()` - Creates sheet with extracted invoice data
- `generate_mismatch_report_sheet()` - Multi-sheet report:
  - **Summary**: Overall statistics and flagged items
  - **Matched**: Successfully matched invoices with discrepancy highlights
  - **Unmatched (Extracted)**: Invoices in documents but not in GSTR2B
  - **Unmatched (GSTR2B)**: Invoices in GSTR2B but not in documents
  - **Consolidated**: All data for reconciliation

**Formatting**:
- Color-coded cells: Yellow (mismatches), Red (errors), Green (matches)
- Blue header row with white text
- Borders and text wrapping
- Auto-adjusted column widths

**Output**: Binary Excel file (.xlsx format)

---

### API Layer

#### **6. [app/api/processing.py](app/api/processing.py)** - Processing Endpoints
**Purpose**: RESTful API for document processing workflow

**Endpoints**:

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/process/extract` | Extract invoice data from uploaded documents |
| POST | `/process/upload-gstr2b/{session_id}` | Upload GSTR2B Excel file |
| POST | `/process/detect-mismatches/{session_id}` | Run mismatch detection algorithm |
| GET | `/process/session/{session_id}` | Fetch session status and data |
| GET | `/process/download-excel/{session_id}` | Download Excel report |
| GET | `/process/download-report-excel/{session_id}` | Download formatted mismatch report |
| POST | `/process/edit-cell/{session_id}` | Edit Excel cell (for manual corrections) |
| POST | `/process/finalize/{session_id}` | Finalize and save processed data |

**ProcessingSession Class**:
- Tracks in-memory session state (in production, use database)
- Properties:
  - `session_id` - Unique identifier
  - `client_name` - Client reference
  - `month` - Tax period
  - `status` - Current stage
  - `progress` - Percentage completion
  - `extracted_invoices` - OCR results
  - `gstr2b_data` - Uploaded GSTR2B
  - `mismatch_results` - Comparison output
  - `error` - Error messages if any

---

#### **7. [app/api/upload.py](app/api/upload.py)** - Upload Endpoints
(Referenced in main.py, handles file ingestion)

---

## 💻 Frontend Structure

### Pages

#### **[src/pages/landing.tsx](src/pages/landing.tsx)** - Landing Page
- Welcome/introduction
- Links to upload workflow
- Project description

#### **[src/pages/upload.tsx](src/pages/upload.tsx)** - Document Upload
**Features**:
- Client name input
- Month selector
- File drop zone
- Progress indication
- Error/success messages

**Workflow**:
1. User selects files and enters client info
2. Form submits to `POST /upload/`
3. Displays success/failure feedback

#### **[src/pages/report.tsx](src/pages/report.tsx)** - Multi-Stage Report Viewer
**5-Stage Workflow**:

**Stage 1: Extracted Invoices**
- View OCR-extracted data in table
- Download as Excel
- Shows status of extraction process

**Stage 2: GSTR2B Upload**
- Upload Excel file with GSTR2B data
- Manual entry option (TODO)
- Validates file format

**Stage 3: Mismatch Detection**
- Runs comparison algorithm
- Shows progress
- Generates detailed report cards

**Stage 4: Report Review**
- Display mismatch summary
- View by category:
  - Matched invoices
  - Unmatched (extracted)
  - Unmatched (GSTR2B)
- Edit cells inline for corrections

**Stage 5: Finalization**
- Export final reconciliation report
- Save processed data
- Archive session

**Key Features**:
- Real-time session status polling
- Drag-and-drop file upload
- Inline Excel cell editing
- Multiple export options
- Progress indicators

---

### Components

#### **[src/components/ExcelViewer.tsx](src/components/ExcelViewer.tsx)** - Data Grid
- Display tabular data (extracted invoices, mismatch report)
- Inline cell editing
- Color-coded highlights for mismatches
- Responsive table design

#### **[src/components/FileDropzone.tsx](src/components/FileDropzone.tsx)** - File Upload
- Drag-and-drop interface
- File type validation
- Multiple file support

#### **[src/components/UploadForm.tsx](src/components/UploadForm.tsx)** - Form Handler
- Client name input
- Month selector
- File selection
- Form validation
- Progress display during upload

#### **[src/components/Navbar.tsx](src/components/Navbar.tsx)** - Navigation
- Header with logo/branding
- Links to all pages
- Session info display

---

### Routing

#### **[src/App.tsx](src/App.tsx)**
```typescript
/ → Landing page
/upload → Document upload
/report → Multi-stage report viewer
```

**CORS Configuration**: Allows local frontend (ports 5173-5175)

---

## 🔄 Data Flow

### Complete Processing Pipeline

```
1. USER UPLOADS DOCUMENTS
   └─→ Frontend: UploadForm
       └─→ Backend: POST /upload
           └─→ Saves files to data/uploads/{client_name}/{month}/
           └─→ Returns session_id

2. NAVIGATE TO REPORT PAGE
   └─→ Frontend: Report component receives session_id
       └─→ GET /process/session/{session_id}
           └─→ Shows extraction status

3. REQUEST OCR EXTRACTION
   └─→ Frontend: Click "Extract Invoices" on Stage 1
       └─→ POST /process/extract
           └─→ DocumentProcessor.process_documents()
               ├─ For each file:
               │  ├─ Extract text via Tesseract OCR
               │  └─ Parse with Google Gemini AI
               └─ Returns structured JSON

4. UPLOAD GSTR2B DATA
   └─→ Frontend: Upload Excel file on Stage 2
       └─→ POST /process/upload-gstr2b/{session_id}
           └─→ Parse Excel using openpyxl
           └─→ Store in session.gstr2b_data

5. DETECT MISMATCHES
   └─→ Frontend: Click "Detect Mismatches" on Stage 3
       └─→ POST /process/detect-mismatches/{session_id}
           └─→ MismatchDetector.detect_mismatches()
               ├─ Fuzzy match invoices (85% threshold)
               ├─ Identify discrepancies
               └─ Return match report

6. GENERATE REPORT
   └─→ ExcelGenerator creates multi-sheet workbook
       ├─ Sheet 1: Summary
       ├─ Sheet 2: Matched invoices (with highlights)
       ├─ Sheet 3: Unmatched extracted
       ├─ Sheet 4: Unmatched GSTR2B
       └─ Sheet 5: Consolidated

7. DOWNLOAD REPORT
   └─→ Frontend: Click "Download Excel"
       └─→ GET /process/download-report-excel/{session_id}
           └─→ Returns binary Excel file
           └─→ Browser triggers download
```

---

## 🔑 Key Algorithms

### 1. Fuzzy Invoice Matching
**Location**: `mismatch_detector.py::_calculate_match_score()`

**Logic**:
```python
Similarity Score = 
  40% × invoice_number_match +
  20% × invoice_date_match +
  30% × amount_match +
  10% × gstin_match

Threshold: 0.85 (85% match required)
```

**Field Matching**:
- **Invoice Number**: Exact or fuzzy (SequenceMatcher)
- **Date**: Within 3 days tolerance
- **Amount**: Within 2% tolerance
- **GSTIN**: Exact match only

### 2. OCR + AI Extraction
**Location**: `document_processor.py::_extract_structured_data()`

**Process**:
1. Tesseract OCR extracts raw text from PDF/image
2. Text sent to Google Gemini AI
3. Gemini parses JSON with fields:
   - invoice_number
   - invoice_date
   - gstin
   - amount
   - tax_details

---

## 📊 Data Models

### Invoice Structure
```python
{
    "file": str,                    # Source filename
    "invoice_number": str,          # Invoice ID
    "invoice_date": str,            # Date (YYYY-MM-DD)
    "gstin": str,                   # 15-digit GSTIN
    "amount": float,                # Taxable value
    "cgst": float,                  # Central GST
    "sgst": float,                  # State GST
    "igst": float,                  # Integrated GST
    "total_amount": float,          # Total including tax
    "gst_rate": float,              # Applicable rate
    "status": str                   # "success", "error", "pending_review"
}
```

### Mismatch Detail
```python
{
    "invoice_number": str,
    "match_score": float,           # 0.85-1.0
    "issues": [str]                 # ["amount_mismatch", "date_variance"]
}
```

---

## 🔐 Security & Best Practices

### What's Implemented
✅ CORS middleware (restricted to localhost)
✅ Input validation (file types, formats)
✅ Error handling with graceful fallbacks
✅ Session isolation (per-session data storage)
✅ File organization by client/month

### What Needs Attention
⚠️ **API Key Management**: GEMINI_API_KEY stored in .env (use secrets manager in production)
⚠️ **File Cleanup**: Uploaded files not automatically deleted (add retention policy)
⚠️ **Database**: Using in-memory session storage (implement persistent DB)
⚠️ **Authentication**: No user auth (add JWT/OAuth)
⚠️ **Rate Limiting**: No rate limits on endpoints
⚠️ **HTTPS**: Not enabled (required for production)

---

## 📦 Dependencies

### Backend Requirements
```
fastapi==0.109.0              # Web framework
uvicorn==0.27.0               # ASGI server
python-dotenv==1.0.0          # Environment config
Pillow==11.0.0                # Image processing
PyPDF2==3.0.1                 # PDF reading
pdf2image==1.16.3             # PDF to image conversion
pytesseract==0.3.10           # OCR wrapper
opencv-python==4.8.1.78       # Image processing
numpy>=1.26.0                 # Numerical computing
pandas>=2.0.0                 # Data manipulation
scikit-learn>=1.3.0           # Machine learning utils
requests==2.31.0              # HTTP client
python-multipart==0.0.6       # Form data handling
google-genai>=0.0.1           # Google Gemini API
openpyxl>=3.1.0               # Excel file generation
python-jose==3.3.0            # JWT handling
aiofiles==23.2.1              # Async file operations
```

### Frontend Dependencies
- React + TypeScript
- Vite (build tool)
- React Router (navigation)
- Tailwind CSS (styling)
- Axios or fetch (HTTP client)

---

## 🚀 Running the Application

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### Endpoints Summary
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## 📝 Documentation Files

The project includes comprehensive guides:
- **README_IMPLEMENTATION.md** - Feature overview
- **QUICKSTART.md** - 5-minute setup
- **WORKFLOW_GUIDE.md** - Complete usage guide
- **API_EXAMPLES.md** - cURL + React examples
- **TESTING_CHECKLIST.md** - QA procedures
- **GSTR2B_RECONCILIATION_LOGIC.md** - Technical algorithm details

---

## ✅ Summary

**Strengths**:
- ✅ End-to-end document processing pipeline
- ✅ Intelligent fuzzy matching algorithm
- ✅ Professional Excel report generation with formatting
- ✅ Real-time progress tracking
- ✅ Multi-stage UI workflow matching backend process
- ✅ Error handling and fallbacks
- ✅ Clear separation of concerns (services, APIs, models)

**Areas for Enhancement**:
- 🔧 Persistent database for sessions (currently in-memory)
- 🔧 User authentication and authorization
- 🔧 Rate limiting and request throttling
- 🔧 Comprehensive error logging
- 🔧 Unit and integration tests
- 🔧 Docker containerization
- 🔧 API versioning for backward compatibility

