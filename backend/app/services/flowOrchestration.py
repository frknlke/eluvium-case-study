# Import mail-fetcher
from .mailFetcher import MailFetcher
from .mailPreprocessor.mailPreprocessorService import clean_email
import datetime
import email
from email.utils import parseaddr
from typing import List, Dict
from .entityRecognition.namedEntityRecognition import EntitiyRecognizer
from ..database.db import save_email_with_entities
from .vectorStore import ChromaVectorStore
import uuid

ner = EntitiyRecognizer()
# Initialize the vector store once
vector_store = ChromaVectorStore(collection_name="emails")

def init_mail_fetcher(email_address: str, refresh_token: str, token_expiry: datetime.datetime, provider: str, mailbox_id: str = None):
    """
    Initialize the mail fetcher service and retrieve emails from the last hour
    
    Args:
        email_address: Email address of the mailbox
        refresh_token: OAuth refresh token
        token_expiry: Token expiry timestamp
        provider: Email provider (gmail, outlook, etc.)
        mailbox_id: UUID of the mailbox (if not provided, a placeholder will be used)
    """
    try:
        mail_fetcher = MailFetcher(email_address, refresh_token, token_expiry, provider)
        raw_emails = mail_fetcher.client.get_emails_last_hour()
    
        
        # Process the emails
        processed_emails = [clean_email(raw_email) for raw_email in raw_emails]
        
        print(f"Processed {len(processed_emails)} emails")
        
        # Use the provided mailbox_id or generate a placeholder
        if not mailbox_id:
            mailbox_id = str(uuid.uuid4())  # In a real scenario, this would come from the database
            print(f"Using placeholder mailbox_id: {mailbox_id}")
        
        saved_emails = []
        
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

        
        for i, email_summary in enumerate(email_summaries):
            # Extract entities using NER
            ner_result, success = ner.recognize(email_summary['email_context'])
            print("ner_result", ner_result, success)
            
            if success:
                # Prepare data for database storage
                email_data = processed_emails[i]
                
                # Generate a unique message ID if not available
                message_id = email_data.get('message_id', f"{str(uuid.uuid4())}")
                
                # Generate a thread ID if not available (in real scenario, this would be handled better)
                thread_id = email_data.get('thread_id', f"{str(uuid.uuid4())}")
                
                # Parse timestamp or use current time
                try:
                    email_timestamp = email_data.get('date', datetime.datetime.now())
                    if isinstance(email_timestamp, str):
                        email_timestamp = datetime.datetime.fromisoformat(email_timestamp.replace('Z', '+00:00'))
                except:
                    email_timestamp = datetime.datetime.now()
                
                # Extract recipients list
                recipients = []
                if 'to' in email_data and email_data['to']:
                    if isinstance(email_data['to'], list):
                        recipients = email_data['to']
                    else:
                        recipients = [email_data['to']]
                
                # Save to the PostgreSQL database
                try:
                    email_id = save_email_with_entities(
                        mailbox_id=mailbox_id,
                        email_subject=email_data.get('subject', ''),
                        email_body=email_data.get('body', ''),
                        email_sender=email_data.get('sender_email', email_data.get('from', '')),
                        email_recipients=recipients,
                        email_timestamp=email_timestamp,
                        message_id=message_id,
                        thread_id=thread_id,
                        email_headers=email_data.get('headers', {}),
                        ner_result=ner_result,
                        model_version="1.0"
                    )
                    
                    # Store the email content in the vector database with the same ID
                    if email_id:
                        try:
                            # Prepare the email content for vector storage
                            email_content = email_summary['email_context']
                            
                            # Store in Chroma with the same ID used in PostgreSQL
                            vector_store.add_email_embedding(
                                email_id=email_id,
                                email_content=email_content,
                                ner_result=ner_result
                            )
                            
                            print(f"Added email to vector store with ID: {email_id}")
                        except Exception as ve:
                            print(f"Error storing email in vector database: {str(ve)}")
                    
                    saved_emails.append(email_id)
                    print(f"Saved email to database with ID: {email_id}")
                except Exception as e:
                    print(f"Error saving email to database: {str(e)}")
        
        
        # TODO: Implement email classification
        
        return {
            "status": "success",
            # "emails_processed": len(raw_emails),
            "email_address": email_address,
            "processed_emails": processed_emails,
            "email_summaries": email_summaries,
            "saved_emails": saved_emails
        }
    except Exception as e:
        print(f"Error in mail fetcher initialization: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "email_address": email_address
        }