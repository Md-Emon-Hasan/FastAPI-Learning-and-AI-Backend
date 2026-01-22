from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import os
import shutil
from datetime import datetime

from app.core.database import get_db
from app.core.config import get_settings
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.conversation import Document
from app.schemas.schemas import DocumentUpload, DocumentResponse
from app.services.pdf_processor import pdf_processor
from app.services.vector_db import vector_store

settings = get_settings()
router = APIRouter(prefix="/upload", tags=["File Upload"])

async def process_pdf_background(
    document_id: int,
    filepath: str,
    db: AsyncSession
):
    """
    Background task - PDF processing করবে
    
    Steps:
    1. PDF থেকে text extract করবে
    2. Text chunks এ ভাগ করবে
    3. Embeddings generate করবে
    4. Vector DB তে store করবে
    5. Document status update করবে
    """
    try:
        # Update status to processing
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one()
        document.status = "processing"
        await db.commit()
        
        # Process PDF
        chunks = pdf_processor.process_pdf(filepath)
        
        # Prepare data for vector store
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                **chunk["metadata"],
                "document_id": document_id,
                "user_id": document.user_id
            }
            for chunk in chunks
        ]
        ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Add to vector store
        vector_ids = vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        # Save vector store
        vector_store.save(settings.VECTOR_DB_PATH)
        
        # Update document
        document.status = "completed"
        document.vector_ids = vector_ids
        document.chunk_count = len(chunks)
        document.processed_at = datetime.utcnow()
        await db.commit()
        
    except Exception as e:
        # Update status to failed
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one()
        document.status = "failed"
        document.metadata = {"error": str(e)}
        await db.commit()

@router.post("/pdf", response_model=DocumentUpload, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    PDF upload করবে এবং background এ process করবে
    
    Process:
    1. File validate করবে
    2. File save করবে
    3. Database entry তৈরি করবে
    4. Background task schedule করবে
    """
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Go to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{current_user.id}_{timestamp}_{file.filename}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    # Save file
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create database entry
    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        filepath=filepath,
        file_type="pdf",
        file_size=file_size,
        status="pending"
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    # Schedule background processing
    # FastAPI BackgroundTasks automatically handles async
    background_tasks.add_task(
        process_pdf_background,
        document.id,
        filepath,
        db
    )
    
    return document

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: str = None
):
    """User এর uploaded documents list করবে"""
    query = select(Document).where(Document.user_id == current_user.id)
    
    if status_filter:
        query = query.where(Document.status == status_filter)
    
    result = await db.execute(query.order_by(Document.created_at.desc()))
    documents = result.scalars().all()
    
    return documents

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Specific document এর details"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Document delete করবে
    - Database entry delete করবে
    - File delete করবে
    - Vector DB থেকে embeddings delete করবে
    """
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file
    if os.path.exists(document.filepath):
        os.remove(document.filepath)
    
    # Delete from vector store
    if document.vector_ids:
        chunk_ids = [f"doc_{document_id}_chunk_{i}" for i in range(document.chunk_count)]
        vector_store.delete_by_ids(chunk_ids)
        vector_store.save(settings.VECTOR_DB_PATH)
    
    # Delete from database
    await db.delete(document)
    await db.commit()
    
    return {"message": "Document deleted successfully"}

@router.post("/search")
async def search_documents(
    query: str,
    current_user: User = Depends(get_current_user),
    k: int = 5
):
    """
    Semantic search - Uploaded PDFs এ search করবে
    
    Returns: Relevant chunks from documents
    """
    
    # Vector search করবে (user এর documents এ filter করবে)
    results = vector_store.similarity_search(
        query=query,
        k=k,
        filter_metadata={"user_id": current_user.id}
    )
    
    # Format results
    formatted_results = []
    for text, score, metadata in results:
        formatted_results.append({
            "text": text,
            "score": score,
            "document_id": metadata.get("document_id"),
            "chunk_id": metadata.get("chunk_id"),
            "source": metadata.get("source")
        })
    
    return {
        "query": query,
        "results": formatted_results
    }

@router.post("/chat-with-docs")
async def chat_with_documents(
    query: str,
    current_user: User = Depends(get_current_user),
    k: int = 3
):
    """
    RAG - Documents এর context সহ chat করবে
    
    Process:
    1. Semantic search করবে
    2. Relevant chunks fetch করবে
    3. LLM কে context দিয়ে query করবে
    """
    from app.services.llm import llm_service
    
    # Search relevant chunks
    results = vector_store.similarity_search(
        query=query,
        k=k,
        filter_metadata={"user_id": current_user.id}
    )
    
    if not results:
        return {
            "answer": "No relevant documents found. Please upload PDFs first.",
            "sources": []
        }
    
    # Build context from chunks
    context = "\n\n".join([text for text, _, _ in results])
    
    # Build prompt
    system_prompt = """You are a helpful assistant that answers questions based on the provided documents.
Use ONLY the information from the context below to answer the question.
If the answer is not in the context, say "I cannot find this information in the provided documents."

Context:
{context}
"""
    
    messages = [
        {"role": "user", "content": query}
    ]
    
    # LLM call করবে
    answer = await llm_service.chat_completion_async(
        messages=messages,
        system_prompt=system_prompt.format(context=context)
    )
    
    # Source documents
    sources = [
        {
            "document_id": meta.get("document_id"),
            "chunk_id": meta.get("chunk_id"),
            "score": score
        }
        for _, score, meta in results
    ]
    
    return {
        "answer": answer,
        "sources": sources,
        "context_used": len(results)
    }