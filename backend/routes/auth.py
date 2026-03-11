# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from fastapi import APIRouter, HTTPException, Depends, status
import logging

logger = logging.getLogger(__name__)


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend import services
from backend.core.database_config import get_db
from backend import schemas
from backend.exceptions import auth
from backend import email_service
from backend.routes.dependencies.auth_dependencies import session_token


# ======================================================
# ROUTE PACKAGE
# ======================================================


auth_route = APIRouter(prefix='/auth')


# ======================================================
# LOGIN ROUTE
# ======================================================


@auth_route.post("/login", status_code=200)
def login(payload: schemas.Credentials, db=Depends(get_db)):

    try:
        user_id = services.verify_credentials(db, payload)
        token = services.create_token(db, user_id)
        return {"token": token, "token_type": "bearer"}

    except auth.InvalidCredentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")


# ======================================================
# LOGOUT ROUTE
# ======================================================


@auth_route.post("/logout", status_code=204)
def logout(db=Depends(get_db), token=Depends(session_token)):

    try:
        session = services.authenticate_token(db, token)
        services.delete_token(db, session.token_hash)

    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")


# ======================================================
# REGISTER ROUTE
# ======================================================


@auth_route.post("/register", status_code=201)
def register(payload: schemas.Registration, db=Depends(get_db), token=Depends(session_token)):

    valid_roles = ["super admin"]

    try:
        session = services.authenticate_token(db, token)
        services.has_valid_role(db, session.token_hash, valid_roles)
        user_id = services.register_user(db, payload)
        return {"status": "ok", "user_id": user_id}

    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")

    except auth.InvalidRole:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user is unauthorized for this route")

    except auth.InvalidUserRole:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user role is not valid")

    except auth.InvalidUsername:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="alphanumeric characters only")

    except auth.InvalidPassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="failed password requirements")

    except auth.UsernameTaken:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username already exists")

    except auth.EmailTaken:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email already exists")

    except auth.FailedToHash:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Hashing error")


# ======================================================
# UPDATE PASSWORD ROUTE (USER AUTHENTICATED)
# ======================================================


@auth_route.post("/update/password", status_code=204)
def update_password(payload: schemas.UpdatePassword, db=Depends(get_db), token=Depends(session_token)):

    try:
        session = services.authenticate_token(db, token)
        services.confirm_password(db, payload.current_password, session.user_id)
        services.enforce_password_policy(db, payload.new_password, session.user_id)
        services.change_user_password(db, payload.new_password, session.user_id)

    except (auth.InvalidCredentials, auth.PasswordsMatch, auth.InvalidPassword):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")

    except auth.FailedToHash:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Hashing error")


# ======================================================
# UPDATE USERNAME ROUTE (USER AUTHENTICATED)
# ======================================================


@auth_route.post("/update/username", status_code=204)
def update_username(payload: schemas.UpdateUsername, db=Depends(get_db), token=Depends(session_token)):

    try:
        session = services.authenticate_token(db, token)
        services.change_user_username(db, payload.new_username, session.user_id)

    except auth.InvalidCredentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    except auth.InvalidUsername:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="alphanumeric characters only")

    except auth.UsernameTaken:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username already exists")


# ======================================================
# FORGOT PASSWORD ROUTE (USER NOT AUTHENTICATED)
# ======================================================


@auth_route.post("/forgot-password", status_code=204)
def forgot_password(payload: schemas.ForgotPassword, db=Depends(get_db)):

    try:
        token = services.get_password_reset_token(db, payload.email)
        email_service.send_password_reset_link(payload.email, token)

    except auth.FailedToSend:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email")

    except auth.EmailNotFound:
        pass


# ======================================================
# RESET PASSWORD ROUTE (USER NOT AUTHENTICATED)
# ======================================================


@auth_route.post("/reset-password", status_code=204)
def reset_password(payload: schemas.ResetPassword, db=Depends(get_db)):

    try:
        session = services.authenticate_reset_token(db, payload.reset_token)
        services.reset_password(db, payload.new_password, session.user_id)

    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")

    except auth.InvalidPassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="failed password requirements")

    except auth.PasswordsMatch:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    except auth.FailedToHash:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Hashing error")
