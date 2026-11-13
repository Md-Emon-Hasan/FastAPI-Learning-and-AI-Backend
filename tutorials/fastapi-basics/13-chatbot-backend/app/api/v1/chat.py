from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.services.llm import llm_service
from app.db.models import User, Conversation, Message
from app.db.vector_store import vector_store
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chat endpoint with RAG support
    - Creates/continues conversation
    - Searches vector store for context
    - Generates response with Groq
    """
    try:
        # Get or create conversation
        if request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.conversation_id == request.conversation_id,
                Conversation.user_id == current_user.id
            ).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            # New conversation
            conversation = Conversation(
                conversation_id=str(uuid.uuid4()),
                user_id=current_user.id,
                title=request.message[:50]
            )
            db.add(conversation)
            db.commit()
        
        # Get chat history
        messages_db = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.timestamp.desc()).limit(10).all()
        
        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages_db)
        ]
        
        # Search vector store for context
        context_docs = vector_store.similarity_search(request.message, k=3)
        
        # Generate response
        if context_docs:
            # RAG mode
            response = await llm_service.chat_with_context(
                query=request.message,
                context_docs=context_docs,
                chat_history=chat_history
            )
        else:
            # Normal chat
            messages = chat_history + [{"role": "user", "content": request.message}]
            response = await llm_service.chat(
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        
        # Save user message
        user_msg = Message(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
            timestamp=datetime.utcnow()
        )
        db.add(user_msg)
        
        # Save assistant message
        assistant_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=response["content"],
            tokens_used=response["tokens"],
            timestamp=datetime.utcnow()
        )
        db.add(assistant_msg)
        
        # Update conversation
        conversation.updated_at = datetime.utcnow()
        db.commit()
        
        return ChatResponse(
            conversation_id=conversation.conversation_id,
            message=response["content"],
            tokens_used=response["tokens"],
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history/{conversation_id}")
async def get_chat_history(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversation history"""
    conversation = db.query(Conversation).filter(
        Conversation.conversation_id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.timestamp).all()
    
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in messages
        ]
    }