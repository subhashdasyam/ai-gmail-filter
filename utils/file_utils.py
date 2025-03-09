"""
File utilities module.
Handles file operations for the application.
"""

import os
import json
import time
from loguru import logger

def ensure_directory_exists(directory):
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory (str): Directory path
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not directory:
        return True
        
    try:
        if not os.path.exists(directory):
            logger.debug(f"Creating directory: {directory}")
            os.makedirs(directory)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {str(e)}")
        return False

def save_results(emails_processed, unnecessary_emails, results_dir=None):
    """
    Save processing results to a JSON file.
    
    Args:
        emails_processed (list): List of all processed emails
        unnecessary_emails (list): List of emails marked as unnecessary
        results_dir (str, optional): Directory to save results
        
    Returns:
        str: Path to the saved file
    """
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_processed': len(emails_processed),
        'unnecessary_count': len(unnecessary_emails),
        'unnecessary_emails': unnecessary_emails
    }
    
    # Create timestamp for filename
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"email_results_{timestamp}.json"
    
    # Ensure directory exists if specified
    if results_dir:
        ensure_directory_exists(results_dir)
        file_path = os.path.join(results_dir, filename)
    else:
        file_path = filename
    
    try:
        with open(file_path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving results to {file_path}: {str(e)}")
        # Fallback to current directory
        fallback_path = filename
        try:
            with open(fallback_path, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to fallback path: {fallback_path}")
            return fallback_path
        except Exception as inner_e:
            logger.error(f"Error saving results to fallback path: {str(inner_e)}")
            return None