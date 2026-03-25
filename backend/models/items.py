
#                            ORM MODEL


# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from sqlalchemy import Column, BIGINT, NUMERIC, text
from sqlalchemy.dialects.postgresql import UUID


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.models.model_config import Base



class Items(Base):

    __tablename__    = "items"

    id               = Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    item_id          = Column(BIGINT, nullable=False)
    cost             = Column(NUMERIC(10, 2), nullable=False)