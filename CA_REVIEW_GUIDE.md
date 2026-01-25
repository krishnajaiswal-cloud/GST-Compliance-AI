# GST Reconciliation: CA Review & Action Items

## Executive Summary for CA

The system now provides **deterministic reconciliation** between:
- **Books**: Your client's purchase invoices (from bills/PDFs)
- **GSTR-2B**: GST Portal data (from GSTR-2B download)

### Key Features
✓ Automatic matching: Supplier GSTIN + Invoice Number + Document Type
✓ Mismatch detection: Amounts (1% tolerance), Tax structures, Dates (7 days)
✓ Actionable outcomes: Not guesses—deterministic rules with clear remediation paths
✓ Field-level tracking: Exactly which fields differ and by how much
✓ Summary reports: Reconciliation rates, issue counts, action priorities

---

## The Five Reconciliation Outcomes

### 1. ✅ MATCHED
**Meaning**: Exact match in both systems (or within tolerance)

**Probable Reason**: Normal matched invoice

**Your Action**: 
- ✓ Verify in your records (routine check)
- Accept for ITC claim or P&L
- No follow-up needed

**When This Happens**:
- All matching criteria met
- Amounts within 1% variance
- Tax structures consistent
- Date difference ≤ 7 days

---

### 2. ❌ MISSING IN GSTR-2B
**Meaning**: Invoice in client's books but NOT in GSTR-2B data

**Probable Reason**: 
- Supplier hasn't filed GSTR-1 yet (filing deadline: 11th of next month)
- Invoice issued after GSTR-2B data was downloaded
- Supplier filed under wrong GSTIN
- Inter-state supply with place of supply issue
- Supplier excluded from GST (unregistered, composition scheme)

**Your Action** (In Order of Priority):
1. **Confirm invoice date** - Is it recent? (GSTR-2B updates monthly)
2. **Verify supplier GSTIN** - Check GST registration status
3. **Contact supplier** - Ask if they filed GSTR-1
4. **Check place of supply** - For inter-state supplies
5. **Wait & reconcile later** - If filing was delayed, re-run reconciliation next month
6. **If nothing works** - Don't claim ITC; treat as regular purchase expense

**Deadline**: Typically resolve within 2 months

---

### 3. ❌ MISSING IN BOOKS
**Meaning**: Invoice in GSTR-2B but NOT in client's books

**Probable Reason**:
- Purchase not yet recorded in accounting system
- Invoice received but not yet matched to GR/receipt
- Duplicate entry (already recorded under different reference)
- Accounting entry pending (books not finalized)
- Debit note/Credit note not recorded

**Your Action** (In Order of Priority):
1. **Search accounting records** - By invoice number, date range, supplier name
2. **Check with warehouse/operations** - Was material received?
3. **Verify supplier details** - Is GSTIN identical in books vs portal?
4. **Ask client for GR (Goods Receipt)** - Match GSTR-2B to actual receipt
5. **If confirmed in warehouse** - Record the accounting entry
6. **If not confirmed** - Reject GSTR-2B invoice (may be duplicate or supply issue)

**Deadline**: Resolve before filing GSTR-3B (monthly)

---

### 4. ⚠️ VALUE MISMATCH
**Meaning**: Invoice matched, but amounts or taxes differ

**Probable Reason**:
- Supplier issued amendment/debit note
- Partial payment/discount applied
- Data entry error by supplier or your team
- Tax rate different in portal vs bill (GST rate change)
- Invoice partially received

**System Shows**:
- Which fields differ (Taxable Value, CGST, SGST, IGST)
- Exact difference amount
- Difference percentage (if >1%)

**Your Action** (In Order of Priority):
1. **Get original bill PDF** - Physical verification
2. **Check for amendments** - Any debit notes or credit notes?
3. **Verify tax rate** - Is 5%, 12%, 18%, or 28% correct?
4. **If supplier error** - Request corrected invoice
5. **If data entry error** - Correct your records
6. **If ITC differs** - File Form GSTR-1/Amendment if needed
7. **Document difference** - For audit trail

**Tolerance Allowed**: 1% variance (e.g., ₹100,000 → ₹101,000 is OK)

**Deadline**: Resolve before GSTR-3B filing

---

### 5. ⚠️ TAX STRUCTURE MISMATCH
**Meaning**: Same invoice, but tax components are different

**Example**:
- Your books: IGST ₹18,000 (inter-state supply)
- GSTR-2B: CGST ₹9,000 + SGST ₹9,000 (intra-state supply)

**Probable Reason**:
- Place of supply error
- Supplier filed with wrong state
- Inter-state vs Intra-state confusion
- Transaction location changed (reverse charge?)
- Supplier registered in multiple states

**Your Action** (CRITICAL - Legal Implications)**:
1. **Verify place of supply**
   - Where was the material delivered?
   - Where is the registered office?
   - Contract terms?
2. **Check reverse charge applicability**
   - Is this a reverse charge supply?
   - Should you be liable instead of supplier?
3. **Contact supplier**
   - Why is tax structure different?
   - Which is correct?
4. **Contact GST officer** (if unsure)
   - Place of supply interpretation
5. **Decide ITC claim**
   - Based on actual place of supply
   - Not what supplier filed (you're liable)

**Deadline**: URGENT - Impacts ITC eligibility and legal compliance

---

## Summary Statistics Explained

### Reconciliation Rate
```
✓ Matched: 800 invoices
✗ Total: 1000 invoices
= 80% Reconciliation Rate
```

**What it means**: 800 invoices are perfect matches or within tolerance.

**Benchmark**:
- 95%+ → Excellent (minor issues)
- 85-95% → Good (some follow-ups needed)
- 70-85% → Fair (systematic review recommended)
- <70% → Poor (detailed audit required)

### Issue Breakdown

```
Missing in GSTR-2B:      150 invoices
Missing in Books:         30 invoices
Value Mismatch:           15 invoices
Tax Structure Mismatch:    5 invoices
Invalid Data:              0 invoices
```

**Severity Priority**:
1. **RED** - Tax Structure Mismatch (legal risk)
2. **ORANGE** - Missing in GSTR-2B (ITC eligibility risk)
3. **YELLOW** - Value Mismatch (audit trail needed)
4. **BLUE** - Missing in Books (accounting correction)

---

## Recommended Workflow for CA

### Week 1: Data Preparation
- [ ] Client uploads all purchase bills (PDF/images)
- [ ] System extracts invoice data (Gemini AI)
- [ ] Client downloads Excel preview for verification
- [ ] Client corrects any mis-extracted data

### Week 2: GSTR-2B Upload
- [ ] Client exports GSTR-2B data from GST portal
- [ ] System parses GSTR-2B (Excel or CSV)
- [ ] System stores in session with extraction metadata

### Week 3: Run Reconciliation
- [ ] System executes deterministic matching
- [ ] Generates reconciliation report
- [ ] CA reviews outcomes by category

### Week 4: Follow-Up
- [ ] **RED Items**: Contact suppliers for legal clarification
- [ ] **ORANGE Items**: Wait for filing period or follow up
- [ ] **YELLOW Items**: Request corrected invoices
- [ ] **BLUE Items**: Record accounting entries

---

## Common Scenarios & Resolutions

### Scenario A: New Supplier (Invoice Not Yet in GSTR-2B)
```
Status: Missing in GSTR-2B
Invoice Date: 20-Jan-2025
GSTR-2B Downloaded: 02-Feb-2025
```
**Resolution**:
- Invoice issued after GSTR-2B download
- Supplier likely to file GSTR-1 by 11-Feb-2025
- Re-run reconciliation in March
- Temporarily don't claim ITC (or claim in next month)

### Scenario B: Amount Discrepancy
```
Books: Taxable ₹1,00,000 | CGST ₹9,000 | SGST ₹9,000
GSTR-2B: Taxable ₹99,000 | CGST ₹8,910 | SGST ₹8,910
Difference: -1% (within tolerance)
```
**Resolution**:
- Likely early payment discount (0.5% discount = -₹500)
- Check supplier invoice for discount terms
- Acceptable—claim full ITC

### Scenario C: Place of Supply Error
```
Books: IGST ₹18,000 (Delivered to Delhi)
GSTR-2B: CGST ₹9,000 + SGST ₹9,000
Supplier GSTIN State: Mumbai
```
**Resolution**:
- **Your invoice is correct** (place of supply = Delhi)
- Supplier filed wrong (should have charged IGST)
- Contact supplier for corrected invoice
- Claim IGST ITC based on your invoice
- File amendment to GSTR-1 if needed

### Scenario D: Duplicate Entry
```
Books: Invoice #INV001 and INV001-DUPLICATE both recorded
GSTR-2B: INV001 appears once
Status: Impossible to match (2 books invoices → 1 portal entry)
```
**Resolution**:
- Delete duplicate entry in books
- Re-run reconciliation
- Should now show as Matched

---

## Audit Trail for GST Officer

If GST officer questions your ITC claim:

1. **Show the reconciliation report** proving invoice was matched
2. **Show original bill PDF** (supporting document)
3. **Show GSTR-2B data** (what was in portal)
4. **Show reconciliation logic** (matching criteria)
5. **Explain any mismatches** (what action was taken)

**This establishes**: 
- Due diligence in verifying invoices
- Cross-checked against portal
- Followed GST best practices

---

## Red Flags for Investigation

🚩 **INVESTIGATE IF**:
- Tax Structure Mismatch → 10+ invoices (systematic supplier error)
- Same supplier → 50%+ invoices Missing in GSTR-2B (possible GSTIN issue)
- Same supplier → Consistent Value Mismatches (invoice template error)
- Unidentifiable invoices → >5% of total (potential fraud risk)

---

## Best Practices

✓ **DO**:
- Run reconciliation monthly (after GSTR-2B is available)
- Keep reconciliation reports as audit trail
- Follow up on RED items within 2 weeks
- Contact suppliers for missing/wrong invoices
- Document all follow-ups

✗ **DON'T**:
- Claim ITC for unmatched invoices without investigation
- Ignore Tax Structure Mismatches (legal liability)
- Wait more than 2 months to follow up
- Delete records of mismatches
- Assume supplier is always correct

---

## Integration with GST Compliance Calendar

```
Date               Action
---                ------
1-30 Jun           Purchase invoices received
01 Jul             GSTR-2B available (for Jun purchases)
02-15 Jul          Run reconciliation
15 Jul             Follow up on RED items
20 Jul             File GSTR-3B (using reconciled data)
25 Jul             Deadline for supplier amendments
01 Aug             GSTR-2B updated for late filings
05 Aug             Re-run reconciliation if needed
```

---

## Questions for System Validation

Before going live, verify with your technical team:

- [ ] System correctly identifies place of supply
- [ ] Tax structure validation catches IGST vs (CGST+SGST) mismatches
- [ ] Amount tolerance is exactly 1% (not more, not less)
- [ ] Date tolerance is 7 days (configurable if needed)
- [ ] "Matched" status only appears for actually matching invoices
- [ ] Field differences show exact amounts
- [ ] Summary statistics are accurate
- [ ] Excel export includes all matching criteria fields

---

## CA Sign-Off Checklist

- [ ] Reconciliation logic reviewed and approved
- [ ] Tolerance thresholds (1% amount, 7 days date) acceptable
- [ ] Action items clearly defined for each outcome
- [ ] Audit trail requirements met
- [ ] Report format suitable for GST officer review
- [ ] Data privacy/confidentiality verified
- [ ] Ready for production deployment

---

**Document Version**: 1.0
**Date**: January 24, 2025
**Prepared for**: CA/Compliance Team Review
**Status**: Ready for Validation
