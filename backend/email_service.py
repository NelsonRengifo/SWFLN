# ======================================================
# EXTERNAL IMPORTS
# ======================================================


import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.exceptions import auth


# ======================================================
# SENDGRID BASIC CODE
# ======================================================

PROTOCOL = "https://"
DOMAIN = "127.0.0.1"            # This domain should be the front-end domain
ROUTE = "/auth/reset-password"  # this route should be the front-end UI landing page


def send_password_reset_link(recipient_email, token) -> None:

    reset_url = f"{PROTOCOL}{DOMAIN}{ROUTE}?token={token}"

    message = Mail(
        from_email='nrengifo2468@eagle.fgcu.edu',
        to_emails=recipient_email,
        subject='Reset Password Link',
        html_content=f'Click here to reset password: <a href="{reset_url}">{reset_url}</a>')

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg.send(message)

    except Exception:
        raise auth.FailedToSend
    

def send_username_email(recipient_email, username) -> None:

    message = Mail(
        from_email='nrengifo2468@eagle.fgcu.edu',
        to_emails=recipient_email,
        subject='Username recovery',
        html_content=f'<p>Your username is: <strong>{username}</strong></p>')

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg.send(message)

    except Exception:
        raise auth.FailedToSend


# Brevo (formerly Sendinblue) – free tier supports up to ~300 emails/day which is more than enough for occasional transactional sends.

# Mailjet – free API tier with up to 6,000 emails/month.

# Mailgun – has a free tier that allows 100 emails/day via API/SMTP.

# SendPulse – free tier described with relatively generous monthly volume.

# Postmark (Developer tier) – free 100 emails/month forever (good for very low volume).

# SENDGRID TRIAL ENDS APRIL 8TH 2026
