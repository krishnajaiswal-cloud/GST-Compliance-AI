import os
import json
import base64
from typing import List, Dict, Optional
from google import genai
import pytesseract
from PIL import Image
import PyPDF2
from pdf2image import convert_from_path
from pathlib import Path

class DocumentProcessor:
    """Handles OCR extraction and Gemini AI processing of documents"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
    
    async def process_documents(self, file_paths: List[str], progress_callback=None) -> Dict:
        """
        Process multiple documents and extract invoice data using OCR and Gemini
        
        Args:
            file_paths: List of file paths to process
            progress_callback: Async callback for progress updates
        
        Returns:
            Dictionary with extracted invoice data and metadata
        """
        extracted_data = []
        total_files = len(file_paths)
        
        for index, file_path in enumerate(file_paths):
            try:
                # Update progress
                if progress_callback:
                    await progress_callback({
                        "step": "extraction",
                        "current": index + 1,
                        "total": total_files,
                        "status": f"Processing {os.path.basename(file_path)}..."
                    })
                
                # Extract text from file
                text = await self._extract_text_from_file(file_path)
                
                # Use Gemini to structure the data
                if self.client and text:
                    structured_data = await self._extract_structured_data(text, os.path.basename(file_path))
                    extracted_data.append(structured_data)
                else:
                    # Fallback if Gemini not available
                    extracted_data.append({
                        "file": os.path.basename(file_path),
                        "raw_text": text,
                        "invoice_number": "UNKNOWN",
                        "invoice_date": "UNKNOWN",
                        "gstin": "UNKNOWN",
                        "amount": 0.0,
                        "status": "pending_review"
                    })
                
            except Exception as e:
                extracted_data.append({
                    "file": os.path.basename(file_path),
                    "error": str(e),
                    "status": "error"
                })
        
        return {
            "status": "completed",
            "total_processed": len(extracted_data),
            "invoices": extracted_data
        }
    
    async def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from PDF or image file"""
        file_ext = Path(file_path).suffix.lower()
        text = ""
        
        try:
            if file_ext == ".pdf":
                text = await self._extract_text_from_pdf(file_path)
            elif file_ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
                text = await self._extract_text_from_image(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            text = ""
        
        return text
    
    async def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using OCR"""
        text = ""
        
        try:
            # Try direct text extraction first
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            
            # If minimal text extracted, use OCR
            if len(text.strip()) < 100:
                images = convert_from_path(pdf_path, dpi=300)
                for image in images:
                    text += pytesseract.image_to_string(image) + "\n"
        
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            text = ""
        
        return text
    
    async def _extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
    
    async def _extract_structured_data(self, text: str, filename: str) -> Dict:
        """Use Gemini to extract structured invoice data from text"""
        try:
            prompt = f"""
                Extract structured purchase invoice data from the following text.

                Return a SINGLE JSON object with EXACTLY these fields:

                - supplier_gstin (string or null)
                - invoice_number (string or null)
                - invoice_date (string in YYYY-MM-DD format or null)
                - document_type (string: "Invoice", "Debit Note", or "Credit Note", or null)

                - taxable_value (number or null)
                - cgst (number or null)
                - sgst (number or null)
                - igst (number or null)

                - invoice_amount (number or null)
                - tax_amount (number or null)
                - total_amount (number or null)

                - expense_category (string or null)
                (Examples: Office Supplies, Travel, Food & Beverages, Software, Machinery, Raw Material, Rent, Utilities, Professional Fees)

                - gstr2b_section (string: "B2B", "ISD", "IMPG", "CDNR" or null - use null for books data as this is GSTR-2B specific)
                - itc_eligibility (boolean or null - true if eligible for ITC, null if unknown)

                - items (array of objects with:
                    description (string),
                    quantity (number or null),
                    rate (number or null),
                    amount (number or null)
                )

                - status (string: "valid", "partial", or "invalid")

                Rules:
                - If a field cannot be determined, use null
                - CGST + SGST should be used for intra-state invoices
                - IGST should be used for inter-state invoices
                - document_type: Try to detect if it's a regular invoice, debit note, or credit note
                - gstr2b_section: Leave as null (for extraction from bills, not GSTR-2B)
                - itc_eligibility: Determine from invoice content if possible
                - Return ONLY valid JSON
                - No markdown
                - No explanations

                TEXT:
                {text[:4000]}
                """

            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            response_text = response.text.strip()
            
            # Clean up response if it has markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response_text)
            data["file"] = filename
            data["raw_text_preview"] = text[:500]
            
            return data
            
        except json.JSONDecodeError as e:
            return {
                "file": filename,
                "error": f"Failed to parse Gemini response: {str(e)}",
                "status": "error"
            }
        except Exception as e:
            return {
                "file": filename,
                "error": str(e),
                "status": "error"
            }
    
    async def validate_gstr2b_data(self, gstr2b_data: Dict) -> Dict:
        """
        Validate and structure GSTR2B data
        """
        try:
            # Check for required invoices field (others can have defaults)
            if "invoices" not in gstr2b_data or not gstr2b_data["invoices"]:
                return {
                    "valid": False,
                    "message": "No invoices found in GSTR2B data. Please ensure the Excel file contains invoice records."
                }
            
            # Provide defaults for optional fields
            if not gstr2b_data.get("period"):
                gstr2b_data["period"] = "Unknown"
            if not gstr2b_data.get("gstin"):
                gstr2b_data["gstin"] = "Not provided"
            
            return {
                "valid": True,
                "message": "GSTR2B data is valid",
                "data": gstr2b_data
            }
        except Exception as e:
            return {
                "valid": False,
                "message": str(e)
            }
