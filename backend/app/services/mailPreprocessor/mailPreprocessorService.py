# Preprocess the emails
# -> Clears any html tags in the email body
# -> Removes quoted replies and forwarded text
# -> Clears signatures from the email body (if any)
import re
from bs4 import BeautifulSoup
from email import message_from_string
from email.header import decode_header
from typing import Dict, Any, Union, Optional

def clean_email(raw_email: str) -> Dict[str, str]:
    """
    Process raw email to extract and clean key components.
    
    Args:
        raw_email: Raw email content in RFC822 format
        
    Returns:
        Dictionary with cleaned email components:
        - subject: Email subject
        - from: Sender information
        - body: Cleaned email body text
        - date: Date of the email
        - to: Recipient information
        - sender_email: Verified sender email from SPF header
    """
    if not raw_email:
        return {
            "subject": "",
            "from": "",
            "body": "",
            "date": "",
            "to": "",
            "sender_email": ""
        }
    
    # Parse the email
    try:
        msg = message_from_string(raw_email)
        
        # Extract and decode headers
        subject = decode_email_header(msg.get('Subject', ''))
        sender = decode_email_header(msg.get('From', ''))
        date = msg.get('Date', '')
        to = decode_email_header(msg.get('To', ''))
        
        # Extract the verified sender email from SPF header
        sender_email = extract_verified_sender(raw_email)
        
        # Extract the body
        body = extract_body_from_message(msg)
        
        # Clean the body text
        cleaned_body = clean_body_text(body)
        
        return {
            "subject": subject,
            "from": sender,
            "body": cleaned_body,
            "date": date,
            "to": to,
            "sender_email": sender_email
        }
    except Exception as e:
        print(f"Error processing email: {str(e)}")
        return {
            "subject": "",
            "from": "",
            "body": raw_email,  # Return raw email as fallback
            "date": "",
            "to": "",
            "sender_email": "",
            "error": str(e)
        }

def decode_email_header(header: str) -> str:
    """
    Decode email headers that may contain encoded words.
    
    Args:
        header: Encoded email header
        
    Returns:
        Decoded header text
    """
    if not header:
        return ""
    
    try:
        parts = decode_header(header)
        decoded_parts = []
        
        for part, encoding in parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_parts.append(part.decode(encoding or 'utf-8', errors='replace'))
                else:
                    decoded_parts.append(part.decode('utf-8', errors='replace'))
            else:
                decoded_parts.append(part)
                
        return ''.join(decoded_parts)
    except Exception as e:
        print(f"Error decoding header: {str(e)}")
        return header  # Return original header as fallback

def extract_verified_sender(raw_email: str) -> str:
    """
    Extract the verified sender email from SPF header.
    
    Args:
        raw_email: Raw email content in RFC822 format
        
    Returns:
        Verified sender email from smtp.mailfrom field or empty string if not found
    """
    try:
        # Look for SPF header with smtp.mailfrom
        spf_pattern = r'smtp\.mailfrom=([^\s;>]+)'
        spf_match = re.search(spf_pattern, raw_email)
        
        if spf_match:
            return spf_match.group(1)
        
        # Fallback to Authentication-Results header
        auth_pattern = r'Authentication-Results:.*?smtp\.mailfrom=([^\s;>]+)'
        auth_match = re.search(auth_pattern, raw_email, re.DOTALL)
        
        if auth_match:
            return auth_match.group(1)
            
        return ""
    except Exception as e:
        print(f"Error extracting verified sender: {str(e)}")
        return ""

def extract_body_from_message(msg) -> str:
    """
    Extract body text from an email.message object
    Prioritizes plain text over HTML to avoid duplication
    """
    body = ""
    
    # Handle multipart messages
    if msg.is_multipart():
        # First try to find text/plain parts
        plain_text_body = ""
        html_body = ""
        
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            
            # Skip attachments
            if "attachment" in content_disposition:
                continue
            
            # Get the payload
            payload = part.get_payload(decode=True)
            if payload:
                # Convert bytes to string
                charset = part.get_content_charset() or 'utf-8'
                try:
                    decoded_payload = payload.decode(charset, errors='replace')
                except:
                    decoded_payload = payload.decode('utf-8', errors='replace')
                
                if content_type == 'text/plain':
                    plain_text_body += decoded_payload
                elif content_type == 'text/html':
                    # Extract text from HTML
                    soup = BeautifulSoup(decoded_payload, 'html.parser')
                    html_body += soup.get_text()
        
        # Prioritize plain text over HTML
        if plain_text_body:
            body = plain_text_body
        elif html_body:
            body = html_body
    else:
        # Handle single-part messages
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or 'utf-8'
            try:
                body = payload.decode(charset, errors='replace')
            except:
                body = payload.decode('utf-8', errors='replace')
            
            # If it's HTML, extract text
            if msg.get_content_type() == 'text/html':
                soup = BeautifulSoup(body, 'html.parser')
                body = soup.get_text()
    
    return body

def clean_body_text(body: str) -> str:
    """
    Clean body text content while preserving original formatting as much as possible
    """
    if not body:
        return ""
        
    # Convert literal newline text to actual newlines if they exist
    body = body.replace('\\n', '\n')
    
    # Remove quoted replies and forwarded text
    QUOTE_PATTERNS = [
        r"(?i)^-----\s*Original Message\s*-----.*",
        r"(?i)^From:\s+.*",
        r"(?i)^Sent:\s+.*",
        r"(?i)^To:\s+.*",
        r"(?i)^Subject:\s+.*",
        r"(?i)^On\s+.*wrote:$",
        r"(?i)^\s*>.*$"  # Lines starting with >
    ]
    for pattern in QUOTE_PATTERNS:
        body = re.sub(pattern, '', body, flags=re.MULTILINE)

    # Remove signatures using a common delimiter or heuristics
    signature_delimiters = ['-- ', 'Regards,', 'Best regards,', 'Thanks,', 'Sincerely,']
    for delimiter in signature_delimiters:
        if delimiter in body:
            body = body.split(delimiter)[0]

    # Remove image references or non-text
    body = re.sub(r'cid:\S+|<img[^>]*>|http\S+|\[image:.*?\]', '', body)
    
    # Normalize line endings
    body = body.replace('\r\n', '\n')
    
    # Remove duplicate paragraphs that often appear in emails
    lines = body.split('\n')
    unique_lines = []
    
    # Simple deduplication for adjacent identical lines
    prev_line = None
    for line in lines:
        if line != prev_line:
            unique_lines.append(line)
        prev_line = line
    
    body = '\n'.join(unique_lines)
    
    # Do NOT lowercase the text to preserve original capitalization
    
    # Collapse excess whitespace but preserve newlines
    body = re.sub(r' {2,}', ' ', body)  # Multiple spaces to single space
    body = re.sub(r'\n{3,}', '\n\n', body)  # More than 2 newlines to double newline
    
    return body.strip()