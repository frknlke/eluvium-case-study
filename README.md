# Eluvium Case Study

This repository contains the case study project for Eluvium.

## Project Structure

- `/frontend` - Next.js application for Google OAuth authentication and user interface
- `/backend` - Python FastAPI backend for database operations and API endpoints

## Architecture

This project follows a client-server architecture:

1. **Frontend (Next.js)**: 
   - Handles the Google OAuth flow
   - Collects additional information via forms
   - Displays user data and connected mailboxes
   - Communicates with the backend API

2. **Backend (Python/FastAPI)**:
   - Provides RESTful API endpoints
   - Handles database operations
   - Stores OAuth credentials and mailbox information

## Google OAuth Application

The application provides a Google OAuth flow to access user mailboxes. The authentication flow includes:

1. A form to collect additional information (company ID, sync method)
2. Google OAuth authentication
3. Storage of credentials in a PostgreSQL database via the backend API
4. A dashboard to display connected mailboxes

## Database Schema

The application uses a PostgreSQL database with the following schema:

```sql
CREATE TABLE mailboxes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    provider provider_enum NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TIMESTAMP,
    last_synced_at TIMESTAMP,
    sync_method sync_method_enum,
    sync_status sync_status_enum DEFAULT 'idle',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE provider_enum AS ENUM ('google', 'microsoft', 'other');
CREATE TYPE sync_method_enum AS ENUM ('api', 'imap', 'pop3');
CREATE TYPE sync_status_enum AS ENUM ('idle', 'running', 'failed', 'completed');
```
```sql
CREATE TABLE emails (
    -- Primary key and identifiers
    email_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mailbox_id UUID NOT NULL REFERENCES mailboxes(id) ON DELETE CASCADE, -- Foreign key to mailboxes table
    email_subject VARCHAR(500),
    email_body TEXT NOT NULL,
    email_sender VARCHAR(255),
    email_recipients TEXT[], -- Array for multiple recipients
    email_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    message_id VARCHAR(255) UNIQUE, -- Original email message ID
    thread_id VARCHAR(255), -- For email thread tracking
    email_headers JSONB, -- Store full email headers as JSON
    intent VARCHAR(100), -- e.g., 'place_order', 'inquiry', 'complaint'
    customer_organization VARCHAR(255),
    producer_organization VARCHAR(255),
    people TEXT[], -- Array of person names mentioned
    extracted_date_time TIMESTAMP WITH TIME ZONE,
    products JSONB, -- Store array of product objects
    monetary_values DECIMAL[], -- Array of monetary amounts
    addresses TEXT[], -- Array of addresses
    phone_numbers VARCHAR(50)[], -- Array of phone numbers
    email_addresses VARCHAR(255)[], -- Array of email addresses found in content
    processing_status VARCHAR(50) DEFAULT 'pending', -- pending, processed, failed
    confidence_score DECIMAL(3,2), -- AI extraction confidence (0.00-1.00)
    extraction_model_version VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);
```



## Setup and Running

See the respective README files in the [frontend](./frontend/README.md) and [backend](./backend/README.md) directories for setup and running instructions.
