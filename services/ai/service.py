"""
AI Service for the AI-driven learning platform.
Provides Ollama abstraction, prompt execution, caching, and safety mechanisms.
"""

from typing import List, Dict, Any, Optional
import requests
import hashlib
import json
from datetime import datetime, timedelta
from enum import Enum
import time
import re


class SafetyLevel(Enum):
    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"


class ModelProvider(Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"


class AIService:
    def __init__(self, ollama_url: str = "http://localhost:11434", 
                 default_model: str = "mistral", 
                 cache_ttl_minutes: int = 60):
        self.ollama_url = ollama_url
        self.default_model = default_model
        self.cache_ttl_minutes = cache_ttl_minutes
        self.response_cache = {}
        self.usage_stats = {}
        self.safety_filters = {
            SafetyLevel.STRICT: self._strict_safety_filter,
            SafetyLevel.MODERATE: self._moderate_safety_filter,
            SafetyLevel.PERMISSIVE: self._permissive_safety_filter
        }
    
    def generate_response(self, prompt: str, model: str = None, 
                         temperature: float = 0.7, 
                         safety_level: SafetyLevel = SafetyLevel.MODERATE,
                         use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Generate AI response for a given prompt using the specified model.
        """
        if model is None:
            model = self.default_model
        
        # Create cache key
        cache_key = self._create_cache_key(prompt, model, temperature, safety_level)
        
        # Check cache first
        if use_cache and cache_key in self.response_cache:
            cached_response = self.response_cache[cache_key]
            if datetime.utcnow() < cached_response["expires_at"]:
                # Update usage stats
                self._update_usage_stats(model, len(prompt), len(cached_response["response"]))
                return cached_response["response"]
            else:
                # Remove expired cache entry
                del self.response_cache[cache_key]
        
        # Apply safety filter to prompt
        if not self._apply_safety_filter(prompt, safety_level):
            return {"error": "Prompt failed safety check", "response": ""}
        
        # Make request to Ollama
        response = self._call_ollama_api(prompt, model, temperature)
        
        if response and "error" not in response:
            # Apply safety filter to response
            filtered_response = self._apply_output_safety_filter(response["response"], safety_level)
            
            # Cache the response if successful
            if use_cache:
                self._cache_response(cache_key, filtered_response)
            
            # Update usage stats
            self._update_usage_stats(model, len(prompt), len(filtered_response))
            
            return {"response": filtered_response}
        else:
            return response
    
    def _call_ollama_api(self, prompt: str, model: str, temperature: float) -> Optional[Dict[str, Any]]:
        """
        Make API call to Ollama service.
        """
        try:
            url = f"{self.ollama_url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {"response": result.get("response", "")}
            else:
                return {"error": f"Ollama API error: {response.status_code}", "response": ""}
        
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}", "response": ""}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "response": ""}
    
    def _create_cache_key(self, prompt: str, model: str, temperature: float, 
                         safety_level: SafetyLevel) -> str:
        """
        Create a unique cache key for the given parameters.
        """
        cache_string = f"{prompt}:{model}:{temperature}:{safety_level.value}"
        return hashlib.sha256(cache_string.encode()).hexdigest()
    
    def _cache_response(self, cache_key: str, response: str):
        """
        Cache the AI response with TTL.
        """
        self.response_cache[cache_key] = {
            "response": response,
            "expires_at": datetime.utcnow() + timedelta(minutes=self.cache_ttl_minutes),
            "created_at": datetime.utcnow()
        }
    
    def _apply_safety_filter(self, text: str, safety_level: SafetyLevel) -> bool:
        """
        Apply safety filtering to input text.
        """
        if safety_level not in self.safety_filters:
            return True  # Default to safe if unknown level
        
        return self.safety_filters[safety_level](text)
    
    def _strict_safety_filter(self, text: str) -> bool:
        """
        Apply strict safety filtering.
        """
        # Check for potentially harmful content
        harmful_patterns = [
            r"(?i)(kill|murder|assassinate|terrorist|bomb|weapon|violence)",
            r"(?i)(sexually|explicit|nudity|pornographic)",
            r"(?i)(drug|illegal|substance abuse)",
            r"(?i)(suicide|self-harm|kill myself)"
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, text):
                return False
        
        return True
    
    def _moderate_safety_filter(self, text: str) -> bool:
        """
        Apply moderate safety filtering.
        """
        # Less restrictive than strict
        harmful_patterns = [
            r"(?i)(terrorist|bomb|weapon)",
            r"(?i)(explicit|nudity|pornographic)",
            r"(?i)(drug|illegal|controlled substance)",
            r"(?i)(suicide|kill myself)"
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, text):
                return False
        
        return True
    
    def _permissive_safety_filter(self, text: str) -> bool:
        """
        Apply permissive safety filtering.
        """
        # Only check for the most severe content
        harmful_patterns = [
            r"(?i)(terrorist|bomb|weapon|chemical weapon)",
            r"(?i)(instructions for making explosives)",
            r"(?i)(suicide method|how to kill myself)"
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, text):
                return False
        
        return True
    
    def _apply_output_safety_filter(self, text: str, safety_level: SafetyLevel) -> str:
        """
        Apply safety filtering to AI-generated output.
        """
        # For now, just return the text as-is
        # In a real implementation, this would sanitize or redact unsafe content
        return text
    
    def _update_usage_stats(self, model: str, input_tokens: int, output_tokens: int):
        """
        Update usage statistics for the model.
        """
        if model not in self.usage_stats:
            self.usage_stats[model] = {
                "requests_count": 0,
                "input_tokens_total": 0,
                "output_tokens_total": 0,
                "last_used": datetime.utcnow()
            }
        
        self.usage_stats[model]["requests_count"] += 1
        self.usage_stats[model]["input_tokens_total"] += input_tokens
        self.usage_stats[model]["output_tokens_total"] += output_tokens
        self.usage_stats[model]["last_used"] = datetime.utcnow()
    
    def get_usage_stats(self, model: str = None) -> Dict[str, Any]:
        """
        Get usage statistics for models.
        """
        if model:
            return self.usage_stats.get(model, {})
        return self.usage_stats
    
    def generate_embeddings(self, texts: List[str], model: str = "nomic-embed-text") -> Optional[List[List[float]]]:
        """
        Generate embeddings for the given texts.
        """
        try:
            url = f"{self.ollama_url}/api/embeddings"
            embeddings = []
            
            for text in texts:
                payload = {
                    "model": model,
                    "prompt": text
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    embeddings.append(result.get("embedding", []))
                else:
                    return None
            
            return embeddings
        
        except requests.exceptions.RequestException as e:
            print(f"Embedding request failed: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error during embedding: {str(e)}")
            return None
    
    def evaluate_response_quality(self, original_prompt: str, ai_response: str) -> Dict[str, float]:
        """
        Evaluate the quality of an AI response against the original prompt.
        """
        # Basic evaluation metrics
        response_length = len(ai_response.strip())
        prompt_coverage = self._calculate_prompt_coverage(original_prompt, ai_response)
        coherence_score = self._calculate_coherence_score(ai_response)
        
        return {
            "length_score": min(response_length / 100, 1.0),  # Normalize to 0-1
            "prompt_coverage": prompt_coverage,
            "coherence_score": coherence_score,
            "overall_quality": (prompt_coverage + coherence_score) / 2
        }
    
    def _calculate_prompt_coverage(self, prompt: str, response: str) -> float:
        """
        Calculate how well the response addresses the prompt.
        """
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        
        if not prompt_words:
            return 1.0  # If no prompt words, consider fully covered
        
        matching_words = prompt_words.intersection(response_words)
        coverage = len(matching_words) / len(prompt_words)
        
        return min(coverage, 1.0)
    
    def _calculate_coherence_score(self, response: str) -> float:
        """
        Calculate coherence/sense-making score of the response.
        """
        # Simple heuristic: ratio of meaningful sentences to total sentences
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        
        if not sentences:
            return 0.0
        
        meaningful_sentences = 0
        for sentence in sentences:
            # A sentence is meaningful if it has at least 3 words and some content
            words = sentence.split()
            if len(words) >= 3 and any(c.isalnum() for c in sentence):
                meaningful_sentences += 1
        
        return meaningful_sentences / len(sentences)
    
    def batch_generate_responses(self, prompts: List[str], model: str = None, 
                                temperature: float = 0.7) -> List[Optional[Dict[str, Any]]]:
        """
        Generate responses for multiple prompts efficiently.
        """
        results = []
        for prompt in prompts:
            result = self.generate_response(prompt, model, temperature)
            results.append(result)
        
        return results
    
    def clear_cache(self):
        """
        Clear the response cache.
        """
        self.response_cache.clear()
    
    def get_cached_entries_count(self) -> int:
        """
        Get the number of cached entries.
        """
        # Remove expired entries first
        now = datetime.utcnow()
        expired_keys = [
            key for key, value in self.response_cache.items()
            if now >= value["expires_at"]
        ]
        
        for key in expired_keys:
            del self.response_cache[key]
        
        return len(self.response_cache)