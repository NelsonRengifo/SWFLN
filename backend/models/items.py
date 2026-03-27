
#                            ORM MODEL


# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from sqlalchemy import Column, BIGINT, NUMERIC, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.models.model_config import Base



class Items(Base):

    __tablename__    = "items"

    id               = Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    uploaded_file_id = Column(UUID, ForeignKey("uploaded_files.uploaded_file_id", ondelete="CASCADE"))
    item_id          = Column(BIGINT, nullable=False)
    cost             = Column(NUMERIC(10, 2), nullable=False)