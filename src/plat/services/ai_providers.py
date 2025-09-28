"""AI provider services for content generation and enhancement."""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

import openai
import google.generativeai as genai
from anthropic import Anthropic

from ..core.config import settings

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def generate_content(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        max_tokens: int = 2000
    ) -> Tuple[str, float]:
        """Generate content and return content with confidence score."""
        pass
    
    @abstractmethod
    async def enhance_content(
        self, 
        content: str, 
        enhancement_type: str = "improve"
    ) -> Tuple[str, float]:
        """Enhance existing content and return enhanced content with confidence score."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI GPT-4 provider implementation."""
    
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not provided")
        openai.api_key = settings.openai_api_key
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    
    async def generate_content(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        max_tokens: int = 2000
    ) -> Tuple[str, float]:
        """Generate neurosurgical content using GPT-4."""
        try:
            system_prompt = (
                "You are an expert neurosurgeon and medical educator. "
                "Provide accurate, evidence-based information about neurosurgical "
                "concepts, procedures, and clinical guidelines. Always cite relevant "
                "medical literature when possible."
            )
            
            messages = [{"role": "system", "content": system_prompt}]
            
            if context:
                messages.append({"role": "user", "content": f"Context: {context}"})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.3  # Lower temperature for more consistent medical content
            )
            
            content = response.choices[0].message.content
            # Estimate confidence based on response length and completion reason
            confidence = self._calculate_confidence(response)
            
            return content, confidence
            
        except Exception as e:
            logger.error(f"OpenAI content generation failed: {e}")
            return "", 0.0
    
    async def enhance_content(
        self, 
        content: str, 
        enhancement_type: str = "improve"
    ) -> Tuple[str, float]:
        """Enhance existing content using GPT-4."""
        try:
            enhancement_prompts = {
                "improve": "Improve the following neurosurgical content by adding more detail, clarity, and evidence-based information:",
                "summarize": "Summarize the following neurosurgical content while preserving key clinical information:",
                "update": "Update the following neurosurgical content with the latest evidence and best practices:",
                "clarify": "Clarify and explain the following neurosurgical content for better understanding:"
            }
            
            prompt = enhancement_prompts.get(enhancement_type, enhancement_prompts["improve"])
            full_prompt = f"{prompt}\n\n{content}"
            
            return await self.generate_content(full_prompt)
            
        except Exception as e:
            logger.error(f"OpenAI content enhancement failed: {e}")
            return content, 0.5  # Return original content with low confidence
    
    def _calculate_confidence(self, response) -> float:
        """Calculate confidence score based on OpenAI response."""
        base_confidence = 0.8  # Base confidence for GPT-4
        
        # Adjust based on completion reason
        if response.choices[0].finish_reason == "stop":
            return base_confidence
        elif response.choices[0].finish_reason == "length":
            return base_confidence * 0.9  # Slightly lower if truncated
        else:
            return base_confidence * 0.7


class GeminiProvider(AIProvider):
    """Google Gemini provider implementation."""
    
    def __init__(self):
        if not settings.google_api_key:
            raise ValueError("Google API key not provided")
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_content(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        max_tokens: int = 2000
    ) -> Tuple[str, float]:
        """Generate neurosurgical content using Gemini."""
        try:
            system_instruction = (
                "You are an expert neurosurgeon and medical educator. "
                "Provide accurate, evidence-based information about neurosurgical "
                "concepts, procedures, and clinical guidelines."
            )
            
            full_prompt = f"{system_instruction}\n\n"
            if context:
                full_prompt += f"Context: {context}\n\n"
            full_prompt += prompt
            
            response = await asyncio.to_thread(
                self.model.generate_content, 
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.3
                )
            )
            
            content = response.text
            confidence = 0.8  # Base confidence for Gemini
            
            return content, confidence
            
        except Exception as e:
            logger.error(f"Gemini content generation failed: {e}")
            return "", 0.0
    
    async def enhance_content(
        self, 
        content: str, 
        enhancement_type: str = "improve"
    ) -> Tuple[str, float]:
        """Enhance existing content using Gemini."""
        try:
            enhancement_prompts = {
                "improve": "Improve the following neurosurgical content:",
                "summarize": "Summarize the following neurosurgical content:",
                "update": "Update the following neurosurgical content:",
                "clarify": "Clarify the following neurosurgical content:"
            }
            
            prompt = enhancement_prompts.get(enhancement_type, enhancement_prompts["improve"])
            full_prompt = f"{prompt}\n\n{content}"
            
            return await self.generate_content(full_prompt)
            
        except Exception as e:
            logger.error(f"Gemini content enhancement failed: {e}")
            return content, 0.5


class ClaudeProvider(AIProvider):
    """Anthropic Claude provider implementation."""
    
    def __init__(self):
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key not provided")
        self.client = Anthropic(api_key=settings.anthropic_api_key)
    
    async def generate_content(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        max_tokens: int = 2000
    ) -> Tuple[str, float]:
        """Generate neurosurgical content using Claude."""
        try:
            system_prompt = (
                "You are an expert neurosurgeon and medical educator. "
                "Provide accurate, evidence-based information about neurosurgical "
                "concepts, procedures, and clinical guidelines."
            )
            
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\n{prompt}"
            
            response = await asyncio.to_thread(
                self.client.messages.create,
                model="claude-3-opus-20240229",
                max_tokens=max_tokens,
                temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            content = response.content[0].text
            confidence = 0.85  # Base confidence for Claude
            
            return content, confidence
            
        except Exception as e:
            logger.error(f"Claude content generation failed: {e}")
            return "", 0.0
    
    async def enhance_content(
        self, 
        content: str, 
        enhancement_type: str = "improve"
    ) -> Tuple[str, float]:
        """Enhance existing content using Claude."""
        try:
            enhancement_prompts = {
                "improve": "Improve the following neurosurgical content by adding more detail and evidence:",
                "summarize": "Summarize the following neurosurgical content concisely:",
                "update": "Update the following neurosurgical content with latest practices:",
                "clarify": "Clarify and explain the following neurosurgical content:"
            }
            
            prompt = enhancement_prompts.get(enhancement_type, enhancement_prompts["improve"])
            full_prompt = f"{prompt}\n\n{content}"
            
            return await self.generate_content(full_prompt)
            
        except Exception as e:
            logger.error(f"Claude content enhancement failed: {e}")
            return content, 0.5


class AIProviderManager:
    """Manages multiple AI providers and coordinates content generation."""
    
    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available AI providers based on configuration."""
        try:
            if settings.openai_api_key:
                self.providers["openai"] = OpenAIProvider()
                logger.info("OpenAI provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI provider: {e}")
        
        try:
            if settings.google_api_key:
                self.providers["gemini"] = GeminiProvider()
                logger.info("Gemini provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini provider: {e}")
        
        try:
            if settings.anthropic_api_key:
                self.providers["claude"] = ClaudeProvider()
                logger.info("Claude provider initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Claude provider: {e}")
    
    async def generate_consensus_content(
        self, 
        prompt: str, 
        context: Optional[str] = None,
        providers: Optional[List[str]] = None
    ) -> Tuple[str, float]:
        """Generate content using multiple providers and create consensus."""
        if not providers:
            providers = list(self.providers.keys())
        
        if not providers or not any(p in self.providers for p in providers):
            raise ValueError("No valid AI providers available")
        
        # Generate content from multiple providers
        tasks = []
        for provider_name in providers:
            if provider_name in self.providers:
                task = self.providers[provider_name].generate_content(prompt, context)
                tasks.append((provider_name, task))
        
        if not tasks:
            raise ValueError("No providers available for content generation")
        
        # Wait for all providers to complete
        results = []
        for provider_name, task in tasks:
            try:
                content, confidence = await task
                if content:
                    results.append((provider_name, content, confidence))
            except Exception as e:
                logger.warning(f"Provider {provider_name} failed: {e}")
        
        if not results:
            return "", 0.0
        
        # If only one result, return it
        if len(results) == 1:
            return results[0][1], results[0][2]
        
        # For multiple results, use the one with highest confidence
        # In a more sophisticated implementation, we could combine/synthesize content
        best_result = max(results, key=lambda x: x[2])
        return best_result[1], best_result[2]
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return list(self.providers.keys())


# Global AI provider manager instance
ai_manager = AIProviderManager()