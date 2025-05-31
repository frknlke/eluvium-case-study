import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import base64
import email
from typing import List, Dict, Optional
import os

class GmailEmailRetriever:
    def __init__(self, email_address: str, refresh_token: str, token_expiry: datetime.datetime):
        """
        Initialize Gmail client with OAuth credentials
        
        Args:
            email_address: The Gmail address
            refresh_token: OAuth refresh token
            token_expiry: Token expiry datetime
        """
        self.email_address = email_address
        self.refresh_token = refresh_token
        self.token_expiry = token_expiry
        self.service = None
        
    def _get_credentials(self) -> Credentials:
        """Create and refresh OAuth2 credentials"""
        # Use the Google OAuth credentials from environment variables or hard-coded values
        client_id = os.getenv('GOOGLE_CLIENT_ID', '576019191668-4kcfq8ukau22qvghjo2223t3pbjo904u.apps.googleusercontent.com')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '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')
        
        creds = Credentials(
            token=None,  # Will be refreshed
            refresh_token=self.refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/gmail.readonly']
        )
        
        # Refresh the token if needed
        if not creds.valid:
            creds.refresh(Request())
            
        return creds
    
    def _initialize_service(self):
        """Initialize Gmail API service"""
        if not self.service:
            creds = self._get_credentials()
            self.service = build('gmail', 'v1', credentials=creds)
    
    def get_emails_last_hour(self) -> List[str]:
        """
        Retrieve all emails received in the last hour as raw email strings.
        Only fetches emails in the INBOX (where the user is the receiver).
        
        Returns:
            List of raw email strings in RFC822 format
        """
        self._initialize_service()
        
        # Calculate timestamp for one hour ago
        one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        timestamp = int(one_hour_ago.timestamp())
        
        try:
            # Search for messages received in the inbox after the timestamp
            query = f'in:inbox after:{timestamp}'
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10  # Adjust as needed
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return []
            
            # Get raw emails for each message
            raw_emails = []
            for msg in messages:
                raw_email = self._get_raw_email(msg['id'])
                if raw_email:
                    raw_emails.append(raw_email)
            
            return raw_emails
            
        except Exception as e:
            print(f"Error retrieving emails: {str(e)}")
            return []
    
    def _get_raw_email(self, message_id: str) -> Optional[str]:
        """
        Get raw email content in RFC822 format
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Raw email string in RFC822 format
        """
        try:
            # Get the raw message in RFC822 format
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='raw'
            ).execute()
            
            # Decode the raw message
            raw_email = base64.urlsafe_b64decode(
                message['raw']
            ).decode('utf-8', errors='replace')
            
            return raw_email
            
        except Exception as e:
            print(f"Error getting raw email for {message_id}: {str(e)}")
            return None
    
    def _get_header_value(self, headers: List[Dict], name: str) -> str:
        """Extract header value by name"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
        else:
            # Single part message
            if payload['mimeType'] in ['text/plain', 'text/html']:
                if 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(
                        payload['body']['data']
                    ).decode('utf-8')
        
        return body
    
  