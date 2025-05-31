import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'eluvium'),
    'user': os.getenv('DB_USER', 'frknlke_eluvium'),
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