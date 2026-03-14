# ======================================================
# EXTERNAL IMPORTS
# ======================================================


import secrets
import hashlib
import logging
import io
import csv
from datetime import time
from typing import Literal
from argon2 import exceptions, PasswordHasher
from uuid import UUID
from sqlalchemy.engine import Row
from fastapi import UploadFile
from uuid import uuid4
from dateutil import parser


# ======================================================
# INTERNAL IMPORTS
# ======================================================

from backend.clients.supabase import supabase
from backend import queries, validators
from backend.schemas import Credentials, Registration
from backend.exceptions import auth
from backend.exceptions import admin
from backend.clients.supabase import supabase
from backend.dto.upload_dto import FilePathResult
from backend.schemas import TopTutorials
from backend.schemas import FileListResponse
import backend.models


logger = logging.getLogger(__name__)
hasher = PasswordHasher()


#-------------------------------------------------------
#               AUTH ROUTE LOGIC
#-------------------------------------------------------


# ======================================================
# VALIDATES LOGIN CREDENTIALS
# ======================================================


def verify_credentials(db, payload: Credentials) -> UUID:

    if not validators.validate_username(payload.username):
        raise auth.InvalidCredentials
    norm_username = validators.normalize_username(payload.username)
    row = queries.get_user_for_auth_by_username(db, norm_username)
    if not row:
        raise auth.InvalidCredentials
    try:
        validators.verify_password(payload.password, row.password_hash)
        return row.user_id
    except (exceptions.VerifyMismatchError, exceptions.VerificationError, exceptions.InvalidHashError) as e:
        logger.exception(f"Failed password attempt for username: {norm_username} | error: {e}")
        raise auth.InvalidCredentials


# ======================================================
# CREATES SESSION TOKEN
# ======================================================


def create_token(db, user_id) -> str:

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    queries.create_session_token(db, user_id, token_hash)
    return token


# ======================================================
# CREATES PASSWORD RESET TOKEN
# ======================================================


def generate_password_reset_token(db, user_id) -> str:

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    queries.create_password_reset_token(db, user_id, token_hash)
    return token


# ======================================================
# AUTHENTICATES SESSION TOKEN
# ======================================================


def authenticate_token(db, token) -> Row | None:

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    session = queries.get_session_info_by_token_hash(db, token_hash)
    if not session:
        raise auth.InvalidToken
    return session


# ======================================================
# AUTHENTICATES RESET PASSWORD TOKEN
# ======================================================


def authenticate_reset_token(db, token) -> Row | None:

    token_hash = hashlib.sha256(token.encode()).hexdigest()
    session = queries.get_reset_session_info_by_token_hash(db, token_hash)
    if not session:
        raise auth.InvalidToken
    return session


# ======================================================
# EXTENDS SESSION TOKEN
# ======================================================


def extend_session_expiration(db, token_hash) -> None:

    queries.extend_session_expiry(db, token_hash)


# ======================================================
# DELETES SESSION TOKEN
# ======================================================


def delete_token(db, token_hash) -> str:

    row = queries.delete_session_token_by_token_hash(db, token_hash)
    if not row:
        raise auth.InvalidToken

    return row.id


# ======================================================
# REGISTERS A NEW USER
# ======================================================


def register_user(db, payload: Registration) -> UUID:

    # Username
    if not validators.validate_username(payload.username):
        raise auth.InvalidUsername
    norm_username = validators.normalize_username(payload.username)
    if queries.exists_username(db, norm_username):
        raise auth.UsernameTaken

    # Password
    if not validators.validate_password(payload.password):
        raise auth.InvalidPassword
    password_hash = ""
    try:
        password_hash = hasher.hash(payload.password)
    except exceptions.HashingError as e:
        logger.exception(f"Failed hashing for username: {payload.username} | error: {e}")
        raise auth.FailedToHash

    # Email
    norm_email = validators.normalize_email(payload.email)
    if queries.exists_email(db, norm_email):
        raise auth.EmailTaken

    # First name
    norm_first_name = validators.normalize_first_name(payload.first_name)

    # Last name
    norm_last_name = validators.normalize_last_name(payload.last_name)

    # Role
    if payload.user_role not in ["admin", "super admin"]:
        raise auth.InvalidUserRole
    user_role = payload.user_role

    # Insert user profile
    user_id = queries.create_user(db, norm_username, password_hash, norm_email, norm_first_name, norm_last_name, user_role)

    return user_id


# ======================================================
# CHECKS USER ROLE VALID FOR THE ROUTE
# ======================================================


def has_valid_role(db, token_hash, role) -> None:

    if not queries.exists_user_role(db, token_hash, role):
        raise auth.InvalidRole


# ======================================================
# VERIFY USER PASSWORD
# ======================================================


def confirm_password(db, plain_password, user_id) -> None:

    password_hash = queries.get_user_password_by_user_id(db, user_id)
    try:
        validators.verify_password(plain_password, password_hash)
    except (exceptions.VerifyMismatchError, exceptions.VerificationError, exceptions.InvalidHashError) as e:
        logger.exception(f"Failed password hash verification attempt for user: {user_id} | error: {e}")
        raise auth.InvalidCredentials


# ======================================================
# VALIDATE USER PASSWORD
# ======================================================


def enforce_password_policy(db, new_password, user_id) -> None:
    # checks that the new password passes policy checks
    if not validators.validate_password(new_password):
        raise auth.InvalidPassword
    # check new password != old password
    old_password = queries.get_user_password_by_user_id(db, user_id)
    try:
        validators.verify_password(new_password, old_password)
        raise auth.PasswordsMatch
    except exceptions.VerifyMismatchError:
        pass
    except (exceptions.VerificationError, exceptions.InvalidHashError) as e:
        logger.exception(f"Failed password hash verification attempt for user: {user_id} | error: {e}")
        raise auth.FailedToHash


# ======================================================
# UPDATE USER PASSWORD
# ======================================================


def change_user_password(db, new_password, user_id) -> None:

    try:
        password_hash = hasher.hash(new_password)
        queries.update_user_password_by_user_id(db, password_hash, user_id)
        queries.delete_sessions_by_user_id(db, user_id)
    except exceptions.HashingError as e:
        logger.exception(f"Failed hashing password for user: {user_id} | error: {e}")
        raise auth.FailedToHash


# ======================================================
# UPDATE USER USERNAME
# ======================================================


def change_user_username(db, new_username, user_id) -> None:

    if not validators.validate_username(new_username):
        raise auth.InvalidUsername
    norm_username = validators.normalize_username(new_username)
    if queries.exists_username(db, norm_username):
        raise auth.UsernameTaken
    queries.update_user_username_by_user_id(db, norm_username, user_id)


# ======================================================
# CREATE PASSWORD RESET TOKEN & CONFIRM EMAIL EXISTS
# ======================================================


def get_password_reset_token(db, email) -> str:

    norm_email = validators.normalize_email(email)
    user_id = queries.get_user_id_for_transaction_by_email(db, norm_email)
    if not user_id:
        raise auth.EmailNotFound
    return generate_password_reset_token(db, user_id)


# ======================================================
# RESET PASSWORD
# ======================================================


def reset_password(db, new_password, user_id) -> None:

    enforce_password_policy(db, new_password, user_id)

    try:
        password_hash = hasher.hash(new_password)
        queries.update_user_password_by_user_id(db, password_hash, user_id)
    except exceptions.HashingError as e:
        logger.exception(f"Failed hashing password for user: {user_id} | error: {e}")
        raise auth.FailedToHash


# ======================================================
# GET USERNAME VIA EMAIL
# ======================================================


def get_username(db, email) -> str:

    norm_email = validators.normalize_email(email)
    username = queries.get_user_username_by_email(db, norm_email)
    if not username:
        raise auth.EmailNotFound
    return username



#-------------------------------------------------------
#               ADMIN ROUTE LOGIC
#-------------------------------------------------------


# ======================================================
# UPLOAD FILE LOGIC: STORAGE AND SCHEMA
# ======================================================


async def upload_file_service(db, file: UploadFile, source: str, user_id: UUID) -> UUID:
    
    if not file.filename:
        raise admin.NoFileWasUploaded
    
    if not file.filename.lower().endswith(".csv"):
        raise admin.InvalidFileFormat
    
    file_bytes = await _get_file_bytes(file)
    if not file_bytes:
        raise admin.FileIsEmpty

    checksum = _checksum(file_bytes)

    if  _ensure_not_duplicate(db, checksum):
        raise admin.DuplicateFile
    
    result = _build_file_path(source)
    file_path = result.file_path
    file_id = result.file_id

    try:
        _upload_file_to_storage(file_bytes, file_path) # saves raw file in supabase storage
    
    except Exception as e:
        logger.warning(f"Failed to upload file {file_path} | ERROR: {e}")
        raise admin.StorageUploadFailError
    
    data = {
        "uploaded_file_id": file_id,
        "uploaded_by": user_id,
        "original_file_name": file.filename,
        "original_file_size_in_bytes": file.size,
        "source": source,
        "storage_path": file_path,
        "checksum_sha256": checksum
    }

    # saves file metadata in schema
    try:
        file_id = queries.create_new_file(db, data)
    
    except Exception as e:
        logger.exception(f"Failed to save file to schema | ERROR: {e}")
        _delete_file_from_storage(file_path)
        raise admin.FailedToUploadMetaData

    return file_id 


# ======================================================
# DELETE FILE LOGIC: STORAGE AND SHEMA
# ======================================================


def delete_files(db, files: list[UUID]) -> None:

    storage_paths = queries.delete_uploaded_files(db, files)
    _delete_tutorials(db)
    for file_path in storage_paths:
        _delete_file_from_storage(file_path)


# ======================================================
# DELETE ORPHAN TUTORIALS
# ======================================================


def _delete_tutorials(db) -> None:

    try:
        queries.delete_orphan_tutorials(db)
        
    except Exception as e:
        logger.exception(f"Failed to delete tutorials | ERROR: {e}")
        raise admin.FailedToDeleteTutorials
    
# ======================================================
# READ FILE BYTES
# ======================================================


async def _get_file_bytes(file: UploadFile) -> bytes:

    return await file.read()


# ======================================================
# COMPUTES CHECKSUM
# ======================================================


def _checksum(file_bytes: bytes) -> str:

    return hashlib.sha256(file_bytes).hexdigest()


# ======================================================
# CHECK FOR DUPLICATE FILE
# ======================================================


def _ensure_not_duplicate(db, checksum: str) -> bool:

    return queries.exists_file(db, checksum)


# ======================================================
# BUILD FILE PATH FOR SUPABASE
# ======================================================


def _build_file_path(source: str) -> FilePathResult:

    file_id = uuid4()
    file_path = f"{source}/{file_id}.csv"
    return FilePathResult(file_id=file_id, file_path=file_path)


# ======================================================
# UPLOAD FILE TO SUPABASE
# ======================================================


def _upload_file_to_storage(file_bytes, file_path) -> None:

    supabase.storage.from_("raw_uploads").upload(file=file_bytes, path=file_path, file_options={"content-type": "text/csv"})
    

# ======================================================
# DELETE FILE FROM SUPABASE
# ======================================================


def _delete_file_from_storage(file_path) -> None:
    
    supabase.storage.from_("raw_uploads").remove([f"{file_path}"])


# ======================================================
# NICHE PENDING FILES
# ======================================================


def run_niche_ingestion_logic(db, source) -> None:
        
    while True:

        try:
            payload  = queries.claim_ingestion_file(db, source)
            if payload is None:
                break # There are no files waiting to be processed

            storage_path = payload.storage_path
            file_id = payload.uploaded_file_id

            file_bytes = supabase.storage.from_("raw_uploads").download(storage_path)

            file_reader = _load_csv_reader(file_bytes)
            if not file_reader.fieldnames:
                logger.warning(f"Missing CSV headers {storage_path}")
                _set_ingestion_status(db, "failed", file_id, "missing csv headers")
                continue

            _insert_raw_rows_batch(db, file_reader, file_id)
            _set_ingestion_status(db, "completed", file_id)

        # Special handling here to not trigger the get_db() logic in order to save file status.
        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to process niche uploaded files. ERROR: {e}")
            _set_ingestion_status(db, "failed", file_id, str(e))
            db.commit()


# ======================================================
# LIBCAL PENDING FILES
# ======================================================


def run_libcal_ingestion_logic(db, source) -> None:

    while True:

        try:
            payload  = queries.claim_ingestion_file(db, source)
            if payload is None:
                break # There are no files waiting to be processed

            storage_path = payload.storage_path
            file_id = payload.uploaded_file_id
            file_bytes = supabase.storage.from_("raw_uploads").download(storage_path)

            file_reader = _load_csv_reader(file_bytes)
            if not file_reader.fieldnames:
                logger.warning(f"Missing CSV headers {storage_path}")
                _set_ingestion_status(db, "failed", file_id, "missing csv headers")
                continue
            
            _insert_raw_rows_batch(db, file_reader, file_id)
            _set_ingestion_status(db, "completed", file_id)
            db.commit()

        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to process libcal uploaded file. ERROR: {e}")
            _set_ingestion_status(db, "failed", file_id, str(e))
            db.commit()


# ======================================================
# NICHE TRANSFORMATION LOGIC
# ======================================================


def run_niche_transform_logic(db, source) -> None:
    
    while True:

        try:
            file_id = queries.claim_transform_file(db, source)
            if file_id is None:
                break # There are no files waiting to be transformed
            
            # RAW rows
            rows = _get_rows(db, file_id)

            # collect tutorial names
            tutorial_names = list({"tutorial_name": row.get("Tutorial")} for row in rows[:-1])
            if None in tutorial_names:
                raise ValueError("Missing tutorial name")
            
            # batch insert tutorials
            if tutorial_names:
                _insert_tutorials(db, tutorial_names)

            # tutorial_name -> tutorial_id mapping
            result = _get_tutorial_mapping(db)
            tutorial_mapping = {row["tutorial_name"]: row["tutorial_id"] for row in result}
                
            # build batch insert for metrics
            seen = set()
            tutorial_metrics = []
            for row in rows[:-1]:
                tutorial_id = tutorial_mapping[row["Tutorial"]]
                for key, value in row.items():
                    if key not in ["Tutorial", "Total"]:
                        metric_date = parser.parse(key).replace(day=1).date()
                        if (tutorial_id, metric_date) in seen:
                            continue
                        seen.add((tutorial_id, metric_date))
                        total_views = int(value)
                        tutorial_metrics.append({
                            "tutorial_id": tutorial_id,
                            "metric_date": metric_date,
                            "total_views": total_views,
                            "uploaded_file_id": file_id
                        })

            # batch insert tutorial_metric
            if tutorial_metrics:
                _insert_tutorial_metrics(db, tutorial_metrics)
               
            _set_transform_status(db, "completed", file_id)
                
        # Special handling here to not trigger the get_db() logic in order to save file status.
        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to transform niche row. ERROR: {e}")
            _set_transform_status(db, "failed", file_id, str(e))
            db.commit()


# ======================================================
# LIBCAL TRANSFORMATION LOGIC
# ======================================================


def run_libcal_transform_logic(db, source):
    
    while True:

        try:
            file_id = queries.claim_transform_file(db, source)
            if file_id is None:
                break # There are no files waiting to be transformed
            
            # RAW rows
            rows = _get_rows(db, file_id)

            seen = set()
            events_batch = []
            registrants_batch = []

            for row in rows:
                first_name = row.get("First Name")
                last_name = row.get("Last Name")
                if not first_name or not last_name:
                    continue
                
                attended = row.get("Attended")

                # attended field was left empty
                if not attended:
                    continue

                full_name = ""
                if attended.lower() == 'yes':
                        full_name += first_name.lower().strip() + " " + last_name.lower().strip()
                else:
                    # attended field == no
                    continue

                event_id = row.get("Event ID")
                event_title = row.get("Title")
                start_time = row.get("Start Time")
                end_time = row.get("End Time")
                start_date = row.get("Start Date")
                end_date = row.get("End Date")

                # Determines if duplicate row
                
                key = (event_id, first_name, last_name, event_title, start_time, end_time)

                if key in seen:
                    continue
                
                seen.add(key)

                # normalize data
                start_date = parser.parse(start_date).date()
                end_date = parser.parse(end_date).date()
                title = event_title.strip()
                start_time = time.fromisoformat(start_time)
                end_time = time.fromisoformat(end_time)
                # total people who registered for the event
                total_number_registrants = int(row.get("Confirmed Registrations"))
                # total people who actually showed up
                total_confirmed_registrants = int(row.get("Confirmed Attendance"))
                
                events_batch.append({
                    "start_date": start_date,
                    "end_date": end_date,
                    "registrant_name": full_name,
                    "event_title": title,
                    "total_confirmed_registrants": total_confirmed_registrants,
                    "total_number_registrants": total_number_registrants,
                    "uploaded_file_id": file_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "event_id": event_id
                })
               
            if events_batch:
                _insert_events_data(db, events_batch)
            
            # result = _get_event_mapping(db)
            # event_mapping = {row["registrant_name"]: row["id"] for row in result}

            # for row in events_batch:

            #     registrants_batch.append({
            #         "id": event_mapping[row["registrant_name"]],
            #         "registrant_name": row["registrant_name"]
            #     })
            
            # if registrants_batch:
            #     _insert_registrant_data(db, registrants_batch)

            _set_transform_status(db, "completed", file_id)

        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to transform libcal row. ERROR: {e}")
            _set_transform_status(db, "failed", file_id, str(e))
            db.commit()


# ======================================================
# SET FILE STATUS
# ======================================================


def _set_ingestion_status(db, status: Literal["pending", "processing", "completed", "failed"], file_id: UUID, error_message=None):
    
    queries.update_ingestion_status(db, status, file_id, error_message)


def _set_transform_status(db, status: Literal["pending", "processing", "completed", "failed"], file_id: UUID, error_message=None):
    
    queries.update_transform_status(db, status, file_id, error_message)


# ======================================================
# INSERT THE JSONB
# ======================================================


def _insert_raw_row(db, data: list[dict]) -> int:
    
    return queries.insert_raw_row_data(db, data)



# ======================================================
# GET JSONB ROW
# ======================================================


def _get_rows(db, file_id) -> list[dict]:
    
    return queries.fetch_raw_rows(db, file_id)


# ======================================================
# NICHE HELPER FUNCTIONS
# ======================================================


def _insert_tutorials(db, tutorial_names) -> None:

    return queries.insert_tutorial_names(db, tutorial_names)


def _insert_tutorial_metrics(db, tutorial_metrics) -> None:

    queries.insert_tutorial_data(db, tutorial_metrics)


def _get_tutorial_mapping(db) -> dict:

    return queries.tutorial_mapping(db)


def _build_top_tutorials_dto(rows: list[Row]) -> list[TopTutorials]:

    return list({"tutorial_name": row.tutorial_name, "total_views": row.total_views} for row in rows)


# ======================================================
# LIBCAL HELPER FUNCTIONS
# ======================================================


def _insert_events_data(db, batch) -> None:

    queries.insert_event_metadata(db, batch)

def _get_event_mapping(db) -> dict:

    return queries.event_mapping(db)

def _insert_registrant_data(db, batch) -> None:
    
    queries.insert_registrant_metadata(db, batch)



# ======================================================
# FETCHES TOP TUTORIALS
# ======================================================


def top_tutorials(db, limit, start_date, end_date) -> list[TopTutorials]:

    rows = queries.get_top_tutorials(db, limit, start_date, end_date)
    return _build_top_tutorials_dto(rows)
    


# ======================================================
# PERFORMS BATCH INSERTION INTO RAW ROWS FOR NICHE
# ======================================================


def _insert_raw_rows_batch(db, file_reader: bytes, file_id: UUID) -> None:

    # Multi-value insert method
    batch = []
    BATCH_LIMIT = 5000
    for row_number, row in enumerate(file_reader, start=1):
        batch.append({
            "uploaded_file_id": file_id,
            "raw_data": row,
            "row_number": row_number
        })
        # 5000 rows of data
        if len(batch) >= BATCH_LIMIT:
            inserted_ids = _insert_raw_row(db, batch)
            # check we actually inserted 5000 rows of data
            assert inserted_ids == len(batch)
            batch.clear()

    if batch:
        inserted_ids = _insert_raw_row(db, batch)
        assert inserted_ids == len(batch)


# ======================================================
# PARSES AND PREPARES THE CSV FILE
# ======================================================


def _load_csv_reader(file_bytes: bytes) -> csv.DictReader:
    # removes the BOM by using utf-8-sig
    file_text = file_bytes.decode(encoding='utf-8-sig')
    # creates an in-memory file-like object for strings so it can be used by DictReader
    file_stream = io.StringIO(file_text)
    # reads a CSV file and returns each row as a dictionary instead of a list so we can access by name
    file_reader = csv.DictReader(file_stream)

    return file_reader


# ======================================================
# GETS FILES TO DISPLAY FOR FRONTEND
# ======================================================


def file_data_dto(db, source, page) -> FileListResponse:

    ROW_LIMIT = 25
    offset_value = (page - 1) * ROW_LIMIT
    rows = queries.get_file_data(db, offset_value, source)
    has_next = False

    data = []
    counter = 0
    for row in rows:
        if counter > 25:
            has_next = True
            break
        first_name = row.first_name.title()
        last_name = row.last_name.title()
        full_name = first_name + " " + last_name

        row_dict = {
            "uploaded_file_id": row.uploaded_file_id,
            "uploaded_by": full_name,
            "uploaded_at": row.uploaded_at.date(),
            "original_file_name": row.original_file_name,
            "ingestion_status": row.ingestion_status,
            "transform_status": row.transform_status
        }

        data.append(row_dict)
    
    return FileListResponse(data=data, source=source ,page=page, limit=ROW_LIMIT, has_next=has_next)
        
