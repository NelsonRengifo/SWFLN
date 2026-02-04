"""
Authentication & Authorization Routes
"""

# login
# logout
# forgot username
# forgot password
# create user (register)


# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend import services
from backend.core.database_config import get_db
from backend import schemas
from backend.exceptions import auth


# ======================================================
# ROUTE PACKAGE
# ======================================================


auth_route = APIRouter(prefix='/auth')


# ======================================================
# CREDENTIALS DEPENDENCY
# ======================================================


bearer_object = HTTPBearer()


def session_token(credentials=Depends(bearer_object)):
    return credentials.credentials


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
def test(payload: schemas.Registration, db=Depends(get_db), token=Depends(session_token)):

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
