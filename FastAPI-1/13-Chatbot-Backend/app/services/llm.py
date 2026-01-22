from groq import Groq
from app.core.config import settings
from typing import List, Dict, Optional
import json

class LLMService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> Dict:
        """Simple chat completion"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                "content": response.choices[0].message.content,
                "tokens": response.usage.total_tokens,
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    async def chat_with_context(
        self,
        query: str,
        context_docs: List[Dict],
        chat_history: List[Dict] = None
    ) -> Dict:
        """RAG: Chat with vector store context"""
        # Build context from retrieved documents
        context = "\n\n".join([
            f"Document {i+1}:\n{doc['content']}"
            for i, doc in enumerate(context_docs[:3])
        ])
        
        # Build messages
        messages = []
        
        # System prompt
        messages.append({
            "role": "system",
            "content": f"""You are a helpful AI assistant. Use the following context to answer questions.
            
Context:
{context}

If the context doesn't contain relevant information, say so clearly."""
        })
        
        # Add chat history
        if chat_history:
            messages.extend(chat_history[-5:])  # Last 5 messages
        
        # Add current query
        messages.append({
            "role": "user",
            "content": query
        })
        
        return await self.chat(messages)
    
    async def stream_chat(self, messages: List[Dict], temperature: float = 0.7):
        """Streaming response"""
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"Groq streaming error: {str(e)}")

llm_service = LLMService()