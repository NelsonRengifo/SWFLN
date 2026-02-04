from backend import queries, validators
from argon2 import exceptions
import logging

logger = logging.getLogger(__name__)

# ======================================================
# CONFIRMS IF USERNAME & PASSWORD EXISTS IN DB
# ======================================================


def has_credentials(db, username, plain_password) -> bool:

    stored_password = queries.get_user_password_by_username(db, username)
    if not stored_password:
        return False
    try:
        validators.verify_password(plain_password, stored_password)
        return True
    except (exceptions.VerifyMismatchError, exceptions.VerificationError, exceptions.InvalidHashError) as e:
        logger.warning(f"Failed password attempt for username: {username} | error: {e}")
        return False
