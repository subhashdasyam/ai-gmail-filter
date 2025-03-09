"""
Gmail label operations module.
Handles creation and management of labels.
"""

import time
from googleapiclient.errors import HttpError
from loguru import logger

def ensure_label_exists(service, label_name, user_id='me', retry_attempts=3, retry_delay=2):
    """
    Ensure a label exists, creating it if necessary. Returns label ID.
    
    Args:
        service: Gmail API service instance
        label_name (str): Name of the label
        user_id (str): User ID, 'me' for authenticated user
        retry_attempts (int): Number of retry attempts for API calls
        retry_delay (int): Delay between retries in seconds
        
    Returns:
        str: Label ID
        
    Raises:
        Exception: If unable to ensure label exists after retries
    """
    logger.info(f"Ensuring label '{label_name}' exists")
    
    # Retry mechanism for API calls
    for attempt in range(retry_attempts):
        try:
            # List all labels
            results = service.users().labels().list(userId=user_id).execute()
            labels = results.get('labels', [])
            
            # Check if our label exists
            for label in labels:
                if label['name'] == label_name:
                    logger.info(f"Label '{label_name}' already exists with ID: {label['id']}")
                    return label['id']
            
            # If not, create it
            logger.info(f"Label '{label_name}' not found, creating it")
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            created_label = service.users().labels().create(
                userId=user_id, body=label_object
            ).execute()
            logger.info(f"Created label '{label_name}' with ID: {created_label['id']}")
            return created_label['id']
            
        except HttpError as error:
            if attempt < retry_attempts - 1:
                logger.warning(f"Error with labels (attempt {attempt+1}/{retry_attempts}): {error}")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to ensure label exists after {retry_attempts} attempts: {error}")
                raise
    
    raise Exception(f"Failed to ensure label '{label_name}' exists after multiple attempts")

def list_labels(service, user_id='me', retry_attempts=3, retry_delay=2):
    """
    List all available labels for the user.
    
    Args:
        service: Gmail API service instance
        user_id (str): User ID, 'me' for authenticated user
        retry_attempts (int): Number of retry attempts for API calls
        retry_delay (int): Delay between retries in seconds
        
    Returns:
        list: List of label objects
    """
    logger.debug("Fetching all available labels")
    
    # Retry mechanism for API calls
    for attempt in range(retry_attempts):
        try:
            results = service.users().labels().list(userId=user_id).execute()
            labels = results.get('labels', [])
            logger.debug(f"Found {len(labels)} labels")
            return labels
        except HttpError as error:
            if attempt < retry_attempts - 1:
                logger.warning(f"Error listing labels (attempt {attempt+1}/{retry_attempts}): {error}")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to list labels after {retry_attempts} attempts: {error}")
                raise
    
    return []