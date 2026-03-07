
#                            ORM MODEL


# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from sqlalchemy import Column, INTEGER, ForeignKey, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import func


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.models.model_config import Base



class RawRows(Base):

    __tablename__    = "raw_rows"

    id               = Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    uploaded_file_id = Column(UUID, ForeignKey("uploaded_files.uploaded_file_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at       = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    raw_data         = Column(JSONB, nullable=False)
    row_number       = Column(INTEGER, nullable=False)