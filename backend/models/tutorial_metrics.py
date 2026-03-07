
#                            ORM MODEL


# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from sqlalchemy import Column, INTEGER, ForeignKey, TIMESTAMP, DATE
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.models.model_config import Base



class TutorialMetrics(Base):

    __tablename__    = "tutorial_metrics"

    tutorial_id      = Column(UUID, ForeignKey("tutorials.tutorial_id", ondelete="CASCADE") ,nullable=False, primary_key=True)
    metric_date      = Column(DATE, nullable=False, primary_key=True)
    total_views      = Column(INTEGER, nullable=False)
    uploaded_file_id = Column(UUID, ForeignKey("uploaded_files.uploaded_file_id", ondelete="CASCADE"), nullable=False)
    created_at       = Column(TIMESTAMP, nullable=False, server_default=func.now())