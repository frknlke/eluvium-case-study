from fastapi import APIRouter, HTTPException, status
from ..models.mailbox import MailboxCreate, MailboxResponse
from ..database import db as db_client
from ..services import flowOrchestration as orchestrator
from typing import List
import datetime
import uuid

router = APIRouter(
    prefix="/api/mailbox",
    tags=["mailboxes"]
)

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_mailbox(mailbox: MailboxCreate):
    """Create a new mailbox entry with OAuth credentials."""
    try:
        # Generate a company UUID if not provided
        if not mailbox.company_id:
            mailbox.company_id = str(uuid.uuid4())
        
        # Convert token_expiry to proper format if present
        token_expiry = None
        if mailbox.token_expiry:
            token_expiry = mailbox.token_expiry
        
        # Save to database
        mailbox_id = db_client.save_mailbox_credentials(
            mailbox.company_id,
            mailbox.email_address,
            mailbox.provider.value,
            mailbox.access_token,
            mailbox.refresh_token,
            token_expiry,
            mailbox.sync_method.value
        )
        
        return {
            "message": "Mailbox credentials saved successfully",
            "id": mailbox_id,
            "company_id": mailbox.company_id  # Return the generated company ID
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save mailbox credentials: {str(e)}"
        )

@router.get("/", response_model=List[MailboxResponse])
async def list_mailboxes():
    """Get all mailboxes."""
    try:
        mailboxes = db_client.get_mailboxes()
        
        # Format the results
        formatted_mailboxes = []
        for mailbox in mailboxes:
            formatted_mailboxes.append({
                "id": mailbox["id"],
                "company_id": mailbox["company_id"],
                "email_address": mailbox["email_address"],
                "provider": mailbox["provider"],
                "sync_method": mailbox["sync_method"],
                "sync_status": mailbox["sync_status"],
                "last_synced_at": mailbox["last_synced_at"],
                "created_at": mailbox["created_at"],
                "updated_at": mailbox["updated_at"]
            })
        
        return formatted_mailboxes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch mailboxes: {str(e)}"
        )

@router.get("/{mailbox_id}", response_model=MailboxResponse)
async def get_mailbox(mailbox_id: str):
    """Get a specific mailbox by ID."""
    try:
        mailbox = db_client.get_mailbox_by_id(mailbox_id)
        
        if not mailbox:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mailbox not found"
            )
        
        return {
            "id": mailbox["id"],
            "company_id": mailbox["company_id"],
            "email_address": mailbox["email_address"],
            "provider": mailbox["provider"],
            "sync_method": mailbox["sync_method"],
            "sync_status": mailbox["sync_status"],
            "last_synced_at": mailbox["last_synced_at"],
            "created_at": mailbox["created_at"],
            "updated_at": mailbox["updated_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch mailbox: {str(e)}"
        )

@router.post("/trigger-email-processing/{mailbox_id}", response_model=dict)
async def trigger_email_processing(mailbox_id: str):
    """Trigger email processing for a specific mailbox."""
    try:
        # First, check if the mailbox exists
        mailbox = db_client.get_mailbox_connection_info(mailbox_id)
        
        if not mailbox:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mailbox not found"
            )
        
        print(mailbox)

        orchestrator.init_mail_fetcher(
            mailbox["email_address"], mailbox["refresh_token"], 
            mailbox["token_expiry"], mailbox["provider"]
            )
        
        # This is a dummy function - no actual processing is done now
        # In a real implementation, you would trigger background processing here
        
        return {
            "message": "Email processing triggered successfully",
            "mailbox_id": mailbox_id,
            "status": "processing"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger email processing: {str(e)}"
        ) 