import datetime

from .providers.gmailMailFetcher import GmailEmailRetriever
# TODO: Add other providers here

class EmailClientFactory:
    @staticmethod
    def get_client(provider, email_address, refresh_token, token_expiry):
        if provider == "gmail":
            return GmailEmailRetriever(email_address, refresh_token, token_expiry)
        elif provider == "outlook":
            # TODO: Implement Outlook email retrieval
            # return OutlookEmailRetriever(email_address, refresh_token, token_expiry)
            return None
        elif provider == "yahoo":
            # TODO: Implement Yahoo email retrieval
            return None
        else:
            raise ValueError(f"Unsupported email provider: {provider}")

class MailFetcher:
    def __init__(self, email_address: str, refresh_token: str, token_expiry: datetime.datetime, provider: str):
        self.email_address = email_address
        self.refresh_token = refresh_token
        self.token_expiry = token_expiry
        self.client = None

        self.client = EmailClientFactory.get_client(provider, email_address, refresh_token, token_expiry)
        
        