# GSTR2B Excel Upload Feature Guide

## Overview
The GSTR2B data upload feature on the Report page has been updated to accept **Excel files (.xlsx, .xls)** instead of JSON data. This makes it more user-friendly and aligns with typical GST processes.

## Features Implemented

### 1. Excel File Upload
- **File Types Accepted**: `.xlsx`, `.xls`
- **Validation**: File type checked on both frontend and backend
- **Error Handling**: User-friendly error messages for invalid formats

### 2. Drag-and-Drop Interface
Users can upload GSTR2B Excel files in two ways:
- **Drag and Drop**: Drag the Excel file directly onto the designated area
- **Click to Browse**: Click on the upload area to open file picker

The drag-and-drop area provides visual feedback:
- **Inactive State**: Gray border with folder icon
- **Hover/Active State**: Purple border with highlight indicating drop zone is active

### 3. File Parsing on Backend
The backend automatically parses Excel files and extracts invoice data with:
- **Intelligent Column Mapping**: Recognizes common column names like:
  - Invoice number: `invoice_no`, `invoice number`, `invoiceno`, `inv_no`
  - Invoice date: `invoice_date`, `invoice date`, `invoicedate`, `inv_date`
  - Supplier GSTIN: `supplier_gstin`, `gstin`, `vendor_gstin`, `supplier gstin`
  - Taxable value: `taxable_value`, `taxable value`, `amount`, `invoice_amount`
  - GST components: `cgst`, `sgst`, `igst`, `gst_rate`
  - Total amount: `total_amount`, `total amount`, `total`, `grand total`

- **Type Conversion**: Numeric fields automatically converted to float values
- **Empty Row Handling**: Skips empty rows in the Excel file

## Technical Implementation

### Frontend Changes (report.tsx)

#### State Variables Added:
```typescript
const [gstr2bFile, setGstr2bFile] = useState(null);
const [dragActive, setDragActive] = useState(false);
```

#### Event Handlers:
- `handleDrag()`: Manages drag enter/leave events for visual feedback
- `handleDrop()`: Processes dropped files and validates format
- `handleFileSelect()`: Handles file selection from input element
- `handleGstr2bSubmit()`: Submits Excel file to backend via FormData

#### UI Components:
- Hidden file input with `.xlsx`, `.xls` accept filter
- Drag-and-drop zone with dynamic styling based on drag state
- File preview showing selected filename
- Submit button enabled only when file is selected

### Backend Changes (processing.py)

#### New Imports:
```python
from fastapi import File, UploadFile
from openpyxl import load_workbook
import tempfile
```

#### Updated Endpoint:
```python
@router.post("/upload-gstr2b/{session_id}")
async def upload_gstr2b(session_id: str, file: UploadFile = File(...)):
```

**Changes**:
- Now accepts `UploadFile` instead of JSON request body
- Uses `multipart/form-data` encoding instead of JSON
- Returns invoice count in response

#### New Helper Function:
```python
def _parse_gstr2b_excel(file_path: str) -> Dict:
```

**Functionality**:
- Reads Excel workbook using openpyxl
- Extracts headers from first row
- Maps columns to standard invoice field names
- Handles type conversion for numeric fields
- Returns parsed invoice data as dictionary

## Usage Workflow

### Step 1: Navigate to Report Page
After uploading and extracting invoices, the report page shows Step 2: Upload GSTR2B Data

### Step 2: Select Input Method
Choose between:
- **Manual Input (Upload Excel)** - Default option
- **Fetch from Govt API** - Alternative method

### Step 3: Upload Excel File
For Manual Input mode:
1. Drag and drop your GSTR2B Excel file onto the upload area, OR
2. Click the upload area to browse and select file
3. Confirm the selected file is displayed
4. Click "Upload GSTR2B" button

### Step 4: Processing
- Backend parses the Excel file
- Validates invoice data structure
- Shows success message with invoice count
- Proceeds to mismatch detection

## Excel File Format Requirements

### Required Columns
Your GSTR2B Excel file should contain at least:
- Invoice Number
- Invoice Date
- Supplier GSTIN
- Taxable Value / Amount
- GST components (CGST, SGST, IGST) or GST Rate
- Total Amount

### Column Naming Flexibility
The system recognizes various column name formats:
- You can use any of the mapped variations (case-insensitive)
- Column order doesn't matter
- Extra columns are ignored

### Example Excel Structure
| Invoice No | Invoice Date | Supplier GSTIN | Taxable Value | CGST | SGST | IGST | Total |
|---|---|---|---|---|---|---|---|
| INV-001 | 2025-01-15 | 18AABCT1234H1Z0 | 10000 | 900 | 900 | 0 | 11800 |
| INV-002 | 2025-01-16 | 18AABCT5678H1Z0 | 5000 | 450 | 450 | 0 | 5900 |

## Error Handling

### Frontend Validation
- **Wrong File Type**: "Please drop an Excel file (.xlsx or .xls)"
- **File Not Selected**: "Please select an Excel file"
- **Upload Failure**: Displays backend error message

### Backend Validation
- **Invalid Excel Format**: "Invalid Excel format. Please ensure it contains invoice data."
- **File Read Error**: "Error processing Excel file: [detailed error]"
- **No Invoices Found**: Empty invoices list returned

## Benefits

✅ **User-Friendly**: Familiar drag-and-drop interface
✅ **Flexible Column Names**: Accepts various column naming conventions
✅ **Automatic Type Conversion**: Numeric fields handled correctly
✅ **Validation**: Both client and server-side validation
✅ **Performance**: Efficient Excel parsing with temporary file handling
✅ **Scalability**: Supports large Excel files with many invoices

## Migration Notes

### For Users Previously Using JSON Input
- No longer need to manually format JSON
- Simply export/download your GSTR2B data as Excel
- Upload directly without any formatting required

### Data Compatibility
- All previously validated JSON data structures still supported
- Excel parsing produces equivalent data format
- Mismatch detection logic unchanged

## Troubleshooting

### "Only Excel files (.xlsx, .xls) are allowed"
- Ensure your file has `.xlsx` or `.xls` extension
- Save Excel file in proper format (not CSV or other formats)

### "Invalid Excel format"
- Verify Excel file has headers in the first row
- Check that column names match expected invoice fields
- Ensure data starts from row 2 onwards

### File Not Showing After Selection
- Try dragging the file again
- Clear browser cache if using same filename
- Ensure file is not corrupted

### "Session not found"
- Start a new document upload process first
- Don't access report page directly from URL
- Use the workflow from the landing page

## Future Enhancements

Potential improvements for consideration:
- 📊 Excel template download for standardized format
- 🔍 Preview of parsed data before submission
- 📈 Batch upload support for multiple GSTR2B files
- 🔗 Direct integration with GST portal export
- 📝 Custom column mapping UI for non-standard formats

## Testing Checklist

- [x] Drag and drop file upload works
- [x] Click to browse file selection works
- [x] File type validation on frontend
- [x] File type validation on backend
- [x] Excel parsing with various column names
- [x] Numeric type conversion
- [x] Empty row handling
- [x] Error messages display correctly
- [x] Success flow to mismatch detection
- [x] Invoice count displayed in response
