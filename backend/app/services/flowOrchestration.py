# Import mail-fetcher
from .mailFetcher import MailFetcher
from .mailPreprocessor.mailPreprocessorService import clean_email
from .entityRecognition.namedEntityRecognition import NamedEntityRecognition
import datetime
import email
from email.utils import parseaddr
from typing import List, Dict

def init_mail_fetcher(email_address: str, refresh_token: str, token_expiry: datetime.datetime, provider: str):
    """
    Initialize the mail fetcher service and retrieve emails from the last hour
    """
    try:
        mail_fetcher = MailFetcher(email_address, refresh_token, token_expiry, provider)
        raw_emails = mail_fetcher.client.get_emails_last_hour()
    
        
        # Process the emails
        processed_emails = [clean_email(raw_email) for raw_email in raw_emails]
        
        print(f"Processed {len(processed_emails)} emails")
        
        # Print some basic info for logging
        email_summaries = []
        for email_data in processed_emails:
            email_summaries.append({
                'subject': email_data['subject'],
                'from': email_data['from'],
                'sender_email': email_data.get('sender_email', ''),
                'body': email_data['body'],
                'email_context': email_data['subject'] + " \n" + email_data['body']
            })
        
        print(processed_emails)

        ner = NamedEntityRecognition()
        for email_summary in email_summaries:
            ner_results = ner.recognize(email_summary['email_context'])
            print(ner_results)
        
        # TODO: Implement email classification
        
        return {
            "status": "success",
            # "emails_processed": len(raw_emails),
            "email_address": email_address,
            "processed_emails": processed_emails,
            "email_summaries": email_summaries
        }
    except Exception as e:
        print(f"Error in mail fetcher initialization: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "email_address": email_address
        }