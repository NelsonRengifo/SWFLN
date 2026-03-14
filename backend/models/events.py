
#                            ORM MODEL


# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from sqlalchemy import Column, TEXT, INTEGER, ForeignKey, DATE, TIME, text
from sqlalchemy.dialects.postgresql import UUID


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.models.model_config import Base



class Events(Base):

    __tablename__    = "events"

    id                          = Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    event_id                    = Column(INTEGER, nullable=False)
    start_date                  = Column(DATE, nullable=False)
    end_date                    = Column(DATE, nullable=False)
    start_time                  = Column(TIME, nullable=False)
    end_time                    = Column(TIME, nullable=False)
    registrant_name             = Column(TEXT, nullable=False)
    event_title                 = Column(TEXT, nullable=False)
    total_confirmed_registrants = Column(INTEGER, nullable=False)
    total_number_registrants    = Column(INTEGER, nullable=False)
    uploaded_file_id            = Column(UUID, ForeignKey("uploaded_files.uploaded_file_id", ondelete="CASCADE"), nullable=False)