"""
Gmail email operations module.
Handles retrieval and modification of emails.
"""

import time
from googleapiclient.errors import HttpError
from loguru import logger
from utils.email_parser import parse_email_content

def get_emails(service, user_id='me', label_ids=None, max_results=100, retry_attempts=3, retry_delay=2):
    """
    Get emails from Gmail with specified labels.
    
    Args:
        service: Gmail API service instance
        user_id (str): User ID, 'me' for authenticated user
        label_ids (list): List of label IDs to filter by (default: ['INBOX'])
        max_results (int): Maximum number of emails to retrieve
        retry_attempts (int): Number of retry attempts for API calls
        retry_delay (int): Delay between retries in seconds
        
    Returns:
        list: List of message objects
    """
    if label_ids is None:
        label_ids = ['INBOX']
        
    logger.info(f"Fetching up to {max_results} emails with labels: {label_ids}")
    
    # Retry mechanism for API calls
    for attempt in range(retry_attempts):
        try:
            results = service.users().messages().list(
                userId=user_id, labelIds=label_ids, maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} emails")
            return messages
        except HttpError as error:
            if attempt < retry_attempts - 1:
                logger.warning(f"Error getting emails (attempt {attempt+1}/{retry_attempts}): {error}")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to get emails after {retry_attempts} attempts: {error}")
                raise
    
    return []

def get_email_content(service, msg_id, user_id='me', retry_attempts=3, retry_delay=2):
    """
    Get the content of an email with ID msg_id.
    
    Args:
        service: Gmail API service instance
        msg_id (str): Email message ID
        user_id (str): User ID, 'me' for authenticated user
        retry_attempts (int): Number of retry attempts for API calls
        retry_delay (int): Delay between retries in seconds
        
    Returns:
        dict: Email content including headers and body
    """
    logger.debug(f"Getting content for email {msg_id}")
    
    # Retry mechanism for API calls
    for attempt in range(retry_attempts):
        try:
            message = service.users().messages().get(
                userId=user_id, id=msg_id, format='full'
            ).execute()
            
            # Parse the email content
            email_data = parse_email_content(message)
            return email_data
            
        except HttpError as error:
            if attempt < retry_attempts - 1:
                logger.warning(f"Error getting email content (attempt {attempt+1}/{retry_attempts}): {error}")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to get email content after {retry_attempts} attempts: {error}")
                raise
    
    raise Exception(f"Failed to get email content for {msg_id}")

def move_to_label(service, msg_id, label_id, user_id='me', retry_attempts=3, retry_delay=2):
    """
    Move an email to a specific label and remove from inbox.
    
    Args:
        service: Gmail API service instance
        msg_id (str): Email message ID
        label_id (str): Label ID to add
        user_id (str): User ID, 'me' for authenticated user
        retry_attempts (int): Number of retry attempts for API calls
        retry_delay (int): Delay between retries in seconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.debug(f"Moving email {msg_id} to label {label_id}")
    
    # Retry mechanism for API calls
    for attempt in range(retry_attempts):
        try:
            service.users().messages().modify(
                userId=user_id,
                id=msg_id,
                body={
                    'addLabelIds': [label_id],
                    'removeLabelIds': ['INBOX']
                }
            ).execute()
            logger.debug(f"Successfully moved email {msg_id}")
            return True
        except HttpError as error:
            if attempt < retry_attempts - 1:
                logger.warning(f"Error moving email (attempt {attempt+1}/{retry_attempts}): {error}")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to move email after {retry_attempts} attempts: {error}")
                raise
    
    return False