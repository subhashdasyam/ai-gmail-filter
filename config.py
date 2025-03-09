"""
Configuration settings for the Gmail filter application.
Load environment variables from .env file if present.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gmail API settings
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', 'credentials.json')
TOKEN_FILE = os.getenv('TOKEN_FILE', 'token.json')

# Email processing settings
MAX_EMAILS = int(os.getenv('MAX_EMAILS', 100))
BODY_PREVIEW_LENGTH = int(os.getenv('BODY_PREVIEW_LENGTH', 1000))
LABEL_NAME = os.getenv('LABEL_NAME', 'potential-unnecessary')

# Ollama API settings
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
OLLAMA_TIMEOUT = int(os.getenv('OLLAMA_TIMEOUT', 30))

# API call retry settings
RETRY_ATTEMPTS = int(os.getenv('RETRY_ATTEMPTS', 3))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', 2))

# Results settings
RESULTS_DIR = os.getenv('RESULTS_DIR', 'results')

# Logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/gmail_filter.log')

# Message for validating Ollama
def check_ollama_settings():
    """Validate Ollama settings."""
    if not OLLAMA_API_URL:
        return "ERROR: Ollama API URL not set. Please check your .env file."
    if not OLLAMA_MODEL:
        return "ERROR: Ollama model not set. Please check your .env file."
    return None