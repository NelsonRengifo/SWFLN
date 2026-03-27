
#                      ORM MODEL

# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from sqlalchemy import Column, TEXT, BIGINT, TIMESTAMP, ForeignKey, text, func
from sqlalchemy.dialects.postgresql import UUID


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.models.model_config import Base


class UploadedFiles(Base):

    __tablename__               = "uploaded_files"

    uploaded_file_id            = Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    uploaded_by                 = Column(UUID, ForeignKey("users.user_id"), nullable=False)
    uploaded_at                 = Column(TIMESTAMP, nullable=False, server_default=func.now())
    original_file_name          = Column(TEXT, nullable=False)
    original_file_size_in_bytes = Column(BIGINT, nullable=False)
    source                      = Column(TEXT, nullable=False)
    ingestion_status            = Column(TEXT, nullable=False, server_default=text('pending'))
    transform_status            = Column(TEXT, nullable=False, server_default=text('pending'))
    storage_path                = Column(TEXT, nullable=False, unique=True)
    checksum_sha256             = Column(TEXT, nullable=False, unique=True)
    