from fastapi import Depends
from fastapi.security import HTTPBearer


# ======================================================
# CREDENTIALS DEPENDENCY
# ======================================================


bearer_object = HTTPBearer()


def session_token(credentials=Depends(bearer_object)):
    return credentials.credentials