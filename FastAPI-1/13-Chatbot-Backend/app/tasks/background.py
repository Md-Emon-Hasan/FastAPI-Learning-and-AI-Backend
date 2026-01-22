from fastapi import BackgroundTasks
from app.db.vector_store import vector_store
from app.services.pdf_processor import pdf_processor
from app.db.session import SessionLocal
from app.db.models import AgentTaskDB
from app.services.llm import llm_service
from typing import Dict
import logging

logger = logging.getLogger(__name__)

async def process_pdf_background(file_path: str, filename: str, user_id: int):
    """Background task: Process PDF and add to vector store"""
    try:
        logger.info(f"Processing PDF: {filename}")
        
        with open(file_path, 'rb') as f:
            result = pdf_processor.process_for_embedding(f, filename)
        
        # Add to vector store
        chunks = vector_store.add_documents(
            texts=[result["text"]],
            metadatas=[result["metadata"]]
        )
        
        logger.info(f"PDF processed: {chunks} chunks created")
        
    except Exception as e:
        logger.error(f"PDF processing failed: {str(e)}")

async def run_agent_task(task_id: str, task_type: str, input_data: str, parameters: Dict):
    """Background task: Run agent workflow"""
    db = SessionLocal()
    
    try:
        # Update status
        task = db.query(AgentTaskDB).filter(AgentTaskDB.task_id == task_id).first()
        task.status = "running"
        db.commit()
        
        # Execute based on task type
        if task_type == "research":
            # Search vector store
            context = vector_store.similarity_search(input_data, k=5)
            
            # Generate response with LLM
            response = await llm_service.chat_with_context(
                query=input_data,
                context_docs=context
            )
            
            result = response["content"]
        
        elif task_type == "summarize":
            messages = [
                {"role": "system", "content": "You are a summarization expert."},
                {"role": "user", "content": f"Summarize this:\n\n{input_data}"}
            ]
            response = await llm_service.chat(messages)
            result = response["content"]
        
        else:
            result = "Unknown task type"
        
        # Update with result
        task.status = "completed"
        task.result = result
        db.commit()
        
    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        db.commit()
        logger.error(f"Agent task failed: {str(e)}")
    
    finally:
        db.close()