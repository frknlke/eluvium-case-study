import os
import psycopg2
import json
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'eluvium_new'),
    'user': os.getenv('DB_USER', 'frknlke'),
    'password': os.getenv('DB_PASSWORD', 'frknlke_eluvium'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_connection():
    """Create a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DB_PARAMS, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise

def save_mailbox_credentials(
    company_id, 
    email_address, 
    provider, 
    access_token, 
    refresh_token, 
    token_expiry, 
    sync_method
):
    """Save mailbox credentials to the database."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                INSERT INTO mailboxes (
                    company_id, email_address, provider, access_token,
                    refresh_token, token_expiry, sync_method
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """
            values = [
                company_id,
                email_address,
                provider,
                access_token,
                refresh_token,
                token_expiry,
                sync_method
            ]
            cur.execute(query, values)
            result = cur.fetchone()
            conn.commit()
            return result['id']
    except Exception as e:
        conn.rollback()
        print(f"Error saving mailbox credentials: {e}")
        raise
    finally:
        conn.close()

def get_mailboxes():
    """Get all mailboxes from the database."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT 
                    id, company_id, email_address, 
                    provider, sync_method, sync_status, 
                    last_synced_at, created_at, updated_at
                FROM mailboxes
                ORDER BY created_at DESC
                LIMIT 100;
            """
            cur.execute(query)
            return cur.fetchall()
    except Exception as e:
        print(f"Error fetching mailboxes: {e}")
        raise
    finally:
        conn.close()

def get_mailbox_connection_info(mailbox_id: str):
    """Get information about mailbox to establish connection including refresh token"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT 
                    email_address, provider, refresh_token, token_expiry, 
                    sync_method, sync_status, last_synced_at
                FROM mailboxes
                WHERE id = %s;
            """
            cur.execute(query, [mailbox_id])
            return cur.fetchone()
    except Exception as e:
        print(f"Error fetching mailbox: {e}")
        raise
    finally:
        conn.close() 


def get_mailbox_by_id(mailbox_id):
    """Get a specific mailbox by ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT 
                    id, company_id, email_address, 
                    provider, sync_method, sync_status, 
                    last_synced_at, created_at, updated_at
                FROM mailboxes
                WHERE id = %s;
            """
            cur.execute(query, [mailbox_id])
            return cur.fetchone()
    except Exception as e:
        print(f"Error fetching mailbox: {e}")
        raise
    finally:
        conn.close() 

def save_email_with_entities(
    mailbox_id,
    email_subject,
    email_body,
    email_sender,
    email_recipients,
    email_timestamp,
    message_id,
    thread_id,
    email_headers,
    ner_result,
    model_version="1.0"
):
    """
    Save email data along with extracted entities to the emails table.
    
    Args:
        mailbox_id: UUID of the mailbox
        email_subject: Subject of the email
        email_body: Body text of the email
        email_sender: Sender email address
        email_recipients: List of recipient email addresses
        email_timestamp: Timestamp of the email
        message_id: Original email message ID
        thread_id: Thread ID for conversation tracking
        email_headers: Dictionary of email headers
        ner_result: Dictionary containing NER extraction results
        model_version: Version of the NER model used
        
    Returns:
        email_id: UUID of the saved email
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Prepare the query
            query = """
                INSERT INTO emails (
                    mailbox_id, email_subject, email_body, email_sender, 
                    email_recipients, email_timestamp, message_id, thread_id, 
                    email_headers, intent, customer_organization, producer_organization,
                    people, extracted_date_time, products, monetary_values, 
                    addresses, phone_numbers, email_addresses,
                    processing_status, confidence_score, extraction_model_version
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    'processed', 0.85, %s
                )
                RETURNING email_id;
            """
            
            # Convert date_time string to timestamp if present
            extracted_date = None
            if ner_result.get('date_time'):
                extracted_date = ner_result['date_time']
                
            # Prepare values for query
            values = [
                mailbox_id,
                email_subject,
                email_body,
                email_sender,
                email_recipients,
                email_timestamp,
                message_id,
                thread_id,
                json.dumps(email_headers) if email_headers else None,
                ner_result.get('intent'),
                ner_result.get('customer_organization'),
                ner_result.get('producer_organization'),
                ner_result.get('people', []),
                extracted_date,
                json.dumps(ner_result.get('products', [])),
                ner_result.get('monetary_values', []),
                ner_result.get('addresses', []),
                [ner_result.get('phone_number')] if ner_result.get('phone_number') else [],
                ner_result.get('email_addresses', []),
                model_version
            ]
            
            # Execute the query
            cur.execute(query, values)
            result = cur.fetchone()
            conn.commit()
            
            # Extract the UUID as a string
            if result and 'email_id' in result:
                return str(result['email_id'])
            else:
                return None
    except Exception as e:
        conn.rollback()
        print(f"Error saving email data: {e}")
        raise
    finally:
        conn.close() 