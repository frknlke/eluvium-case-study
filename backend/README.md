# Eluvium Backend API

This is a Python FastAPI backend for the Eluvium Gmail OAuth application. It handles database operations and provides API endpoints for the frontend.

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Virtual environment (recommended)

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure environment variables by creating a `.env` file with:
   ```
   # Database Configuration
   DB_NAME=eluvium
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432

   # API Configuration
   API_PORT=8000
   API_HOST=0.0.0.0
   ```

## Database

The application requires a PostgreSQL database with the following schema:

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

## Running the Application

Start the server:
```
python run.py
```

The API will be available at http://localhost:8000.

## API Endpoints

- `GET /`: Welcome message
- `GET /health`: Health check endpoint
- `POST /api/mailbox/`: Create a new mailbox with OAuth credentials
- `GET /api/mailbox/`: List all mailboxes
- `GET /api/mailbox/{mailbox_id}`: Get a specific mailbox by ID 