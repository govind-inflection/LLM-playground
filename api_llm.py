import requests
import json
from typing import Dict, Any, Optional, List

class LLMAPI:
    def __init__(self, api_url: str, api_key: str, model_name: str):
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def generate_response(self, conversation: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 500) -> str:
        """
        Generate a response from the LLM using direct API calls with conversation history
        """
        return self._llm_request(conversation, temperature, max_tokens)

    def _llm_request(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> str:
        """Handle LLM API requests with chat history"""
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"LLM API request failed: {response.text}")

def create_model(model_name: str, api_url: str, api_key: str, temperature: float = 0.7, max_tokens: int = 100) -> LLMAPI:
    """
    Create a new LLM API instance
    """
    return LLMAPI(api_url, api_key, model_name)

def generate_answer(llm: LLMAPI, conversation: List[Dict[str, str]]) -> str:
    """
    Generate an answer using the LLM with conversation history
    """
    return llm.generate_response(conversation) 