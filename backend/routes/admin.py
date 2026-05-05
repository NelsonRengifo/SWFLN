# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status
from typing import Literal
from datetime import date, timedelta
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
        services.extend_session_expiration(db, session.expires_at, session.user_id, session.token_hash)
        file_id = await services.upload_file_service(db, file, source, session.user_id)
        
        if source == 'niche':
            services.run_niche_ingestion_logic(db, source)
            services.run_niche_transform_logic(db, source)

        elif source == "libcal":
            services.run_libcal_ingestion_logic(db, source)
            services.run_libcal_transform_logic(db, source)
        
        elif source == "myturn":
            services.run_myturn_ingestion_logic(db, source)
            services.run_myturn_transform_logic(db, source)

        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a recognized source")

        return {"message": "upload sucessful", "file_id": file_id}
    
    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    
    except admin.NoFileWasUploaded:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing csv file")
    
    except admin.InvalidFileFormat:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="file must be csv")
    
    except admin.DuplicateFile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="file was already uploaded")
    
    except admin.FileIsEmpty:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="file is empty")
    
    except admin.InvalidFileType:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="file is not a valid type for this source")
    
    except admin.StorageUploadFailError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to upload file to supabase")
    
    except admin.FailedToUploadMetaData:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="failed to upload file to schema")
    


# ------------------------------------------------------ DASHBOARD ENDPOINTS ------------------------------------------------------


# ======================================================
# TOP TUTORIALS
# ======================================================


@admin_route.get("/tutorials/top", status_code=200, response_model=list[schemas.TopTutorials])
def top_tutorials(limit: int = 10, start_date: date | None = None, end_date: date | None = None, db=Depends(get_db), token=Depends(session_token)):
    
    # A date must be in the format: 2026-02-15
    try:
        session = services.authenticate_token(db, token)
        services.extend_session_expiration(db, session.expires_at, session.user_id, session.token_hash)

        if start_date and end_date:
            services.is_valid_date_range(start_date, end_date)
        
        return services.top_tutorials(db, limit, start_date, end_date)
    
    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    
    except admin.InvalidDateRange:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid date range")
    

# ======================================================
# TOTAL VIEWS FOR TUTORIALS
# ======================================================


@admin_route.get("/tutorials/views", status_code=200, response_model=schemas.TutorialViews)
def tutorial_views_monthly(start_date: date, end_date: date, db=Depends(get_db), token=Depends(session_token)):

    try:
        session = services.authenticate_token(db, token)
        services.extend_session_expiration(db, session.expires_at, session.user_id, session.token_hash)
        if start_date and end_date:
            services.is_valid_date_range(start_date, end_date)

        start_date = services.normalize_day_of_date(start_date)
        end_date = services.normalize_day_of_date(end_date)
        
        return services.tutorial_views(db, start_date, end_date)
    
    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    
    except admin.InvalidDateRange:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid date range")
    

# ======================================================
# TOTAL EVENTS BY EVENT TYPE
# ======================================================


@admin_route.get("/events/total", status_code=200, response_model=schemas.TotalEvents)
def get_total_events(start_date: date | None = None, end_date: date | None = None, db=Depends(get_db), token=Depends(session_token)):

    try:
        session = services.authenticate_token(db, token)
        services.extend_session_expiration(db, session.expires_at, session.user_id, session.token_hash)
        
        if start_date and end_date:
            services.is_valid_date_range(start_date, end_date)
        
        return services.event_count(db, start_date, end_date)
    
    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    
    except admin.InvalidDateRange:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid date range")
    

# ======================================================
# MOST CHECKED OUT ITEMS
# ======================================================


@admin_route.get("/top/items", status_code=200, response_model=schemas.TopCheckedOutItems)
def get_top_items(limit: int = 10, start_date: date | None = None, end_date: date | None = None, db=Depends(get_db), token=Depends(session_token)):

    try:
        session = services.authenticate_token(db, token)
        services.extend_session_expiration(db, session.expires_at, session.user_id, session.token_hash)

        if start_date and end_date:
            services.is_valid_date_range(start_date, end_date)
            end_date = end_date + timedelta(days=1)

        return services.get_top_items(db, start_date, end_date, limit)

    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    
    except admin.InvalidDateRange:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid date range")


# ======================================================
# TOP ORGANIZATIONS BASED ON AMOUNT OF LOANS
# ======================================================


@admin_route.get("/top/organizations", status_code=200, response_model=schemas.TopOrganizations)
def top_organizations(limit: int = 5, start_date: date | None = None, end_date: date | None = None, db=Depends(get_db), token=Depends(session_token)):

    try:
        session = services.authenticate_token(db, token)
        services.extend_session_expiration(db, session.expires_at, session.user_id, session.token_hash)
        if start_date and end_date:
            services.is_valid_date_range(start_date, end_date)
            end_date = end_date + timedelta(days=1)
            
        return services.fetch_top_organizations(db, start_date, end_date, limit)

    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    
    except admin.InvalidDateRange:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid date range")



# ------------------------------------------------------ END ---------------------------------------------------------------------


# ======================================================
# GET ADMIN FILES FOR DELETION
# ======================================================

# User selects "Delete a File" -> Frontend requests file list -> Backend returns filtered files (ASC & by source) -> User selects file(s) -> Frontend sends UUID list to delete endpoint

@admin_route.get("/files", status_code=200, response_model=schemas.FileListResponse)
def delete(source: Literal["libcal", "niche", "myturn"], page: int, db=Depends(get_db), token=Depends(session_token)):

    try:
        session = services.authenticate_token(db, token)
        services.extend_session_expiration(db, session.expires_at, session.user_id, session.token_hash)
        return services.file_data_dto(db, source, page)
    
    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")


# ======================================================
# DELETE UPLOADED FILE(s)
# ======================================================

# Backend receives list of uploaded_file_id -> Backend deletes them (tables and storage)

# Content-Type: application/json

# {
#   "files": ["2e58f6c5-51d3-4d70-8c9a-5e36b3e5e01a", "f9f0f42b-3c5c-4e2c-b6ad-7f4f03c46c28"]
# }

@admin_route.delete("/delete/files", status_code=204)
def delete(payload: schemas.DeleteFilesRequest, db=Depends(get_db), token=Depends(session_token)):

    try:
        session = services.authenticate_token(db, token)
        services.extend_session_expiration(db, session.expires_at, session.user_id, session.token_hash)
        files = payload.files
        services.delete_files(db, files)

    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    
    except admin.FailedToDeleteTutorials:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete tutorial data")


# ======================================================
# FIND ALL ITEMS WHERE COST = 0
# ======================================================

@admin_route.get("/items/free", status_code=200, response_model=schemas.FreeItems)
def get_free_items(db=Depends(get_db), token=Depends(session_token)):
    
    try:
        session = services.authenticate_token(db, token)
        services.extend_session_expiration(db, session.expires_at, session.user_id, session.token_hash)
        return services.free_items(db)

    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    

# ======================================================
# RETURNS METADA OF INDIVIDUALS PER EVENT (LIBCAL)
# ======================================================

@admin_route.get("/event/roster", status_code=200, response_model=schemas.EventRoster)
def get_events_roster(page: int, start_date: date | None = None, end_date: date | None = None, attended: bool | None = None, db=Depends(get_db), token=Depends(session_token)):
    
    try:
        session = services.authenticate_token(db, token)
        services.extend_session_expiration(db, session.expires_at, session.user_id, session.token_hash)
        
        if start_date and end_date:
            services.is_valid_date_range(start_date, end_date)
        return services.roster(db, page, start_date, end_date, attended)

    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    
    except admin.InvalidDateRange:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid date range")

# ======================================================
# SHOWS ALL USERS
# ======================================================


@admin_route.get("/get/users", status_code=200, response_model=schemas.Users)
def get_events_roster(db=Depends(get_db), token=Depends(session_token)):
    
    try:
        session = services.authenticate_token(db, token)
        services.extend_session_expiration(db, session.expires_at, session.user_id, session.token_hash)
        return services.users(db)

    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    

# ======================================================
# DELETES USERS
# ======================================================

@admin_route.delete("/delete/users", status_code=204)
def delete(payload: schemas.DeleteUsersRequest, db=Depends(get_db), token=Depends(session_token)):

    try:
        session = services.authenticate_token(db, token)
        services.extend_session_expiration(db, session.expires_at, session.user_id, session.token_hash)
        users = payload.users
        services.delete_users(db, users)

    except auth.InvalidToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token")
    
    except admin.FailedToDeleteTutorials:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete tutorial data")