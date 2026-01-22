import pdfplumber
from typing import List, Dict
import re

class PDFProcessor:
    """
    PDF processing service
    
    Features:
    - Text extraction
    - Smart chunking (overlap support)
    - Metadata extraction
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlapping characters between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text(self, pdf_path: str) -> str:
        """
        PDF থেকে সব text extract করবে
        
        Returns: Full text content
        """
        text_parts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    def extract_with_metadata(self, pdf_path: str) -> Dict:
        """
        Text + metadata extract করবে
        
        Returns: {
            "text": "...",
            "metadata": {"pages": 10, "title": "..."}
        }
        """
        text_parts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            # Extract text
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            # Extract metadata
            metadata = {
                "pages": len(pdf.pages),
                "metadata": pdf.metadata or {}
            }
        
        return {
            "text": "\n\n".join(text_parts),
            "metadata": metadata
        }
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Long text কে smaller chunks এ ভাগ করবে
        
        Chunking strategy:
        - Split by sentences (preserve meaning)
        - Maintain overlap (context preservation)
        - Max chunk_size characters
        
        Returns: List of text chunks
        """
        # Clean text
        text = self._clean_text(text)
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # যদি current chunk + sentence > chunk_size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Current chunk save করবো
                chunks.append(" ".join(current_chunk))
                
                # Overlap maintain করার জন্য শেষের কিছু sentences রাখবো
                overlap_text = " ".join(current_chunk)
                overlap_sentences = []
                overlap_length = 0
                
                # শেষ থেকে sentences নেবো যতক্ষণ overlap_length < chunk_overlap
                for s in reversed(current_chunk):
                    if overlap_length + len(s) <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_length += len(s)
                    else:
                        break
                
                # নতুন chunk overlap দিয়ে শুরু করবো
                current_chunk = overlap_sentences
                current_length = overlap_length
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # শেষ chunk add করবো
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Text clean করবে"""
        # Multiple spaces/newlines কে single space এ convert করবে
        text = re.sub(r'\s+', ' ', text)
        
        # Leading/trailing whitespace remove করবে
        text = text.strip()
        
        return text
    
    def process_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Complete PDF processing pipeline
        
        Returns: List of chunks with metadata
        [
            {
                "text": "chunk 1",
                "metadata": {"chunk_id": 0, "source": "file.pdf"}
            },
            ...
        ]
        """
        # Extract text and metadata
        result = self.extract_with_metadata(pdf_path)
        text = result["text"]
        pdf_metadata = result["metadata"]
        
        # Chunk করবে
        chunks = self.chunk_text(text)
        
        # Metadata attach করবে
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                "text": chunk,
                "metadata": {
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    "source": pdf_path,
                    **pdf_metadata
                }
            })
        
        return processed_chunks

# Singleton instance
pdf_processor = PDFProcessor()