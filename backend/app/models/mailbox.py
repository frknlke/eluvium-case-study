from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class Provider(str, Enum):
    GMAIL = 'gmail'
    OUTLOOK = 'outlook'
    IMAP = 'imap'
    AWS_SES = 'aws_ses'

class SyncMethod(str, Enum):
    API = 'api'
    IMAP = 'imap'
    WEBHOOK = 'webhook'
    MANUAL = 'manual'

class SyncStatus(str, Enum):
    IDLE = 'idle'
    SYNCING = 'syncing'
    ERROR = 'error'
    COMPLETED = 'completed'
    PAUSED = 'paused'

class MailboxCreate(BaseModel):
    company_id: Optional[str] = None
    email_address: str
    provider: Provider
    access_token: str
    refresh_token: str
    token_expiry: Optional[datetime] = None
    sync_method: SyncMethod

class Mailbox(BaseModel):
    id: str
    company_id: str
    email_address: str
    provider: Provider
    sync_method: SyncMethod
    sync_status: SyncStatus = SyncStatus.IDLE
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class MailboxResponse(BaseModel):
    id: str
    company_id: str
    email_address: str
    provider: Provider
    sync_method: SyncMethod
    sync_status: SyncStatus
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime 