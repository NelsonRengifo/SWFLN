
#                      ORM MODEL

# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from sqlalchemy import Column, TEXT, TIMESTAMP,  text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.models.model_config import Base


class Tutorials(Base):

    __tablename__   = "tutorials"

    tutorial_id     = Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    tutorial_name   = Column(TEXT, unique=True, nullable=False)
    created_at      = Column(TIMESTAMP, nullable=False, server_default=func.now())