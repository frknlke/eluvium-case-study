export enum Provider {
  GMAIL = 'gmail',
  OUTLOOK = 'outlook',
  IMAP = 'imap',
  AWS_SES = 'aws_ses'
}

export enum SyncMethod {
  POLLING = 'polling',
  WEBHOOK = 'webhook',
  IMAP_IDLE = 'imap_idle',
  SES = 'ses'
}

export enum SyncStatus {
  IDLE = 'idle',
  RUNNING = 'running',
  ERROR = 'error'
}

export interface MailboxFormData {
  syncMethod: SyncMethod;
  provider: Provider;
}

export interface Mailbox {
  id: string;
  companyId: string;
  emailAddress: string;
  provider: Provider;
  accessToken?: string;
  refreshToken?: string;
  tokenExpiry?: Date;
  lastSyncedAt?: Date;
  syncMethod: SyncMethod;
  syncStatus: SyncStatus;
  createdAt: Date;
  updatedAt: Date;
} 