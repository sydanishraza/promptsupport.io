"""
KE-PR6: LLM Client
Centralized LLM client with provider switching, retries, and timeout controls
"""

import os
import time
import json
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import random

from ..logging_util import stage_log

class LLMError(Exception):
    """Custom exception for LLM-related errors"""
    pass

class LLMClient:
    """
    Centralized LLM client with provider switching, exponential backoff, 
    timeout controls, and secret redaction in logs
    """
    
    def __init__(self, provider: Optional[str] = None, timeout: int = 120):
        self.provider = provider or os.getenv("LLM_PROVIDER", "openai")
        self.timeout = timeout
        self.max_retries = 3
        self.base_delay = 1.0  # Base delay for exponential backoff
        
        # API Keys from environment
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.local_llm_url = os.getenv("LOCAL_LLM_URL")
        
        # Provider configurations
        self.providers = {
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "default_model": "gpt-4o-mini",
                "requires_key": True
            },
            "anthropic": {
                "base_url": "https://api.anthropic.com/v1",
                "default_model": "claude-3-5-sonnet-20241022",
                "requires_key": True
            },
            "local": {
                "base_url": self.local_llm_url or "http://localhost:1234/v1",
                "default_model": "local-model",
                "requires_key": False
            }
        }
        
        # Validate provider configuration
        self._validate_configuration()
        
        print(f"🤖 LLMClient initialized - Provider: {self.provider}, Timeout: {timeout}s")
    
    def _validate_configuration(self):
        """Validate provider configuration and API keys"""
        if self.provider not in self.providers:
            raise LLMError(f"Unsupported provider: {self.provider}")
        
        provider_config = self.providers[self.provider]
        
        if provider_config["requires_key"]:
            if self.provider == "openai" and not self.openai_key:
                raise LLMError("OpenAI API key required but not found in environment")
            elif self.provider == "anthropic" and not self.anthropic_key:
                raise LLMError("Anthropic API key required but not found in environment")
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for the current provider"""
        headers = {"Content-Type": "application/json"}
        
        if self.provider == "openai" and self.openai_key:
            headers["Authorization"] = f"Bearer {self.openai_key}"
        elif self.provider == "anthropic" and self.anthropic_key:
            headers["x-api-key"] = self.anthropic_key
            headers["anthropic-version"] = "2023-06-01"
        
        return headers
    
    def _redact_secrets(self, text: str) -> str:
        """Redact API keys and other secrets from logs"""
        redacted = text
        
        # Redact OpenAI key
        if self.openai_key and len(self.openai_key) > 8:
            redacted = redacted.replace(self.openai_key, f"sk-***{self.openai_key[-4:]}")
        
        # Redact Anthropic key  
        if self.anthropic_key and len(self.anthropic_key) > 8:
            redacted = redacted.replace(self.anthropic_key, f"sk-ant-***{self.anthropic_key[-4:]}")
        
        return redacted
    
    def _exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
        return min(delay, 60)  # Cap at 60 seconds
    
    async def complete(
        self, 
        prompt: str = None,
        system_message: str = None, 
        user_message: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> str:
        """
        Generate text completion with provider-specific formatting
        
        Args:
            prompt: Single prompt string (converted to messages)
            system_message: System message content
            user_message: User message content  
            model: Model to use (defaults to provider default)
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Generated text completion
        """
        
        # Handle different input formats
        messages = self._format_messages(prompt, system_message, user_message)
        
        provider_config = self.providers[self.provider]
        model = model or provider_config["default_model"]
        
        # Prepare request payload
        payload = self._prepare_payload(messages, model, temperature, max_tokens, **kwargs)
        
        # Execute request with retries
        for attempt in range(self.max_retries):
            try:
                print(f"🤖 LLM Request - Provider: {self.provider}, Model: {model}, Attempt: {attempt + 1}")
                
                response = await self._make_request(payload)
                result = self._extract_completion(response)
                
                print(f"✅ LLM Success - {len(result)} chars generated")
                return result
                
            except Exception as e:
                print(f"⚠️ LLM Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    delay = self._exponential_backoff(attempt)
                    print(f"⏳ Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
                else:
                    print(f"❌ LLM failed after {self.max_retries} attempts")
                    raise LLMError(f"LLM completion failed: {str(e)}")
    
    def _format_messages(self, prompt: str = None, system_message: str = None, user_message: str = None) -> List[Dict[str, str]]:
        """Format messages for LLM provider"""
        messages = []
        
        if prompt:
            # Single prompt - convert to user message
            messages.append({"role": "user", "content": prompt.strip()})
        else:
            # Separate system/user messages
            if system_message:
                messages.append({"role": "system", "content": system_message.strip()})
            if user_message:
                messages.append({"role": "user", "content": user_message.strip()})
        
        if not messages:
            raise LLMError("No prompt, system_message, or user_message provided")
        
        return messages
    
    def _prepare_payload(self, messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int, **kwargs) -> Dict[str, Any]:
        """Prepare provider-specific request payload"""
        base_payload = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if self.provider == "openai":
            payload = {
                **base_payload,
                "messages": messages,
                "stream": False
            }
        elif self.provider == "anthropic":
            # Anthropic has different message format
            system_content = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                else:
                    user_messages.append(msg)
            
            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": user_messages
            }
            
            if system_content:
                payload["system"] = system_content
                
        else:  # local or other providers
            payload = {
                **base_payload,
                "messages": messages
            }
        
        # Add any additional kwargs
        payload.update(kwargs)
        
        return payload
    
    async def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to LLM provider"""
        provider_config = self.providers[self.provider]
        
        if self.provider == "anthropic":
            url = f"{provider_config['base_url']}/messages"
        else:
            url = f"{provider_config['base_url']}/chat/completions"
        
        headers = self._get_auth_headers()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                error_text = self._redact_secrets(response.text)
                raise LLMError(f"HTTP {response.status_code}: {error_text}")
            
            return response.json()
    
    def _extract_completion(self, response: Dict[str, Any]) -> str:
        """Extract completion text from provider response"""
        try:
            if self.provider == "openai" or self.provider == "local":
                return response["choices"][0]["message"]["content"].strip()
            elif self.provider == "anthropic":
                return response["content"][0]["text"].strip()
            else:
                # Fallback - try common patterns
                if "choices" in response:
                    return response["choices"][0]["message"]["content"].strip()
                elif "content" in response:
                    return response["content"][0]["text"].strip()
                else:
                    raise LLMError(f"Unknown response format from {self.provider}")
                    
        except (KeyError, IndexError) as e:
            raise LLMError(f"Failed to extract completion: {str(e)}")
    
    async def moderate(self, text: str) -> Dict[str, Any]:
        """Content moderation (OpenAI only for now)"""
        if self.provider != "openai":
            # Return safe for non-OpenAI providers
            return {
                "ok": True, 
                "provider": self.provider,
                "message": "Moderation not implemented for this provider"
            }
        
        try:
            url = f"{self.providers['openai']['base_url']}/moderations"
            headers = self._get_auth_headers()
            payload = {"input": text}
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    return {"ok": False, "error": f"HTTP {response.status_code}"}
                
                data = response.json()
                result = data["results"][0]
                
                return {
                    "ok": not result["flagged"],
                    "categories": result.get("categories", {}),
                    "category_scores": result.get("category_scores", {})
                }
                
        except Exception as e:
            print(f"⚠️ Moderation check failed: {str(e)}")
            return {"ok": True, "error": str(e)}  # Fail open
    
    @stage_log
    async def analyze_content(self, content: str, analysis_type: str = "general") -> Dict[str, Any]:
        """High-level content analysis wrapper"""
        from .prompts import CONTENT_ANALYSIS_PROMPT
        
        prompt = CONTENT_ANALYSIS_PROMPT.format(
            analysis_type=analysis_type,
            content=content[:8000]  # Limit content length
        )
        
        try:
            result = await self.complete(prompt=prompt, temperature=0.3)
            return {
                "analysis": result,
                "analysis_type": analysis_type,
                "provider": self.provider,
                "success": True
            }
        except Exception as e:
            return {
                "analysis": f"Analysis failed: {str(e)}",
                "analysis_type": analysis_type,
                "provider": self.provider,
                "success": False,
                "error": str(e)
            }


# Global LLM client instance
_llm_client_instance = None

def get_llm_client(provider: Optional[str] = None, **kwargs) -> LLMClient:
    """Get or create global LLM client instance"""
    global _llm_client_instance
    
    # Always create new instance if provider is specified
    if provider or _llm_client_instance is None:
        _llm_client_instance = LLMClient(provider=provider, **kwargs)
    
    return _llm_client_instance