# ======================================================
# EXTERNAL IMPORTS
# ======================================================


import logging
from mailersend import MailerSendClient, EmailBuilder
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


# ======================================================
# LOAD .env
# ======================================================


backend = Path(__file__).resolve().parent
env_path = backend / ".env"
load_dotenv(env_path, override=True)


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.exceptions import auth


# ======================================================
# MAILERSEND BASIC CODE
# ======================================================


PROTOCOL = "http://"                 # use https once live on service provider
DOMAIN = "127.0.0.1:8000"            # This domain should be the front-end domain
ROUTE = "/frontend/pages/reset-password.html"       # this route should be the front-end UI landing page


def send_password_reset_link(recipient_email, token) -> None:

    reset_url = f"{PROTOCOL}{DOMAIN}{ROUTE}?token={token}"

    ms = MailerSendClient()

    email = (EmailBuilder()
         .from_email("noreply@test-r9084zv6q6jgw63d.mlsender.net", "Nelson Rengifo")
         .to_many([{"email": recipient_email}])
         .subject("Reset Password Link")
         .html(f'Click here to reset password: <a href="{reset_url}">{reset_url}</a>')
         .build())
    
    try:
        response = ms.emails.send(email)
        print(f"Email response: {response.status_code}")

    except Exception as e:
        logger.exception(f"ERROR: {e}")
        raise auth.FailedToSend
    

def send_username_email(recipient_email, username) -> None:

    ms = MailerSendClient()

    email = (EmailBuilder()
         .from_email("noreply@test-r9084zv6q6jgw63d.mlsender.net", "Nelson Rengifo")
         .to_many([{"email": recipient_email}])
         .subject("Username recovery")
         .html(f'<p>Your username is: <strong>{username}</strong></p>')
         .build())
    
    try:
        response = ms.emails.send(email)
        print(f"Email response: {response.status_code}")

    except Exception as e:
        logger.exception(f"ERROR: {e}")
        raise auth.FailedToSend
