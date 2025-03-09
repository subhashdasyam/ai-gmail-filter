"""
Email parser utility.
Handles parsing and extraction of email content.
"""

import base64
import re
from html import unescape
from loguru import logger

def parse_email_content(message):
    """
    Parse Gmail API message into structured email content.
    
    Args:
        message (dict): Gmail API message object
        
    Returns:
        dict: Structured email content with headers and body
    """
    # Extract headers
    headers = {}
    for header in message['payload']['headers']:
        headers[header['name'].lower()] = header['value']
    
    subject = headers.get('subject', '(No Subject)')
    sender = headers.get('from', '(No Sender)')
    date = headers.get('date', '(No Date)')
    
    # Extract body
    body_html, body_text = extract_body_content(message['payload'])
    
    # Prefer plain text if available, otherwise extract text from HTML
    if body_text:
        body = body_text
    else:
        body = extract_text_from_html(body_html)
    
    # Clean up whitespace
    body = re.sub(r'\s+', ' ', body).strip()
    
    return {
        'id': message['id'],
        'subject': subject,
        'sender': sender,
        'date': date,
        'body': body,
        'labels': message.get('labelIds', []),
        'snippet': message.get('snippet', '')
    }

def extract_body_content(payload, body_html="", body_text=""):
    """
    Recursively extract HTML and text body content from email payload.
    
    Args:
        payload (dict): Gmail API message payload
        body_html (str): Accumulated HTML content
        body_text (str): Accumulated text content
        
    Returns:
        tuple: (html_content, text_content)
    """
    # If this part has content
    if 'body' in payload and 'data' in payload['body']:
        content = decode_payload(payload['body']['data'])
        mime_type = payload.get('mimeType', '')
        
        if 'text/html' in mime_type:
            body_html += content
        elif 'text/plain' in mime_type:
            body_text += content
    
    # If this part has subparts, process them recursively
    if 'parts' in payload:
        for part in payload['parts']:
            html, text = extract_body_content(part, body_html, body_text)
            body_html += html
            body_text += text
    
    return body_html, body_text

def decode_payload(data):
    """
    Decode base64url encoded payload data.
    
    Args:
        data (str): Base64url encoded string
        
    Returns:
        str: Decoded content
    """
    try:
        body_bytes = base64.urlsafe_b64decode(data)
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'ascii']
        for encoding in encodings:
            try:
                return body_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        # Fallback to ignoring errors
        return body_bytes.decode('utf-8', errors='replace')
        
    except Exception as e:
        logger.error(f"Error decoding payload: {str(e)}")
        return ""

def extract_text_from_html(html_content):
    """
    Extract readable text from HTML content.
    
    Args:
        html_content (str): HTML content
        
    Returns:
        str: Extracted text
    """
    if not html_content:
        return ""
        
    # Remove scripts, styles, and head sections
    html_content = re.sub(r'<script.*?</script>', ' ', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<style.*?</style>', ' ', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<head.*?</head>', ' ', html_content, flags=re.DOTALL)
    
    # Replace break tags with newlines
    html_content = re.sub(r'<br\s*/?>|<\/p>', '\n', html_content)
    
    # Remove all other HTML tags
    html_content = re.sub(r'<[^>]+>', ' ', html_content)
    
    # Unescape HTML entities
    html_content = unescape(html_content)
    
    # Replace multiple spaces with a single space
    html_content = re.sub(r'\s+', ' ', html_content)
    
    # Replace multiple newlines with a single newline
    html_content = re.sub(r'\n+', '\n', html_content)
    
    return html_content.strip()