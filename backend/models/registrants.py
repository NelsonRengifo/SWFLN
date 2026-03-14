
#                            ORM MODEL


# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from sqlalchemy import Column, TEXT, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.models.model_config import Base



class Registrants(Base):

    __tablename__    = "registrants"

    registrant_id    = Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    id               = Column(UUID, ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False)
    registrant_name  = Column(TEXT, ForeignKey("events.registrant_name", ondelete="CASCADE"), nullable=False)
    