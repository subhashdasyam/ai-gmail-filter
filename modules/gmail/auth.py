"""
Gmail authentication module.
Handles OAuth2 authentication with Gmail API.
"""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from loguru import logger

def authenticate_gmail(scopes, credentials_file, token_file):
    """
    Authenticate with Gmail API and return service object.
    
    Args:
        scopes (list): List of OAuth scopes
        credentials_file (str): Path to credentials.json file
        token_file (str): Path to token.json file for storing credentials
        
    Returns:
        service: Authenticated Gmail API service
        
    Raises:
        FileNotFoundError: If credentials file doesn't exist
        Exception: For any other authentication errors
    """
    logger.info("Authenticating with Gmail API")
    creds = None
    
    # Check if token file exists
    if os.path.exists(token_file):
        logger.debug(f"Loading existing token from {token_file}")
        creds = Credentials.from_authorized_user_file(token_file, scopes)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.debug("Refreshing expired token")
            creds.refresh(Request())
        else:
            # Check if credentials file exists
            if not os.path.exists(credentials_file):
                logger.error(f"Credentials file not found: {credentials_file}")
                raise FileNotFoundError(
                    f"Credentials file '{credentials_file}' not found. "
                    "Please follow the setup instructions to create this file."
                )
            
            logger.info("Starting OAuth2 authorization flow")
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, scopes)
            creds = flow.run_local_server(port=0)
            logger.info("Authorization successful")
        
        # Save credentials for next run
        logger.debug(f"Saving token to {token_file}")
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    logger.info("Gmail authentication successful")
    return build('gmail', 'v1', credentials=creds)