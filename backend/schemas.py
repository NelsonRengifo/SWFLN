#                                           Pydantic Models

# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from pydantic import BaseModel, Field, EmailStr, model_validator
from typing_extensions import Self
from typing import Literal
from uuid import UUID
from datetime import date

# ======================================================
# LOGIN ROUTE CONTRACT
# ======================================================


class Credentials(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=8)


# ======================================================
# REGISTER ROUTE CONTRACT
# ======================================================


class Registration(BaseModel):
    username:   str = Field(min_length=3, max_length=32)
    password:   str = Field(min_length=8, max_length=128)
    first_name: str = Field(min_length=1, max_length=64)
    last_name:  str = Field(min_length=1, max_length=64)
    user_role:  str = Field(min_length=5, max_length=11)
    email:      EmailStr


# ======================================================
# UPDATE PASSWORD ROUTE CONTRACT
# ======================================================


class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password:     str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @model_validator(mode='after')
    # self is an instance of UpdatePassword
    def check_passwords_match(self) -> Self:
        if self.new_password != self.confirm_password:
            # HTTP 422
            raise ValueError("Passwords do not match")
        return self


# ======================================================
# UPDATE USERNAME ROUTE CONTRACT
# ======================================================


class UpdateUsername(BaseModel):
    new_username:     str = Field(min_length=3, max_length=32)
    confirm_username: str = Field(min_length=3, max_length=32)

    @model_validator(mode='after')
    def check_usernames_match(self) -> Self:
        # self is an instance of UpdatePassword
        if self.new_username != self.confirm_username:
            # HTTP 422
            raise ValueError("Usernames do not match")
        return self


# ======================================================
# FORGOT-PASSWORD ROUTE CONTRACT
# ======================================================


class ForgotPassword(BaseModel):
    email: EmailStr


# ======================================================
# RESET-PASSWORD ROUTE CONTRACT
# ======================================================


class ResetPassword(BaseModel):
    reset_token:      str = Field(min_length=1)
    new_password:     str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @model_validator(mode='after')
    # self is an instance of ResetPassword
    def check_passwords_match(self) -> Self:
        if self.new_password != self.confirm_password:
            # HTTP 422
            raise ValueError("Passwords do not match")
        return self


# ======================================================
# FORGOT-USERNAME ROUTE CONTRACT
# ======================================================


class ForgotUsername(BaseModel):
    email: EmailStr


# ======================================================
# TOP TUTORIALS RESPONSE MODEL
# ======================================================


class TopTutorials(BaseModel):
    tutorial_name: str
    total_views: int


# ======================================================
# GET FILES RESPONSE MODEL
# ======================================================
    
    
class FileListResponse(BaseModel):
    data: list[dict]    
    source: Literal["libcal", "niche", "myturn"]    
    page:  int
    limit: int
    has_next: bool
    total_pages: int


# ======================================================
# TUTORIAL VIEWS RESPONSE MODEL
# ======================================================


class TutorialViews(BaseModel):
    data: list[dict]
    total: int


# ======================================================
# DELETE FILE(s) ROUTE CONTRACT
# ======================================================


class DeleteFilesRequest(BaseModel):
    files: list[UUID]

# ======================================================
# DELETE USER(S) ROUTE CONTRACT
# ======================================================

class DeleteUsersRequest(BaseModel):
    users: list[UUID]

# ======================================================
# TOTAL EVENTS BY TYPE 
# ======================================================


class TotalEvents(BaseModel):
    data: list[dict]
    total: int

# ======================================================
# TOP CHECKED OUT ITEMS
# ======================================================


class TopCheckedOutItems(BaseModel):
    data: list[dict]


# ======================================================
# TOP ORGANIZATIONS
# ======================================================


class TopOrganizations(BaseModel):
    data: list[dict]


# ======================================================
# ITEMS WHERE COST = 0
# ======================================================

class FreeItems(BaseModel):
    data: list[dict]
    total: int


# ======================================================
# INDIVIDUAL METADATA PER EVENT
# ======================================================

class EventRoster(BaseModel):
    data: list[dict]      
    page:  int
    limit: int
    has_next: bool
    total_pages: int


# ======================================================
# CONTAINS USER METADATA
# ======================================================

class Users(BaseModel):
    data: list[dict]