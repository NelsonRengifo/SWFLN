
#                            ORM MODEL


# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from sqlalchemy import Column, TEXT, ForeignKey, BOOLEAN, text
from sqlalchemy.dialects.postgresql import UUID


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.models.model_config import Base



class Users(Base):

    __tablename__    = "users"


    user_id          = Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    username         = Column(TEXT, unique=True, nullable=False)
    email            = Column(TEXT, unique=True, nullable=False)
    first_name       = Column(TEXT, nullable=False)
    last_name        = Column(TEXT, nullable=False)
    active           = Column(BOOLEAN, nullable=False, server_default=text("TRUE"))
    user_role        = Column(TEXT, nullable=False, server_default=text("admin"))
    password_hash    = Column(TEXT, nullable=False)
