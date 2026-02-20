"""AI analysis module for text processing."""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime


class AIAnalyzer:
    """Handles AI-powered text analysis."""
    
    def __init__(self, provider: str = "openai", model: Optional[str] = None):
        self.provider = provider.lower()
        self.model = model or self._default_model()
        self.client = self._init_client()
    
    def _default_model(self) -> str:
        """Get default model for provider."""
        defaults = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-haiku-20240307",
            "ollama": "llama3"
        }
        return defaults.get(self.provider, "gpt-4o-mini")
    
    def _init_client(self):
        """Initialize AI client based on provider."""
        if self.provider == "openai":
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")
            return OpenAI(api_key=api_key)
        
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")
            return Anthropic(api_key=api_key)
        
        elif self.provider == "ollama":
            import ollama
            return ollama
        
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and return structured insights.
        
        Returns:
            {
                "sentiment": str,
                "sentiment_confidence": float,
                "entities": [{"text": str, "type": str}],
                "topics": [str],
                "summary": str,
                "model": str,
                "timestamp": str
            }
        """
        prompt = self._build_prompt(text)
        
        try:
            response = self._call_ai(prompt)
            result = self._parse_response(response)
            result["model"] = self.model
            result["timestamp"] = datetime.utcnow().isoformat()
            return result
        except Exception as e:
            return self._fallback_analysis(text, str(e))
    
    def _build_prompt(self, text: str) -> str:
        """Build analysis prompt."""
        return f"""Analyze the following text and return a JSON object with this exact structure:
{{
  "sentiment": "positive" | "negative" | "neutral",
  "sentiment_confidence": 0.0 to 1.0,
  "entities": [
    {{"text": "entity name", "type": "PERSON" | "ORGANIZATION" | "LOCATION" | "OTHER"}}
  ],
  "topics": ["topic1", "topic2", "topic3"],
  "summary": "2-sentence summary"
}}

Rules:
- Be concise and factual
- Extract 3-5 topics maximum
- Confidence should reflect certainty
- Return ONLY valid JSON, no markdown

Text to analyze:
{text[:4000]}"""
    
    def _call_ai(self, prompt: str) -> str:
        """Call AI provider and return response text."""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            return response.choices[0].message.content
        
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        elif self.provider == "ollama":
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content']
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format."""
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        
        try:
            data = json.loads(response)
            
            # Validate required fields
            required = ["sentiment", "sentiment_confidence", "entities", "topics", "summary"]
            for field in required:
                if field not in data:
                    raise ValueError(f"Missing field: {field}")
            
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")
    
    def _fallback_analysis(self, text: str, error: str) -> Dict[str, Any]:
        """Provide basic fallback analysis if AI fails."""
        words = text.lower().split()
        
        # Simple sentiment heuristic
        positive_words = {"good", "great", "excellent", "happy", "love", "best"}
        negative_words = {"bad", "terrible", "awful", "hate", "worst", "poor"}
        
        pos_count = sum(1 for w in words if w in positive_words)
        neg_count = sum(1 for w in words if w in negative_words)
        
        if pos_count > neg_count:
            sentiment = "positive"
        elif neg_count > pos_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "sentiment_confidence": 0.5,
            "entities": [],
            "topics": ["general"],
            "summary": text[:200] + "..." if len(text) > 200 else text,
            "model": f"{self.model} (fallback)",
            "timestamp": datetime.utcnow().isoformat(),
            "error": error
        }
