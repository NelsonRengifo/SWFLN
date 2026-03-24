
#                            ORM MODEL


# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from sqlalchemy import Column, ForeignKey, TIMESTAMP, BIGINT, TEXT, BOOLEAN, text
from sqlalchemy.dialects.postgresql import UUID, INTERVAL


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.models.model_config import Base



class Loans(Base):

    __tablename__    = "loans"

    uploaded_file_id = Column(UUID, ForeignKey("uploaded_files.uploaded_file_id", ondelete="CASCADE"), nullable=False)
    loan_id          = Column(BIGINT, primary_key=True)
    client_name      = Column(TEXT, nullable=False)
    organization     = Column(TEXT, nullable=False)
    item_name        = Column(TEXT, nullable=False)
    item_id          = Column(BIGINT, nullable=False)
    checkout_at      = Column(TIMESTAMP(timezone=True), nullable=False)
    returned_at      = Column(TIMESTAMP(timezone=True), nullable=False)
    duration         = Column(INTERVAL, nullable=False)
    renewal          = Column(BOOLEAN, nullable=False, server_default=text("False"))