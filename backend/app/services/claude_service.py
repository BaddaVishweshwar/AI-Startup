"""
Claude Service - Anthropic API Integration

Provides high-quality LLM responses using Claude for:
- SQL generation with superior accuracy
- Executive-level insight generation
- Intelligent visualization selection
- Multi-turn reasoning and analysis

Claude excels at structured tasks and provides CamelAI-quality results
with 3-5 second response times.
"""

import logging
import json
from typing import Optional, Dict, Any
from anthropic import Anthropic, AnthropicError
from ..config import settings

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for interacting with Claude (Anthropic) API."""
    
    def __init__(self):
        """Initialize Claude client."""
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model_name = settings.ANTHROPIC_MODEL
        self.max_tokens = settings.ANTHROPIC_MAX_TOKENS
        
        if self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                logger.info(f"✅ Claude service initialized with model: {self.model_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Claude client: {e}")
                self.client = None
        else:
            self.client = None
            logger.warning("⚠️ No Anthropic API key found. Claude service disabled.")
    
    def is_available(self) -> bool:
        """Check if Claude service is available."""
        return self.client is not None and self.api_key is not None
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate response using Claude.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            json_mode: Whether to request JSON output
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        if not self.is_available():
            raise Exception("Claude service is not available. Please set ANTHROPIC_API_KEY.")
        
        try:
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]
            
            # Add JSON mode instruction if requested
            if json_mode:
                json_instruction = "\n\nIMPORTANT: Return ONLY valid JSON. No markdown, no explanations, just the JSON object."
                messages[0]["content"] += json_instruction
            
            # Prepare system prompt
            system = system_prompt or "You are a helpful AI assistant."
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature,
                system=system,
                messages=messages
            )
            
            # Extract text from response
            result = response.content[0].text
            
            # Clean up JSON response if needed
            if json_mode:
                result = self._clean_json_response(result)
            
            logger.debug(f"Claude response generated: {len(result)} characters")
            return result
            
        except AnthropicError as e:
            logger.error(f"Anthropic API error: {e}")
            raise Exception(f"Claude API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating Claude response: {e}")
            raise e
    
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response by removing markdown code blocks."""
        # Remove markdown code blocks if present
        if response.strip().startswith("```"):
            # Extract content between ```json and ```
            lines = response.strip().split("\n")
            # Remove first line (```json or ```) and last line (```)
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            response = "\n".join(lines)
        
        return response.strip()
    
    def generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> str:
        """
        Generate response with retry logic for rate limits.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            json_mode: Whether to request JSON
            temperature: Temperature for generation
            max_retries: Maximum number of retries
            
        Returns:
            Generated response
        """
        import time
        
        for attempt in range(max_retries):
            try:
                return self.generate_response(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    json_mode=json_mode,
                    temperature=temperature
                )
            except AnthropicError as e:
                if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limit hit. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
        
        raise Exception("Max retries exceeded")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.7,
        task_type: Optional[str] = None,
        model: Optional[str] = None,  # Accept but ignore for compatibility
        **kwargs  # Accept any other args
    ) -> str:
        """
        Alias for generate_response() for backward compatibility.
        Many agents call .generate() instead of .generate_response().
        """
        return self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=json_mode,
            temperature=temperature
        )


# Singleton instance
claude_service = ClaudeService()
