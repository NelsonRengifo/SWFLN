
#                      ORM MODEL

# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from sqlalchemy import Column, TEXT, text
from sqlalchemy.dialects.postgresql import UUID


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.models.model_config import Base


class UploadedFiles(Base):

    __tablename__    = "uploaded_files"

    uploaded_file_id = Column(UUID, primary_key=True, server_default=text("gen_random_uuid()"))
    storage_path     = Column(TEXT, nullable=False, unique=True)
    