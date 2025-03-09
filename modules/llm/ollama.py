"""
Ollama integration module.
Handles communication with local Ollama API for LLM inference.
"""

import requests
import json
from loguru import logger

class OllamaClient:
    """Client for interacting with the local Ollama API."""
    
    def __init__(self, api_url, model, timeout=30):
        """
        Initialize the Ollama client.
        
        Args:
            api_url (str): Ollama API URL (typically http://localhost:11434/api)
            model (str): Model to use for inference (e.g., llama2, mistral)
            timeout (int): Timeout for API requests in seconds
        """
        self.api_url = api_url
        self.generate_url = f"{self.api_url}/generate"
        self.model = model
        self.timeout = timeout
        logger.debug(f"Initialized Ollama client with model: {model}")
    
    def check_availability(self):
        """
        Check if Ollama API is available.
        
        Returns:
            bool: True if available, False otherwise
        """
        try:
            # Try to connect to Ollama API's base endpoint
            base_url = self.api_url.replace('/api', '')
            response = requests.get(f"{base_url}/", timeout=5)
            
            if response.status_code == 200:
                logger.info("Ollama API is available")
                return True
            else:
                logger.error(f"Ollama API returned status code {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Error connecting to Ollama API: {str(e)}")
            return False
    
    def generate_response(self, prompt, system_prompt=None):
        """
        Generate a response using the Ollama API.
        
        Args:
            prompt (str): User prompt
            system_prompt (str, optional): System prompt
            
        Returns:
            str: Generated response text
            
        Raises:
            Exception: If the API call fails
        """
        combined_prompt = prompt
        if system_prompt:
            combined_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": combined_prompt,
            "stream": False,
            "temperature": 0.0  # Lower temperature for more deterministic responses
        }
        
        try:
            logger.debug(f"Sending request to Ollama API with model: {self.model}")
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                # Extract the response text from the completion
                response_text = result.get("response", "").strip()
                logger.debug("Successfully received response from Ollama")
                return response_text
            else:
                logger.error(f"Ollama API returned status code {response.status_code}")
                logger.error(f"Response: {response.text}")
                raise Exception(f"Ollama API error: {response.text}")
                
        except requests.RequestException as e:
            logger.error(f"Request exception when calling Ollama: {str(e)}")
            raise Exception(f"Failed to communicate with Ollama: {str(e)}")