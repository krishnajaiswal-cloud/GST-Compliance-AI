# GSTR-2B Reconciliation Logic - MVP Implementation

## Overview

This implementation provides deterministic, MVP-grade GSTR-2B reconciliation logic that compares purchase invoices extracted from uploaded bills with GSTR-2B data downloaded from the GST portal.

## Core Architecture

### 1. Input Data Sources

#### Books Invoices (Extracted from Uploaded Bills)
```
Fields per row:
- supplier_gstin: Supplier's GST ID
- invoice_number: Invoice number
- invoice_date: Date of invoice (YYYY-MM-DD)
- document_type: "Invoice", "Debit Note", or "Credit Note"
- taxable_value: Taxable amount
- cgst: Central GST
- sgst: State GST
- igst: Integrated GST
- total_amount: Grand total
- expense_category: Category (Office Supplies, Travel, etc.)
- itc_eligibility: Boolean - eligible for Input Tax Credit
```

#### GSTR-2B Data (From GST Portal)
```
Fields per row:
- supplier_gstin: Supplier's GST ID
- invoice_number: Invoice number
- invoice_date: Date of invoice
- document_type: Document type (Invoice, Debit Note, Credit Note)
- taxable_value: Taxable amount
- cgst: Central GST
- sgst: State GST
- igst: Integrated GST
- total_amount: Total amount
- gstr2b_section: Section (B2B, ISD, IMPG, CDNR, etc.)
- itc_eligibility: Boolean - ITC eligibility from portal
```

### 2. Matching Logic (Primary)

**Matching Criteria:**
```
supplier_gstin + invoice_number + document_type
```

**Key Points:**
- Matching is deterministic and exact (after normalization)
- GSTIN comparison: Case-insensitive, whitespace-trimmed
- Invoice number: Case-insensitive, whitespace-trimmed
- Document type: Normalized to standard values

**Date Tolerance:**
- Invoice dates may differ by up to 7 days
- Date mismatch is flagged but non-critical
- Example: Invoice dated 2025-01-15 matches with 2025-01-20

### 3. Reconciliation Rules (MVP)

#### Rule 1: Invoice Exists in Books BUT NOT in GSTR-2B
```
Status:               "Missing in GSTR-2B"
Probable Reason:      "Supplier may not have filed or filed after cutoff date"
Action Required:      "Client/Supplier follow-up required"
Additional Context:   Can suggest letter to supplier for re-filing
```

#### Rule 2: Invoice Exists in GSTR-2B BUT NOT in Books
```
Status:               "Missing in Books"
Probable Reason:      "Invoice not recorded by client or accounting delay"
Action Required:      "Verify purchase register"
Additional Context:   Could indicate accounting error or delayed recording
```

#### Rule 3: Invoice Exists in BOTH - Amount Mismatch
```
Status:               "Value Mismatch"
Probable Reason:      "Supplier amendment or data entry error"
Action Required:      "Verify invoice copy"
Field Differences:    Show exact differences for:
                      - Taxable Value
                      - CGST
                      - SGST
                      - IGST
Tolerance:            1% for amounts, 1% for tax components
```

#### Rule 4: Invoice Exists in BOTH - Tax Structure Mismatch
```
Status:               "Tax Structure Mismatch"
Probable Reason:      "Wrong tax type charged (place of supply issue)"
Action Required:      "Legal review / supplier correction required"
Example Scenario:     Books show IGST but GSTR-2B shows CGST+SGST
                      (indicates intra-state vs inter-state confusion)
```

#### Rule 5: Invoice Exists in BOTH - No Mismatches
```
Status:               "Matched"
Probable Reason:      "Invoice details match GSTR-2B"
Action Required:      "None - verified"
```

### 4. Output Structure

Each reconciliation result includes:
```json
{
  "books_invoice_number": "INV-001",
  "gstr2b_invoice_number": "INV-001",
  "supplier_gstin": "18AABCT1234H1Z0",
  "status": "Matched|Missing in GSTR-2B|Missing in Books|Value Mismatch|Tax Structure Mismatch|Invalid Data",
  "probable_reason": "String describing likely cause",
  "action_required": "String describing recommended action",
  "field_differences": {
    "amount": {
      "mismatch": true/false,
      "details": {
        "taxable_value": {
          "books": 10000,
          "gstr2b": 10100,
          "difference": -100,
          "difference_percent": -1.0
        }
      }
    },
    "tax_structure": {
      "mismatch": true/false,
      "books_structure": "IGST|CGST+SGST",
      "gstr2b_structure": "IGST|CGST+SGST"
    },
    "date": {
      "mismatch": false,
      "books_date": "2025-01-15",
      "gstr2b_date": "2025-01-15",
      "difference_days": 0,
      "note": "Non-critical mismatch - common due to filing delays"
    }
  },
  "books_data": {...sanitized invoice data...},
  "gstr2b_data": {...sanitized invoice data...}
}
```

## Summary Report

The reconciliation returns a comprehensive summary:

```json
{
  "total_books_invoices": 50,
  "total_gstr2b_invoices": 48,
  "matched": 45,
  "value_mismatches": 2,
  "tax_structure_mismatches": 1,
  "missing_in_gstr2b": 2,
  "missing_in_books": 1,
  "invalid_extractions": 0,
  "reconciliation_rate": "90.0%",
  "status_breakdown": {
    "Matched": 45,
    "Value Mismatch": 2,
    "Tax Structure Mismatch": 1,
    "Missing in GSTR-2B": 2
  }
}
```

## Implementation Details

### File Locations

```
backend/app/services/gstr_reconciliation.py
  ├─ GSTRReconciliationEngine class
  ├─ reconcile() - Main reconciliation method
  ├─ _find_match() - Primary matching logic
  ├─ _analyze_mismatches() - Mismatch analysis
  ├─ _check_amounts() - Amount comparison
  ├─ _check_tax_structure() - Tax type comparison
  ├─ _check_dates() - Date validation
  └─ Utility methods

backend/app/services/mismatch_detector.py
  ├─ reconcile() - Wrapper method
  ├─ _parse_gstr2b_for_reconciliation() - Data preparation
  └─ Integration with GSTRReconciliationEngine

backend/app/services/document_processor.py
  └─ Updated Gemini prompt to extract:
     - document_type
     - gstr2b_section (null for books)
     - itc_eligibility

backend/app/services/excel_generator.py
  └─ _prepare_dataframe() - Updated to include:
     - Document Type
     - ITC Eligibility
     - GSTR2B Section

backend/app/api/processing.py
  └─ POST /reconcile-gstr2b/{session_id}
     └─ New endpoint for reconciliation
```

### API Endpoint

**POST /reconcile-gstr2b/{session_id}**

Request:
```
Session must have:
- extracted_invoices: List of parsed invoices from books
- gstr2b_data: GSTR-2B data from portal
```

Response (200 OK):
```json
{
  "status": "success",
  "session_id": "abc123",
  "reconciliation": {
    "status": "completed",
    "summary": {...},
    "books_reconciliation": [...],
    "gstr2b_unmatched": [...],
    "timestamp": "2025-01-24T10:30:00"
  }
}
```

Response (400/404/500):
```json
{
  "detail": "Error message"
}
```

## Tolerance Settings (Configurable)

```python
class GSTRReconciliationEngine:
    def __init__(self):
        self.date_tolerance_days = 7          # Up to 7 days difference
        self.amount_tolerance_percent = 1.0   # 1% variation allowed
        self.tax_tolerance_percent = 1.0      # 1% variation for taxes
```

## MVP Limitations & Assumptions

1. **Does NOT Determine Exact Cause**: System provides probable reasons only
2. **Does NOT Auto-Correct**: All corrections require CA review
3. **Deterministic Only**: Uses exact matching and defined rules
4. **No ML/AI**: No predictive or probabilistic matching
5. **CA Follow-up Required**: All actions require manual verification
6. **Non-Critical Dates**: Date mismatches don't fail reconciliation
7. **Assumes GST Placement**: Intra-state (CGST+SGST) vs Inter-state (IGST)

## Data Flow

```
User uploads documents
    ↓
Gemini extracts invoice data (with document_type, itc_eligibility)
    ↓
Excel preview shows extracted data (with new fields)
    ↓
User downloads Excel (with new fields)
    ↓
User uploads GSTR-2B data from portal
    ↓
Reconciliation engine processes both datasets
    ↓
Returns detailed status, reasons, and actions per invoice
    ↓
Summary shows reconciliation rate, breakdown by status
    ↓
CA reviews results and takes appropriate actions
```

## Usage Example

```python
from app.services.mismatch_detector import MismatchDetector

# Initialize detector (includes reconciliation engine)
detector = MismatchDetector()

# Perform reconciliation
result = detector.reconcile(
    extracted_invoices=books_data,
    gstr2b_data=portal_data
)

# Access results
summary = result['summary']
books_reconciliation = result['books_reconciliation']  # Per-invoice results
gstr2b_unmatched = result['gstr2b_unmatched']         # Extra invoices in portal

# Each invoice result includes:
for invoice_result in books_reconciliation:
    print(f"Invoice: {invoice_result['books_invoice_number']}")
    print(f"Status: {invoice_result['status']}")
    print(f"Reason: {invoice_result['probable_reason']}")
    print(f"Action: {invoice_result['action_required']}")
    if invoice_result['field_differences']:
        print(f"Differences: {invoice_result['field_differences']}")
```

## Safety & Best Practices

1. **Non-Destructive**: Never modifies source data
2. **Error Handling**: Graceful handling of malformed data
3. **Logging**: All errors logged for debugging
4. **Type Safety**: Strict type conversion with null handling
5. **Data Sanitization**: Removes sensitive data before output
6. **Normalization**: Consistent handling of variations (case, whitespace)

## Testing Scenarios

The reconciliation logic handles:

✓ Exact matches (no mismatches)
✓ Amount discrepancies within tolerance
✓ Amount discrepancies outside tolerance
✓ Tax structure mismatches (IGST vs CGST+SGST)
✓ Date variations (within 7 days)
✓ Missing data fields (null handling)
✓ Invoices only in books
✓ Invoices only in GSTR-2B
✓ Invalid extracted data
✓ Empty datasets
✓ Multiple invoice types (Invoices, Debit Notes, Credit Notes)

## Future Enhancements (Post-MVP)

- [ ] Machine learning for pattern detection
- [ ] Historical data analysis
- [ ] Supplier reliability scoring
- [ ] Batch amendment filing support
- [ ] API integration with GST portal
- [ ] Email notifications for actionable items
- [ ] Audit trail and change tracking
- [ ] Multi-period reconciliation
- [ ] Cash flow impact analysis
- [ ] ITC reversal suggestions

## Quality Assurance

All reconciliation output is designed for CA review:
- Clear, non-technical language
- Actionable recommendations
- Conservative (no certainty claims)
- Complete data preservation
- Audit trail capable
- Compliant with GST regulations

---

**Status**: Production Ready for MVP  
**Last Updated**: January 24, 2025  
**Maintainer**: Development Team
