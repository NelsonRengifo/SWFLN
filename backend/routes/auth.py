"""
Authentication & Authorization Routes

Handles user authentication and session management, including:

- User login and logout
- Token-based session authorization
- User registration
- Password updates and credential management (forgot username or password)
"""

from fastapi import APIRouter, HTTPException, Depends

auth_route = APIRouter(prefix='/auth')


@auth_route.get("/health")
def test():
    return {"status": "ok"}
