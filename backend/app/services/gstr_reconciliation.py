from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from difflib import SequenceMatcher


class GSTRReconciliationEngine:
    """
    MVP GSTR-2B reconciliation engine for matching purchase invoices with GSTR-2B data.
    
    Provides deterministic, readable reconciliation logic with clear status,
    probable reasons, and action items for CA review.
    """
    
    def __init__(self):
        """Initialize reconciliation engine with tolerance settings"""
        # Tolerance for date comparison (days)
        self.date_tolerance_days = 7
        
        # Tolerance for amount comparison (percentage)
        self.amount_tolerance_percent = 1.0
        
        # Tolerance for tax components (percentage)
        self.tax_tolerance_percent = 1.0
    
    def reconcile(
        self,
        books_invoices: List[Dict],
        gstr2b_invoices: List[Dict]
    ) -> Dict:
        """
        Reconcile purchase invoices from books with GSTR-2B data.
        
        Args:
            books_invoices: List of extracted invoices from uploaded bills
            gstr2b_invoices: List of invoices from GSTR-2B portal
        
        Returns:
            Dictionary with reconciliation results and summary
        """
        reconciliation_results = []
        matched_gstr2b_indices = set()
        
        # Process each book invoice
        for books_invoice in books_invoices:
            # Skip invalid extractions
            if books_invoice.get("status") == "error" or not books_invoice.get("invoice_number"):
                reconciliation_results.append(
                    self._create_result(
                        books_invoice=books_invoice,
                        status="Invalid Data",
                        probable_reason="Extraction failed or missing invoice number",
                        action_required="Verify source document"
                    )
                )
                continue
            
            # Find matching GSTR-2B invoice
            match_result = self._find_match(books_invoice, gstr2b_invoices, matched_gstr2b_indices)
            
            if match_result["found"]:
                # Invoice exists in both books and GSTR-2B
                gstr2b_invoice = match_result["gstr2b_invoice"]
                matched_gstr2b_indices.add(match_result["index"])
                
                # Check for mismatches
                mismatch_analysis = self._analyze_mismatches(books_invoice, gstr2b_invoice)
                
                if mismatch_analysis["has_mismatches"]:
                    result = self._create_result(
                        books_invoice=books_invoice,
                        gstr2b_invoice=gstr2b_invoice,
                        status=mismatch_analysis["status"],
                        probable_reason=mismatch_analysis["probable_reason"],
                        action_required=mismatch_analysis["action_required"],
                        field_differences=mismatch_analysis["differences"]
                    )
                else:
                    result = self._create_result(
                        books_invoice=books_invoice,
                        gstr2b_invoice=gstr2b_invoice,
                        status="Matched",
                        probable_reason="Invoice details match GSTR-2B",
                        action_required="None - verified"
                    )
            else:
                # Invoice in books but not in GSTR-2B
                result = self._create_result(
                    books_invoice=books_invoice,
                    status="Missing in GSTR-2B",
                    probable_reason="Supplier may not have filed or filed after cutoff date",
                    action_required="Client/Supplier follow-up required"
                )
            
            reconciliation_results.append(result)
        
        # Find GSTR-2B invoices not in books
        unmatched_gstr2b_results = []
        for idx, gstr2b_invoice in enumerate(gstr2b_invoices):
            if idx not in matched_gstr2b_indices:
                result = self._create_result(
                    gstr2b_invoice=gstr2b_invoice,
                    status="Missing in Books",
                    probable_reason="Invoice not recorded by client or accounting delay",
                    action_required="Verify purchase register"
                )
                unmatched_gstr2b_results.append(result)
        
        # Generate summary
        summary = self._generate_summary(
            reconciliation_results,
            unmatched_gstr2b_results,
            len(books_invoices),
            len(gstr2b_invoices)
        )
        
        return {
            "status": "completed",
            "summary": summary,
            "books_reconciliation": reconciliation_results,
            "gstr2b_unmatched": unmatched_gstr2b_results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _find_match(
        self,
        books_invoice: Dict,
        gstr2b_invoices: List[Dict],
        matched_indices: set
    ) -> Dict:
        """
        Find matching GSTR-2B invoice using primary matching criteria.
        
        Primary match: supplier_gstin + invoice_no + document_type
        """
        books_gstin = self._normalize_gstin(books_invoice.get("supplier_gstin"))
        books_inv_no = self._normalize_string(books_invoice.get("invoice_number"))
        books_doc_type = self._normalize_string(books_invoice.get("document_type", "Invoice"))
        
        for idx, gstr2b_invoice in enumerate(gstr2b_invoices):
            if idx in matched_indices:
                continue
            
            gstr2b_gstin = self._normalize_gstin(gstr2b_invoice.get("supplier_gstin"))
            gstr2b_inv_no = self._normalize_string(gstr2b_invoice.get("invoice_number"))
            gstr2b_doc_type = self._normalize_string(gstr2b_invoice.get("document_type", "Invoice"))
            
            # Primary match criteria
            if (books_gstin == gstr2b_gstin and
                books_inv_no == gstr2b_inv_no and
                books_doc_type == gstr2b_doc_type):
                
                return {
                    "found": True,
                    "gstr2b_invoice": gstr2b_invoice,
                    "index": idx
                }
        
        return {"found": False}
    
    def _analyze_mismatches(self, books_invoice: Dict, gstr2b_invoice: Dict) -> Dict:
        """
        Analyze differences between matched invoices from books and GSTR-2B.
        """
        differences = {}
        has_mismatches = False
        
        # 1. Check amount mismatches
        amount_analysis = self._check_amounts(books_invoice, gstr2b_invoice)
        if amount_analysis["mismatch"]:
            has_mismatches = True
            differences["amount"] = amount_analysis
        
        # 2. Check tax structure mismatches
        tax_structure_analysis = self._check_tax_structure(books_invoice, gstr2b_invoice)
        if tax_structure_analysis["mismatch"]:
            has_mismatches = True
            differences["tax_structure"] = tax_structure_analysis
        
        # 3. Check date mismatch (non-critical)
        date_analysis = self._check_dates(books_invoice, gstr2b_invoice)
        if date_analysis["mismatch"]:
            differences["date"] = date_analysis
        
        # Determine status and actions
        if tax_structure_analysis["mismatch"]:
            status = "Tax Structure Mismatch"
            probable_reason = "Wrong tax type charged (place of supply issue)"
            action_required = "Legal review / supplier correction required"
        elif amount_analysis["mismatch"]:
            status = "Value Mismatch"
            probable_reason = "Supplier amendment or data entry error"
            action_required = "Verify invoice copy"
        else:
            status = "Matched"
            probable_reason = "Invoice details match GSTR-2B"
            action_required = "None - verified"
        
        return {
            "has_mismatches": has_mismatches,
            "status": status,
            "probable_reason": probable_reason,
            "action_required": action_required,
            "differences": differences
        }
    
    def _check_amounts(self, books_invoice: Dict, gstr2b_invoice: Dict) -> Dict:
        """
        Check if taxable value and tax components match within tolerance.
        """
        mismatch = False
        details = {}
        
        # Check taxable value
        books_taxable = self._get_numeric(books_invoice.get("taxable_value"))
        gstr2b_taxable = self._get_numeric(gstr2b_invoice.get("taxable_value"))
        
        if books_taxable is not None and gstr2b_taxable is not None:
            if not self._within_tolerance(books_taxable, gstr2b_taxable, self.amount_tolerance_percent):
                mismatch = True
                details["taxable_value"] = {
                    "books": books_taxable,
                    "gstr2b": gstr2b_taxable,
                    "difference": books_taxable - gstr2b_taxable,
                    "difference_percent": ((books_taxable - gstr2b_taxable) / gstr2b_taxable * 100) if gstr2b_taxable else 0
                }
        
        # Check tax components (CGST, SGST, IGST)
        for tax_type in ["cgst", "sgst", "igst"]:
            books_tax = self._get_numeric(books_invoice.get(tax_type))
            gstr2b_tax = self._get_numeric(gstr2b_invoice.get(tax_type))
            
            if books_tax is not None and gstr2b_tax is not None:
                if not self._within_tolerance(books_tax, gstr2b_tax, self.tax_tolerance_percent):
                    mismatch = True
                    details[tax_type] = {
                        "books": books_tax,
                        "gstr2b": gstr2b_tax,
                        "difference": books_tax - gstr2b_tax,
                        "difference_percent": ((books_tax - gstr2b_tax) / gstr2b_tax * 100) if gstr2b_tax else 0
                    }
        
        return {
            "mismatch": mismatch,
            "details": details
        }
    
    def _check_tax_structure(self, books_invoice: Dict, gstr2b_invoice: Dict) -> Dict:
        """
        Check if tax structure is consistent (IGST vs CGST+SGST).
        """
        # Determine tax structure in books
        books_igst = self._get_numeric(books_invoice.get("igst"))
        books_cgst = self._get_numeric(books_invoice.get("cgst"))
        books_sgst = self._get_numeric(books_invoice.get("sgst"))
        
        books_uses_igst = (books_igst is not None and books_igst > 0)
        books_uses_state_tax = ((books_cgst is not None and books_cgst > 0) or
                               (books_sgst is not None and books_sgst > 0))
        
        # Determine tax structure in GSTR-2B
        gstr2b_igst = self._get_numeric(gstr2b_invoice.get("igst"))
        gstr2b_cgst = self._get_numeric(gstr2b_invoice.get("cgst"))
        gstr2b_sgst = self._get_numeric(gstr2b_invoice.get("sgst"))
        
        gstr2b_uses_igst = (gstr2b_igst is not None and gstr2b_igst > 0)
        gstr2b_uses_state_tax = ((gstr2b_cgst is not None and gstr2b_cgst > 0) or
                                (gstr2b_sgst is not None and gstr2b_sgst > 0))
        
        # Check for mismatch
        mismatch = (books_uses_igst != gstr2b_uses_igst)
        
        return {
            "mismatch": mismatch,
            "books_structure": "IGST" if books_uses_igst else "CGST+SGST" if books_uses_state_tax else "None",
            "gstr2b_structure": "IGST" if gstr2b_uses_igst else "CGST+SGST" if gstr2b_uses_state_tax else "None"
        }
    
    def _check_dates(self, books_invoice: Dict, gstr2b_invoice: Dict) -> Dict:
        """
        Check if invoice dates match within tolerance.
        Non-critical mismatch.
        """
        books_date = self._parse_date(books_invoice.get("invoice_date"))
        gstr2b_date = self._parse_date(gstr2b_invoice.get("invoice_date"))
        
        mismatch = False
        difference_days = None
        
        if books_date and gstr2b_date:
            difference_days = abs((books_date - gstr2b_date).days)
            mismatch = difference_days > self.date_tolerance_days
        
        return {
            "mismatch": mismatch,
            "books_date": books_invoice.get("invoice_date"),
            "gstr2b_date": gstr2b_invoice.get("invoice_date"),
            "difference_days": difference_days,
            "note": "Non-critical mismatch - common due to filing delays"
        }
    
    def _create_result(
        self,
        books_invoice: Optional[Dict] = None,
        gstr2b_invoice: Optional[Dict] = None,
        status: str = "",
        probable_reason: str = "",
        action_required: str = "",
        field_differences: Optional[Dict] = None
    ) -> Dict:
        """
        Create standardized reconciliation result.
        """
        return {
            "books_invoice_number": books_invoice.get("invoice_number") if books_invoice else "N/A",
            "gstr2b_invoice_number": gstr2b_invoice.get("invoice_number") if gstr2b_invoice else "N/A",
            "supplier_gstin": (books_invoice.get("supplier_gstin") or gstr2b_invoice.get("supplier_gstin")) if (books_invoice or gstr2b_invoice) else "N/A",
            "status": status,
            "probable_reason": probable_reason,
            "action_required": action_required,
            "field_differences": field_differences or {},
            "books_data": self._sanitize_invoice(books_invoice) if books_invoice else None,
            "gstr2b_data": self._sanitize_invoice(gstr2b_invoice) if gstr2b_invoice else None
        }
    
    def _generate_summary(
        self,
        books_results: List[Dict],
        gstr2b_unmatched: List[Dict],
        total_books: int,
        total_gstr2b: int
    ) -> Dict:
        """
        Generate reconciliation summary statistics.
        """
        status_counts = {}
        for result in books_results:
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        matched_count = status_counts.get("Matched", 0)
        value_mismatches = status_counts.get("Value Mismatch", 0)
        tax_mismatches = status_counts.get("Tax Structure Mismatch", 0)
        missing_in_gstr2b = status_counts.get("Missing in GSTR-2B", 0)
        missing_in_books = len(gstr2b_unmatched)
        
        return {
            "total_books_invoices": total_books,
            "total_gstr2b_invoices": total_gstr2b,
            "matched": matched_count,
            "value_mismatches": value_mismatches,
            "tax_structure_mismatches": tax_mismatches,
            "missing_in_gstr2b": missing_in_gstr2b,
            "missing_in_books": missing_in_books,
            "invalid_extractions": status_counts.get("Invalid Data", 0),
            "reconciliation_rate": f"{(matched_count / total_books * 100):.1f}%" if total_books > 0 else "0%",
            "status_breakdown": status_counts
        }
    
    # Utility methods
    
    @staticmethod
    def _normalize_gstin(gstin: Optional[str]) -> str:
        """Normalize GSTIN for comparison."""
        if not gstin:
            return ""
        return str(gstin).strip().upper()
    
    @staticmethod
    def _normalize_string(value: Optional[str]) -> str:
        """Normalize string for comparison."""
        if not value:
            return ""
        return str(value).strip().upper()
    
    @staticmethod
    def _get_numeric(value) -> Optional[float]:
        """Safely extract numeric value."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _within_tolerance(value1: float, value2: float, tolerance_percent: float) -> bool:
        """Check if two values are within tolerance."""
        if value2 == 0:
            return value1 == 0
        
        difference_percent = abs((value1 - value2) / value2 * 100)
        return difference_percent <= tolerance_percent
    
    @staticmethod
    def _parse_date(date_string: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_string:
            return None
        
        formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_string).strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    @staticmethod
    def _sanitize_invoice(invoice: Optional[Dict]) -> Optional[Dict]:
        """Remove sensitive data before returning."""
        if not invoice:
            return None
        
        sanitized = {
            "invoice_number": invoice.get("invoice_number"),
            "invoice_date": invoice.get("invoice_date"),
            "supplier_gstin": invoice.get("supplier_gstin"),
            "document_type": invoice.get("document_type"),
            "taxable_value": invoice.get("taxable_value"),
            "cgst": invoice.get("cgst"),
            "sgst": invoice.get("sgst"),
            "igst": invoice.get("igst"),
            "total_amount": invoice.get("total_amount"),
            "gstr2b_section": invoice.get("gstr2b_section"),
            "itc_eligibility": invoice.get("itc_eligibility")
        }
        
        return sanitized
