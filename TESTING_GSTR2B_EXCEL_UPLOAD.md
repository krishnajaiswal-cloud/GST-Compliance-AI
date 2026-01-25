# Quick Testing Guide - GSTR2B Excel Upload Feature

## ✅ Implementation Complete

All changes have been successfully implemented and tested:
- ✅ Frontend drag-and-drop interface
- ✅ Excel file parsing on backend
- ✅ Intelligent column mapping
- ✅ TypeScript compilation (47 modules)
- ✅ Python syntax validation

## 🚀 How to Test

### 1. Start the Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Backend will run on: http://localhost:8000

### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend will run on: http://localhost:5173 (or next available port)

### 3. Test the Workflow

#### Step A: Upload Documents
1. Navigate to http://localhost:5173
2. Click "Upload Documents"
3. Select PDF/Image files or folder containing invoices
4. Enter Client Name and Month
5. Click "Upload & Process"
6. Wait for extraction to complete (~30 seconds per document)

#### Step B: Test GSTR2B Excel Upload
1. After extraction completes, click "Go to Report"
2. On Report page, you'll see "Step 2: Upload GSTR2B Data"
3. Ensure "Manual Input (Upload Excel)" is selected
4. You can now:
   - **Drag & Drop**: Drag your Excel file onto the purple dashed box
   - **Click to Browse**: Click the upload area to select file from computer

#### Step C: Verify Upload Success
- When file is selected, you'll see: "✓ Selected: filename.xlsx"
- Click "Upload GSTR2B" button
- On success: "✓ GSTR2B data uploaded successfully" message appears
- System automatically shows invoice count from Excel file

### 4. Test Cases to Verify

#### ✅ Test 1: Valid Excel Upload (Drag & Drop)
**Expected**: File accepted, filename shown, upload succeeds
```
File: sample_gstr2b.xlsx
Method: Drag and drop
Expected Result: Success with invoice count displayed
```

#### ✅ Test 2: Valid Excel Upload (Click Browse)
**Expected**: File picker opens, file selected, upload succeeds
```
File: gstr2b_data.xlsx
Method: Click upload area
Expected Result: Success with invoice count displayed
```

#### ✅ Test 3: Invalid File Type
**Expected**: Error message displayed, file rejected
```
File: invoice_data.pdf or data.json
Method: Drag and drop
Expected Error: "Please drop an Excel file (.xlsx or .xls)"
```

#### ✅ Test 4: Excel with Various Column Names
**Expected**: All columns recognized and parsed correctly
```
Test column name variations:
- "Invoice Number" or "Invoice_No" or "invoiceno"
- "Invoice Date" or "invoice_date"
- "GSTIN" or "Supplier GSTIN"
- "Amount" or "Taxable Value"
- "CGST Amount" or "CGST"
```

#### ✅ Test 5: Empty Rows Handling
**Expected**: Empty rows skipped, only data rows processed
```
Excel structure:
Row 1: Headers
Row 2: Data
Row 3: Empty
Row 4: Data
Expected: Only rows 2 and 4 processed
```

#### ✅ Test 6: Numeric Field Conversion
**Expected**: Amount fields correctly converted to numbers
```
Taxable Value: "10000" → 10000.0
CGST: "900" → 900.0
SGST: "900" → 900.0
IGST: "0" → 0.0
Total: "11800" → 11800.0
```

## 📊 Test Data Preparation

### Create Sample GSTR2B Excel File
Create an Excel file with these columns in row 1:
```
| Invoice No | Invoice Date | Supplier GSTIN | Taxable Value | CGST | SGST | IGST | Total |
```

Sample data:
```
| INV-001    | 2025-01-15  | 18AABCT1234H1Z0 | 10000         | 900  | 900  | 0    | 11800 |
| INV-002    | 2025-01-16  | 18AABCT5678H1Z0 | 5000          | 450  | 450  | 0    | 5900  |
| INV-003    | 2025-01-17  | 18AABCT9999H1Z0 | 7500          | 675  | 675  | 0    | 8850  |
```

Save as: `gstr2b_sample.xlsx`

## 🔍 Debugging Tips

### Issue: File not being accepted
**Solutions**:
1. Check file extension is `.xlsx` or `.xls`
2. Verify file is not corrupted (can open in Excel)
3. Check browser console (F12) for any JavaScript errors
4. Clear browser cache and try again

### Issue: "Invalid Excel format" error
**Solutions**:
1. Ensure first row contains headers
2. Verify at least one invoice row exists (row 2+)
3. Check that column names match expected variations
4. Ensure numeric fields are actual numbers (not text)

### Issue: Drag-and-drop not working
**Solutions**:
1. Try click-to-browse instead
2. Check browser support (should work in modern browsers)
3. Clear browser cache
4. Try different file
5. Check browser console for errors

### Issue: Backend error 500
**Solutions**:
1. Check backend logs in terminal
2. Verify file is valid Excel format
3. Ensure temp directory has write permissions
4. Check available disk space

## 📋 Browser Console Checks

Press F12 to open Developer Tools and check:

### Network Tab
- Verify POST request to `/process/upload-gstr2b/{session_id}`
- Check Content-Type is `multipart/form-data`
- Response should include: `{"status": "success", "invoices_count": N}`

### Console Tab
- No red error messages
- No CORS errors
- No "Failed to fetch" errors

## ✨ Visual Feedback Elements

### Drag-and-Drop Area States

**Before Hover**:
- Gray border (2px dashed)
- Gray background
- Folder icon 📁
- Text: "Drag and drop your GSTR2B Excel file here"

**On Hover/Drag Over**:
- Purple border (2px dashed)
- Purple background (50% opacity)
- Same folder icon
- Same text

**After File Selected**:
- Green success message below drop area
- Shows: "✓ Selected: filename.xlsx"

**On Upload Clicked**:
- Button text changes to "Uploading..."
- Button disabled (grayed out)
- Spinner animation (if visible)

**On Upload Complete**:
- Page shows: "✓ GSTR2B data uploaded successfully"
- Auto-advances to Step 3
- All controls re-enabled

## 🎯 Expected User Journey

1. User lands on Report page
2. Sees "Step 2: Upload GSTR2B Data" section
3. "Manual Input (Upload Excel)" is pre-selected
4. Sees drag-and-drop area with helpful text
5. User drags Excel file onto area (or clicks and browses)
6. File selected and filename appears
7. User clicks "Upload GSTR2B" button
8. Backend processes file, shows success
9. Interface advances to Step 3: Mismatch Detection

## 📞 Support Information

If you encounter issues:
1. Check the logs in both frontend and backend terminals
2. Review the error messages in browser console
3. Verify Excel file format and column names
4. Try with a simple test Excel file first
5. Check network tab for HTTP status codes

## ✅ Final Verification Checklist

- [ ] Frontend builds without TypeScript errors
- [ ] Backend starts without import errors
- [ ] Drag-and-drop visual feedback works
- [ ] File click selection works
- [ ] Valid Excel files accepted and parsed
- [ ] Invalid file types rejected with error
- [ ] Success message appears on upload
- [ ] Mismatch detection proceeds after upload
- [ ] No console errors in browser
- [ ] No errors in backend logs

---

**Ready to Test!** 🚀

Start the backend and frontend servers, then try uploading a GSTR2B Excel file.
