from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.core.database import get_db
from app.api.dependencies import get_current_user, rate_limit
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.schemas.schemas import (
    ChatRequest, ChatResponse, ConversationCreate, 
    ConversationResponse, ConversationWithMessages, MessageResponse
)
from app.services.llm import llm_service
import json

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(rate_limit(30))  # 30 requests per minute
):
    """
    Main chat endpoint - User message পাঠিয়ে AI response পাবে
    
    Features:
    - New conversation তৈরি করবে অথবা existing এ add করবে
    - Message history maintain করবে
    - LLM call করবে
    - Streaming support (optional)
    """
    
    # Conversation handle করবে
    if request.conversation_id:
        # Existing conversation fetch করবে
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            )
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    else:
        # New conversation তৈরি করবে
        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:50] + "..." if len(request.message) > 50 else request.message
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
    
    # User message save করবে
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)
    
    # Previous messages load করবে (context এর জন্য)
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
        .limit(20)  # Last 20 messages (context window manage করার জন্য)
    )
    previous_messages = result.scalars().all()
    
    # Messages format করবে LLM এর জন্য
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in previous_messages
    ]
    
    # LLM call করবে
    try:
        ai_response = await llm_service.chat_completion_async(
            messages=messages,
            system_prompt=conversation.system_prompt,
            temperature=request.temperature,
            max_tokens=1024
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM error: {str(e)}"
        )
    
    # Assistant message save করবে
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_response,
        metadata={
            "model": request.model or llm_service.model,
            "temperature": request.temperature
        }
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)
    
    return {
        "conversation_id": conversation.id,
        "message": user_message,
        "assistant_message": assistant_message
    }

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Streaming chat endpoint - Real-time response
    
    Returns: Server-Sent Events (SSE) stream
    """
    
    # Conversation setup (same as above)
    if request.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(
            user_id=current_user.id,
            title=request.message[:50]
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    await db.commit()
    
    # Load conversation history
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
        .limit(20)
    )
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in result.scalars().all()
    ]
    
    # Streaming generator
    async def event_stream():
        full_response = ""
        
        async for chunk in llm_service.chat_completion_stream_async(
            messages=messages,
            system_prompt=conversation.system_prompt,
            temperature=request.temperature
        ):
            full_response += chunk
            # SSE format
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        
        # Save complete response
        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=full_response
        )
        db.add(assistant_message)
        await db.commit()
        
        yield f"data: {json.dumps({'done': True, 'message_id': assistant_message.id})}\n\n"
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """User এর সব conversations list করবে"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.updated_at))
        .limit(limit)
        .offset(offset)
    )
    
    conversations = result.scalars().all()
    
    # Message count add করবে
    response = []
    for conv in conversations:
        msg_result = await db.execute(
            select(Message).where(Message.conversation_id == conv.id)
        )
        message_count = len(msg_result.scalars().all())
        
        response.append({
            **conv.__dict__,
            "message_count": message_count
        })
    
    return response

@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Specific conversation এর details এবং সব messages"""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Load all messages
    msg_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = msg_result.scalars().all()
    
    return {
        **conversation.__dict__,
        "messages": messages,
        "message_count": len(messages)
    }

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Conversation delete করবে (cascade delete messages)"""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await db.delete(conversation)
    await db.commit()
    
    return {"message": "Conversation deleted successfully"}