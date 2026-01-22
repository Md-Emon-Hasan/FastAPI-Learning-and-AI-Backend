from groq import Groq
from typing import List, Dict, Optional, AsyncIterator
from app.core.config import get_settings
import asyncio

settings = get_settings()

class LLMService:
    """
    Groq LLM service - Chat completion এর জন্য
    
    Features:
    - Sync এবং async support
    - Streaming support
    - Conversation history management
    """
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
    
    def _format_messages(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Messages format করবে Groq API এর জন্য
        System prompt থাকলে শুরুতে add করবে
        """
        formatted = []
        
        if system_prompt:
            formatted.append({
                "role": "system",
                "content": system_prompt
            })
        
        formatted.extend(messages)
        return formatted
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        Synchronous chat completion
        
        Args:
            messages: [{"role": "user", "content": "Hello"}]
            system_prompt: Optional system instruction
            temperature: 0.0-2.0 (higher = more creative)
            max_tokens: Max response length
        
        Returns: Assistant's response text
        """
        formatted_messages = self._format_messages(messages, system_prompt)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.choices[0].message.content
    
    async def chat_completion_async(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        Async chat completion - FastAPI async endpoints এ use করবো
        
        Blocking operation কে thread এ run করবে
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.chat_completion(
                messages, system_prompt, temperature, max_tokens
            )
        )
    
    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        """
        Streaming chat completion - Real-time response এর জন্য
        
        Usage:
            for chunk in llm.chat_completion_stream(messages):
                print(chunk, end="", flush=True)
        
        Yields: Text chunks
        """
        formatted_messages = self._format_messages(messages, system_prompt)
        
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def chat_completion_stream_async(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """
        Async streaming - FastAPI streaming response এ use করবো
        
        Usage:
            async for chunk in llm.chat_completion_stream_async(messages):
                yield chunk
        """
        formatted_messages = self._format_messages(messages, system_prompt)
        
        # Run streaming in executor
        loop = asyncio.get_event_loop()
        
        def stream_generator():
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        # Convert to async iterator
        for chunk in await loop.run_in_executor(None, lambda: list(stream_generator())):
            yield chunk

# Singleton instance
llm_service = LLMService()