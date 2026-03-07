# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status
from typing import Literal
from datetime import date
import logging

logger = logging.getLogger(__name__)


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.routes.dependencies.auth_dependencies import session_token
from backend.core.database_config import get_db
from backend import services
from backend.exceptions import auth
from backend.exceptions import admin
from backend import schemas

# ======================================================
# ROUTE PACKAGE
# ======================================================


admin_route = APIRouter(prefix='/admin')


# ======================================================
# FILE UPLOAD ROUTE
# ======================================================


@admin_route.post("/upload", status_code=200)
async def upload_file(file: UploadFile = File(...), source: Literal["libcal", "niche", "myturn"] = Form(...), db=Depends(get_db), token=Depends(session_token)):

    try:
        session = services.authenticate_token(db, token)
        file_id = await services.upload_file_service(db, file, source, session.user_id)
        services.run_ingestion_logic(db)
        services.run_transform_logic(db)
        return {"message": "upload sucessful", "file_id": file_id}
    
    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    
    except admin.NoFileWasUploaded:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing csv file")
    
    except admin.InvalidFileFormat:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="file must be csv")
    
    except admin.DuplicateFile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="file was already uploaded")
    
    except admin.StorageUploadFailError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to upload file to supabase")
    
    except admin.FailedToUploadMetaData:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to upload file to schema")


# ======================================================
# TOP TUTORIALS
# ======================================================


@admin_route.get("/tutorials/top", status_code=200, response_model=list[schemas.TopTutorials])
def top_tutorials(limit: int = 10, start_date: date | None = None, end_date: date | None = None, db=Depends(get_db), token=Depends(session_token)):
    
    # date must be -> ISO 8601
    try:
        services.authenticate_token(db, token)
        return services.top_tutorials(db, limit, start_date, end_date)
    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    