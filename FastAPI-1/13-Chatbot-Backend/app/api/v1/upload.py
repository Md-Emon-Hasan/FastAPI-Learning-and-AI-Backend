from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException
from app.api.deps import get_current_user
from app.db.models import User
from app.tasks.background import process_pdf_background
from app.services.pdf_processor import pdf_processor
from app.db.vector_store import vector_store
import shutil
import os
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    background: bool = False,
    current_user: User = Depends(get_current_user)
):
    """
    Upload PDF and process for RAG
    - Extracts text from PDF
    - Chunks and embeds content
    - Adds to vector store
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    try:
        # Save file temporarily
        file_path = UPLOAD_DIR / f"{current_user.id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        if background:
            # Process in background
            background_tasks.add_task(
                process_pdf_background,
                str(file_path),
                file.filename,
                current_user.id
            )
            return {
                "status": "processing",
                "message": "PDF upload started in background",
                "filename": file.filename
            }
        else:
            # Process immediately
            with open(file_path, 'rb') as f:
                result = pdf_processor.process_for_embedding(f, file.filename)
            
            # Add to vector store
            chunks = vector_store.add_documents(
                texts=[result["text"]],
                metadatas=[result["metadata"]]
            )
            
            # Clean up
            os.remove(file_path)
            
            return {
                "status": "completed",
                "message": "PDF processed successfully",
                "filename": file.filename,
                "chunks_created": chunks,
                "metadata": result["metadata"]
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")

@router.get("/documents/search")
async def search_documents(
    query: str,
    k: int = 5,
    current_user: User = Depends(get_current_user)
):
    """Search similar documents in vector store"""
    try:
        results = vector_store.similarity_search(query, k=k)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))