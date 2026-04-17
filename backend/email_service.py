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
         .html(f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Reset your password</title>
  </head>
  <body style="margin:0; padding:0; background-color:#f4f4f7; font-family:Arial, Helvetica, sans-serif; color:#222222;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%; background-color:#f4f4f7; margin:0; padding:24px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; background-color:#ffffff; border-radius:8px;">
            <tr>
              <td style="padding:32px 32px 16px 32px;">
                <h1 style="margin:0; font-size:24px; line-height:32px; color:#111111;">
                  Reset your password
                </h1>
              </td>
            </tr>

            <tr>
              <td style="padding:0 32px 16px 32px; font-size:16px; line-height:24px; color:#444444;">
                We received a request to reset the password for your account.
              </td>
            </tr>

            <tr>
              <td style="padding:0 32px 24px 32px; font-size:16px; line-height:24px; color:#444444;">
                Click the button below to choose a new password.
              </td>
            </tr>

            <tr>
              <td align="center" style="padding:0 32px 32px 32px;">
                <a href="{reset_url}"
                   style="display:inline-block; padding:14px 24px; background-color:#111111; color:#ffffff; text-decoration:none; font-size:16px; font-weight:bold; border-radius:6px;">
                  Reset Password
                </a>
              </td>
            </tr>

            <tr>
              <td style="padding:0 32px 12px 32px; font-size:14px; line-height:22px; color:#666666;">
                This link will expire in 30 minutes.
              </td>
            </tr>

            <tr>
              <td style="padding:0 32px 16px 32px; font-size:14px; line-height:22px; color:#666666;">
                If you did not request a password reset, you can safely ignore this email. Your password will not change unless this link is used.
              </td>
            </tr>

            <tr>
              <td style="padding:0 32px 12px 32px; font-size:14px; line-height:22px; color:#666666;">
                If the button does not work, copy and paste this link into your browser:
              </td>
            </tr>

            <tr>
              <td style="padding:0 32px 32px 32px; font-size:14px; line-height:22px; word-break:break-all;">
                <a href="{reset_url}" style="color:#1a73e8; text-decoration:underline;">
                  {reset_url}
                </a>
              </td>
            </tr>
          </table>

          <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%;">
            <tr>
              <td style="padding:16px 24px; text-align:center; font-size:12px; line-height:18px; color:#888888;">
                This is an automated message. Please do not reply.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
""")
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
        .html(f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Your username</title>
  </head>
  <body style="margin:0; padding:0; background-color:#f4f4f7; font-family:Arial, Helvetica, sans-serif; color:#222222;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%; background-color:#f4f4f7; margin:0; padding:24px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%; background-color:#ffffff; border-radius:8px;">
            <tr>
              <td style="padding:32px 32px 16px 32px;">
                <h1 style="margin:0; font-size:24px; line-height:32px; color:#111111;">
                  Your username
                </h1>
              </td>
            </tr>

            <tr>
              <td style="padding:0 32px 16px 32px; font-size:16px; line-height:24px; color:#444444;">
                We received a request to remind you of your username.
              </td>
            </tr>

            <tr>
              <td style="padding:0 32px 24px 32px; font-size:16px; line-height:24px; color:#444444;">
                Your username is:
              </td>
            </tr>

            <tr>
              <td align="center" style="padding:0 32px 32px 32px;">
                <div style="display:inline-block; padding:14px 24px; background-color:#f0f0f0; color:#111111; font-size:18px; font-weight:bold; border-radius:6px;">
                  {username}
                </div>
              </td>
            </tr>

            <tr>
              <td style="padding:0 32px 16px 32px; font-size:14px; line-height:22px; color:#666666;">
                If you did not request this email, you can safely ignore it.
              </td>
            </tr>
          </table>

          <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width:600px; width:100%;">
            <tr>
              <td style="padding:16px 24px; text-align:center; font-size:12px; line-height:18px; color:#888888;">
                This is an automated message. Please do not reply.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
""")
         .build())
    
    try:
        response = ms.emails.send(email)
        print(f"Email response: {response.status_code}")

    except Exception as e:
        logger.exception(f"ERROR: {e}")
        raise auth.FailedToSend
