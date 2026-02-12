# ======================================================
# EXTERNAL IMPORTS
# ======================================================


import secrets
import hashlib
import logging
from argon2 import exceptions, PasswordHasher
from uuid import UUID
from sqlalchemy.engine import Row


# ======================================================
# INTERNAL IMPORTS
# ======================================================

from backend import queries, validators
from backend.schemas import Credentials, Registration
from backend.exceptions import auth


logger = logging.getLogger(__name__)
hasher = PasswordHasher()

# ======================================================
# VALIDATES LOGIN CREDENTIALS
# ======================================================


def verify_credentials(db, payload: Credentials) -> UUID:

    if not validators.validate_username(payload.username):
        raise auth.InvalidCredentials
    norm_username = validators.normalize_username(payload.username)
    row = queries.get_user_for_auth_by_username(db, norm_username)
    if not row:
        raise auth.InvalidCredentials
    try:
        validators.verify_password(payload.password, row.password_hash)
        return row.user_id
    except (exceptions.VerifyMismatchError, exceptions.VerificationError, exceptions.InvalidHashError) as e:
        logger.exception(f"Failed password attempt for username: {norm_username} | error: {e}")
        raise auth.InvalidCredentials


# ======================================================
# CREATES SESSION TOKEN
# ======================================================


def create_token(db, user_id) -> str:

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    queries.create_session_token(db, user_id, token_hash)
    return token


# ======================================================
# CREATES PASSWORD RESET TOKEN
# ======================================================


def generate_password_reset_token(db, user_id) -> str:

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    queries.create_password_reset_token(db, user_id, token_hash)
    return token


# ======================================================
# AUTHENTICATES SESSION TOKEN
# ======================================================


def authenticate_token(db, token) -> Row | None:

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    session = queries.get_session_info_by_token_hash(db, token_hash)
    if not session:
        raise auth.InvalidToken
    return session


# ======================================================
# AUTHENTICATES RESET PASSWORD TOKEN
# ======================================================


def authenticate_reset_token(db, token) -> Row | None:

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    session = queries.get_reset_session_info_by_token_hash(db, token_hash)
    if not session:
        raise auth.InvalidToken
    return session


# ======================================================
# EXTENDS SESSION TOKEN
# ======================================================


def extend_session_expiration(db, token_hash) -> None:

    queries.extend_session_expiry(db, token_hash)


# ======================================================
# DELETES SESSION TOKEN
# ======================================================


def delete_token(db, token_hash) -> str:

    row = queries.delete_session_token_by_token_hash(db, token_hash)
    if not row:
        raise auth.InvalidToken

    return row.id


# ======================================================
# REGISTERS A NEW USER
# ======================================================


def register_user(db, payload: Registration) -> UUID:

    # Username
    if not validators.validate_username(payload.username):
        raise auth.InvalidUsername
    norm_username = validators.normalize_username(payload.username)
    if queries.exists_username(db, norm_username):
        raise auth.UsernameTaken

    # Password
    if not validators.validate_password(payload.password):
        raise auth.InvalidPassword
    password_hash = ""
    try:
        password_hash = hasher.hash(payload.password)
    except exceptions.HashingError as e:
        logger.exception(f"Failed hashing for username: {payload.username} | error: {e}")
        raise auth.FailedToHash

    # Email
    norm_email = validators.normalize_email(payload.email)
    if queries.exists_email(db, norm_email):
        raise auth.EmailTaken

    # First name
    norm_first_name = validators.normalize_first_name(payload.first_name)

    # Last name
    norm_last_name = validators.normalize_last_name(payload.last_name)

    # Role
    if payload.user_role not in ["admin", "super admin"]:
        raise auth.InvalidUserRole
    user_role = payload.user_role

    # Insert user profile
    user_id = queries.create_user(db, norm_username, password_hash, norm_email, norm_first_name, norm_last_name, user_role)

    return user_id


# ======================================================
# CHECKS USER ROLE VALID FOR THE ROUTE
# ======================================================


def has_valid_role(db, token_hash, role) -> None:

    if not queries.exists_user_role(db, token_hash, role):
        raise auth.InvalidRole


# ======================================================
# VERIFY USER PASSWORD
# ======================================================


def confirm_password(db, plain_password, user_id) -> None:

    password_hash = queries.get_user_password_by_user_id(db, user_id)
    try:
        validators.verify_password(plain_password, password_hash)
    except (exceptions.VerifyMismatchError, exceptions.VerificationError, exceptions.InvalidHashError) as e:
        logger.exception(f"Failed password hash verification attempt for user: {user_id} | error: {e}")
        raise auth.InvalidCredentials


# ======================================================
# VALIDATE USER PASSWORD
# ======================================================


def enforce_password_policy(db, new_password, user_id) -> None:
    # checks that the new password passes policy checks
    if not validators.validate_password(new_password):
        raise auth.InvalidPassword
    # check new password != old password
    old_password = queries.get_user_password_by_user_id(db, user_id)
    try:
        validators.verify_password(new_password, old_password)
        raise auth.PasswordsMatch
    except exceptions.VerifyMismatchError:
        pass
    except (exceptions.VerificationError, exceptions.InvalidHashError) as e:
        logger.exception(f"Failed password hash verification attempt for user: {user_id} | error: {e}")
        raise auth.FailedToHash


# ======================================================
# UPDATE USER PASSWORD
# ======================================================


def change_user_password(db, new_password, user_id) -> None:

    try:
        password_hash = hasher.hash(new_password)
        queries.update_user_password_by_user_id(db, password_hash, user_id)
        queries.delete_sessions_by_user_id(db, user_id)
    except exceptions.HashingError as e:
        logger.exception(f"Failed hashing password for user: {user_id} | error: {e}")
        raise auth.FailedToHash


# ======================================================
# UPDATE USER USERNAME
# ======================================================


def change_user_username(db, new_username, user_id) -> None:

    if not validators.validate_username(new_username):
        raise auth.InvalidUsername
    norm_username = validators.normalize_username(new_username)
    if queries.exists_username(db, norm_username):
        raise auth.UsernameTaken
    queries.update_user_username_by_user_id(db, norm_username, user_id)


# ======================================================
# CREATE PASSWORD RESET TOKEN & CONFIRM EMAIL EXISTS
# ======================================================


def get_password_reset_token(db, email) -> str:

    norm_email = validators.normalize_email(email)
    user_id = queries.get_user_id_for_transaction_by_email(db, norm_email)
    if not user_id:
        raise auth.EmailNotFound
    return generate_password_reset_token(db, user_id)


# ======================================================
# RESET PASSWORD
# ======================================================


def reset_password(db, new_password, user_id) -> None:

    enforce_password_policy(db, new_password, user_id)

    try:
        password_hash = hasher.hash(new_password)
        queries.update_user_password_by_user_id(db, password_hash, user_id)
    except exceptions.HashingError as e:
        logger.exception(f"Failed hashing password for user: {user_id} | error: {e}")
        raise auth.FailedToHash


# ======================================================
# GET USERNAME VIA EMAIL
# ======================================================

def get_username(db, email) -> str:

    norm_email = validators.normalize_email(email)
    username = queries.get_user_username_by_email(db, norm_email)
    if not username:
        raise auth.EmailNotFound
    return username