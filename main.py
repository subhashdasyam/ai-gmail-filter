"""
Gmail Unnecessary Email Filter

This script connects to Gmail, analyzes emails using local Ollama API,
and moves unnecessary emails to a separate label.

Usage:
    python main.py
"""

import os
import sys
import time

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configuration
import config

# Import utilities
from utils.logging_utils import setup_logging
from utils.file_utils import ensure_directory_exists, save_results

# Import modules
from modules.gmail.auth import authenticate_gmail
from modules.gmail.email_ops import get_emails, get_email_content, move_to_label
from modules.gmail.label_ops import ensure_label_exists
from modules.llm.ollama import OllamaClient
from modules.llm.analyzer import EmailAnalyzer

from loguru import logger

def main():
    """Main function to run the email filter process."""
    # Step 1: Setup logging
    setup_logging(config.LOG_LEVEL, config.LOG_FILE)
    
    logger.info("=== Gmail Unnecessary Email Filter ===")
    
    # Step 2: Check configuration
    logger.info("Step 1: Checking configuration")
    
    # Check if credentials file exists
    if not os.path.exists(config.CREDENTIALS_FILE):
        logger.error(f"Credentials file not found: {config.CREDENTIALS_FILE}")
        logger.error("\nTo create credentials.json, follow these steps:")
        logger.error("1. Create a Google Cloud Project at https://console.cloud.google.com/")
        logger.error("2. Enable Gmail API for your project")
        logger.error("3. Create OAuth 2.0 Desktop credentials")
        logger.error("4. Download the credentials.json file and place it in the same directory as this script")
        return
    
    # Ensure results directory exists
    if config.RESULTS_DIR:
        ensure_directory_exists(config.RESULTS_DIR)
    
    # Check Ollama settings
    ollama_message = config.check_ollama_settings()
    if ollama_message:
        logger.error(ollama_message)
        return
    
    # Step 3: Initialize Ollama client
    logger.info("Step 2: Initializing Ollama client")
    ollama_client = OllamaClient(
        api_url=config.OLLAMA_API_URL,
        model=config.OLLAMA_MODEL,
        timeout=config.OLLAMA_TIMEOUT
    )
    
    # Check Ollama availability
    logger.info("Checking Ollama API availability")
    if not ollama_client.check_availability():
        logger.error(f"Cannot connect to Ollama API at {config.OLLAMA_API_URL}.")
        logger.error("Please make sure Ollama is installed and running.")
        logger.error("Install Ollama from https://ollama.ai/")
        logger.error(f"Make sure the model is pulled: ollama pull {config.OLLAMA_MODEL}")
        return
    
    # Step 4: Initialize email analyzer
    logger.info("Step 3: Initializing email analyzer")
    email_analyzer = EmailAnalyzer(
        llm_client=ollama_client,
        body_preview_length=config.BODY_PREVIEW_LENGTH
    )
    
    # Step 5: Authenticate with Gmail
    logger.info("Step 4: Connecting to Gmail")
    try:
        gmail_service = authenticate_gmail(
            scopes=config.GMAIL_SCOPES,
            credentials_file=config.CREDENTIALS_FILE,
            token_file=config.TOKEN_FILE
        )
        logger.info("Successfully connected to Gmail!")
    except Exception as e:
        logger.error(f"Error connecting to Gmail: {str(e)}")
        return
    
    # Step 6: Ensure label exists
    label_name = config.LABEL_NAME
    logger.info(f"Step 5: Ensuring label '{label_name}' exists")
    try:
        label_id = ensure_label_exists(
            service=gmail_service,
            label_name=label_name,
            retry_attempts=config.RETRY_ATTEMPTS,
            retry_delay=config.RETRY_DELAY
        )
        logger.info(f"Label ready with ID: {label_id}")
    except Exception as e:
        logger.error(f"Error creating/finding label: {str(e)}")
        return
    
    # Step 7: Get emails from inbox
    logger.info(f"Step 6: Fetching up to {config.MAX_EMAILS} emails from inbox")
    try:
        emails = get_emails(
            service=gmail_service,
            max_results=config.MAX_EMAILS,
            retry_attempts=config.RETRY_ATTEMPTS,
            retry_delay=config.RETRY_DELAY
        )
        logger.info(f"Found {len(emails)} emails to process")
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}")
        return
    
    # Step 8: Process each email
    logger.info("Step 7: Processing emails")
    logger.info("This may take some time depending on the number of emails...")
    
    emails_processed = []
    unnecessary_emails = []
    
    for i, email_msg in enumerate(emails):
        try:
            # Get email content
            email_data = get_email_content(
                service=gmail_service,
                msg_id=email_msg['id'],
                retry_attempts=config.RETRY_ATTEMPTS,
                retry_delay=config.RETRY_DELAY
            )
            
            # Print progress
            logger.info(f"Processing email {i+1}/{len(emails)}: '{email_data['subject'][:50]}...'")
            
            # Check necessity
            is_necessary = email_analyzer.check_necessity(email_data)
            
            # Store processed information
            result = {
                'id': email_msg['id'],
                'subject': email_data['subject'],
                'sender': email_data['sender'],
                'is_necessary': is_necessary
            }
            emails_processed.append(result)
            
            if not is_necessary:
                # Move to our label
                if move_to_label(
                    service=gmail_service,
                    msg_id=email_msg['id'],
                    label_id=label_id,
                    retry_attempts=config.RETRY_ATTEMPTS,
                    retry_delay=config.RETRY_DELAY
                ):
                    unnecessary_emails.append(result)
                    logger.info(f"  → Marked as unnecessary and moved to '{label_name}'")
                else:
                    logger.warning(f"  → Determined to be unnecessary, but failed to move")
            else:
                logger.info(f"  → Determined to be necessary, keeping in inbox")
                
        except Exception as e:
            logger.error(f"Error processing email {email_msg['id']}: {str(e)}")
    
    # Step 9: Save and report results
    logger.info("Step 8: Saving results")
    results_file = save_results(
        emails_processed=emails_processed,
        unnecessary_emails=unnecessary_emails,
        results_dir=config.RESULTS_DIR
    )
    
    # Final report
    logger.info("Processing complete!")
    if results_file:
        logger.info(f"Results saved to {results_file}")
    logger.info(f"Total emails processed: {len(emails_processed)}")
    logger.info(f"Unnecessary emails moved to '{label_name}': {len(unnecessary_emails)}")
    logger.info("\nPlease review the emails in this label to confirm they are indeed unnecessary.")
    logger.info(f"You can find them in Gmail under the label: {label_name}")

if __name__ == "__main__":
    main()