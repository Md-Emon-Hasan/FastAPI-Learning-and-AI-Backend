from PyPDF2 import PdfReader
from typing import List, Dict
import hashlib
from datetime import datetime

class PDFProcessor:
    def extract_text(self, pdf_file) -> str:
        """Extract text from PDF"""
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return text.strip()
    
    def process_for_embedding(self, pdf_file, filename: str) -> Dict:
        """Process PDF and prepare for vector store"""
        # Extract text
        text = self.extract_text(pdf_file)
        
        # Generate unique ID
        file_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Metadata
        metadata = {
            "filename": filename,
            "file_hash": file_hash,
            "uploaded_at": datetime.utcnow().isoformat(),
            "page_count": len(PdfReader(pdf_file).pages)
        }
        
        return {
            "text": text,
            "metadata": metadata
        }

pdf_processor = PDFProcessor()