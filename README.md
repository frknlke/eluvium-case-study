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

## Setup and Running

See the respective README files in the [frontend](./frontend/README.md) and [backend](./backend/README.md) directories for setup and running instructions.