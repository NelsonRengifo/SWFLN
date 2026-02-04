# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from pydantic import BaseModel, Field, EmailStr


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
