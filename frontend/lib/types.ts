export enum Provider {
  GMAIL = 'gmail',
  OUTLOOK = 'outlook',
  IMAP = 'imap',
  AWS_SES = 'aws_ses'
}

export enum SyncMethod {
  API = 'api',
  IMAP = 'imap',
  WEBHOOK = 'webhook',
  MANUAL = 'manual'
}

export enum SyncStatus {
  IDLE = 'idle',
  SYNCING = 'syncing',
  ERROR = 'error',
  COMPLETED = 'completed',
  PAUSED = 'paused'
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