# ======================================================
# EXTERNAL IMPORTS
# ======================================================


import secrets
import hashlib
import logging
import io
import csv
from datetime import time, date
from datetime import datetime, timezone, timedelta
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
from backend.dto.upload_dto import FilePathResult
from backend.schemas import TopTutorials
from backend.schemas import FileListResponse
from backend.schemas import TutorialViews
from backend.schemas import TotalEvents
from backend.schemas import TopCheckedOutItems
from backend.schemas import TopOrganizations
from backend.schemas import FreeItems
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


def extend_session_expiration(db, expires_at ,user_id, token_hash) -> None:

    LIMIT = timedelta(hours=2) # 2 hours or less till session expires

    if expires_at - datetime.now(timezone.utc) <= LIMIT:
        logger.debug("---EXTENDING SESSION---")
        queries.extend_session_expiry(db, user_id, token_hash)
    logger.debug("--NOTHING TO EXTEND---")


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
        user_id = queries.update_user_password_by_user_id(db, password_hash, user_id)
        logger.debug(user_id)
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



def normalize_day_of_date(raw_date: date) -> date:

    return raw_date.replace(day=1)



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
# CHECKS FILE HAS HEADERS
# ======================================================


def _is_valid_file(file_reader) -> bool:

    return False if not file_reader.fieldnames else True


# ======================================================
# CLASSIFY FILE TYPE
# ======================================================


def _classify_file(file_reader) -> Literal["niche", "libcal", "loans", "items"] | None:

    # loans and items are both myturn files with different data.
    NICHE = ["tutorial"]
    LIBCAL = ["event id", "attended", "start time", "end time", "start date", "end date"]
    LOANS = ["loan id", "checked out", "checked in", "renewal"]
    ITEMS = ["historical cost", "item cost"]

    headers = file_reader.fieldnames

    for h in headers:

        h = h.lower().strip()
        
        if h in NICHE:
            return "niche"
        
        elif h in LIBCAL:
            return "libcal"
        
        elif h in LOANS:
            return "loans"
        
        elif h in ITEMS:
            return "items"
    
    return None


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

            if not _is_valid_file(file_reader):
                logger.warning(f"Missing CSV headers {storage_path}")
                # _set_ingestion_status(db, "failed", file_id, "missing csv headers")
                continue

            file_type = _classify_file(file_reader)

            if file_type not in ["niche"]:
                raise admin.InvalidFileType("file is not a valid niche file")
            
            _insert_raw_rows_batch(db, file_reader, file_id)
            _set_ingestion_status(db, "completed", file_id)
            
        except Exception as e:
            logger.exception(f"Failed to process niche uploaded files. ERROR: {e}")
            # _set_ingestion_status(db, "failed", file_id, str(e))
            _delete_file_from_storage(storage_path)
            raise


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

            if not _is_valid_file(file_reader):
                logger.warning(f"Missing CSV headers {storage_path}")
                # _set_ingestion_status(db, "failed", file_id, "missing csv headers")
                continue

            file_type = _classify_file(file_reader)

            if file_type not in ["libcal"]:
                raise admin.InvalidFileType("file is not a valid libcal file")
            
            _insert_raw_rows_batch(db, file_reader, file_id)
            _set_ingestion_status(db, "completed", file_id)

        except Exception as e:
            logger.exception(f"Failed to process libcal uploaded file. ERROR: {e}")
            # _set_ingestion_status(db, "failed", file_id, str(e))
            _delete_file_from_storage(storage_path)
            raise


# ======================================================
# MYTURN PENDING FILES
# ======================================================

def run_myturn_ingestion_logic(db, source) -> None:

    while True:

        try:
            payload  = queries.claim_ingestion_file(db, source)
            if payload is None:
                break # There are no files waiting to be processed

            storage_path = payload.storage_path
            file_id = payload.uploaded_file_id

            file_bytes = supabase.storage.from_("raw_uploads").download(storage_path)

            file_reader = _load_csv_reader(file_bytes)

            if not _is_valid_file(file_reader):
                logger.warning(f"Missing CSV headers {storage_path}")
                # _set_ingestion_status(db, "failed", file_id, "missing csv headers")
                continue

            file_type = _classify_file(file_reader)

            logger.debug(file_type)

            if file_type not in ["loans", "items"]:
                raise admin.InvalidFileType("file is not a valid myturn file")
            
            _insert_raw_rows_batch(db, file_reader, file_id)
            _set_ingestion_status(db, "completed", file_id)

        except Exception as e:
            logger.exception(f"Failed to process myturn uploaded files. ERROR: {e}")
            # _set_ingestion_status(db, "failed", file_id, str(e))
            _delete_file_from_storage(storage_path)
            raise


# ======================================================
# NICHE TRANSFORMATION LOGIC
# ======================================================


def run_niche_transform_logic(db, source) -> None:

    while True:

        try:
            payload = queries.claim_transform_file(db, source)

            if payload is None:
                break # There are no files waiting to be transformed

            storage_path = payload.storage_path
            file_id = payload.uploaded_file_id
            
            file_bytes = supabase.storage.from_("raw_uploads").download(storage_path)

            file_reader = _load_csv_reader(file_bytes)

            file_type = _classify_file(file_reader)

            if file_type not in ["niche"]:
                raise admin.InvalidFileType("file is not a valid niche file")
            
            normalized_year = None

            for h in file_reader.fieldnames:

                keyword = _classify_niche(h)

                if keyword == 'date':
                    month, two_digit_year = h.split()
                    two_digit_year = int(two_digit_year)
                    normalized_year = _normalize_year(two_digit_year) 

            # RAW rows
            rows = _get_rows(db, file_id)

            filtered_rows = [] # store the valid rows

            for row in rows:
            
                name = None
                has_valid_value = False

                for header, value in row.items():    
                    keyword = _classify_niche(header)

                    if keyword == "tutorial":

                        if value: # we have a tutorial name

                            if value.lower().strip() == "total": # invalid tutorial name
                                break
                            
                            name = value # found a valid tutorial name

                        else: # tutorial has no name
                            break
                    
                    elif keyword == "total": # dont care about this header
                        continue
                        
                    else: # must be the date column
                        try:
                            val = int(value)
                            if val > 0: # we only care if tutorial has at least 1 view
                                has_valid_value = True
                                continue
                        except:
                            break
                
                if not name:
                    continue

                if not has_valid_value:
                    continue
                
                filtered_rows.append(row)

            # collect tutorial names
            tutorial_names = []

            for row in filtered_rows:
                
                for header, value in row.items():    
                    keyword = _classify_niche(header)

                    if keyword == "tutorial":
                        tutorial_names.append({"tutorial_name": value})
            
            # batch insert tutorials
            if tutorial_names:
                _insert_tutorials(db, tutorial_names)

            # tutorial_name -> tutorial_id mapping
            result = _get_tutorial_mapping(db)
            tutorial_mapping = {row["tutorial_name"]: row["tutorial_id"] for row in result}
                
            # build batch insert for metrics
            seen = set()
            tutorial_metrics = []

            for row in filtered_rows:
                
                tutorial_id = None
                metric_date = None
                total_views = None

                for header, value in row.items():
                    keyword = _classify_niche(header)

                    if keyword == "tutorial":
                        tutorial_id = tutorial_mapping[value]

                    elif keyword == "total":
                        continue

                    else:
                        metric_date = parser.parse(header).replace(day=1, year=normalized_year).date()
                        total_views = value

                if (tutorial_id, metric_date) in seen:
                    continue
                    
                seen.add((tutorial_id, metric_date))
                
                tutorial_metrics.append({
                    "tutorial_id": tutorial_id,
                    "metric_date": metric_date,
                    "total_views": total_views,
                    "uploaded_file_id": file_id
                })

                logger.debug(tutorial_metrics)

            # batch insert tutorial_metric
            if tutorial_metrics:
                _insert_tutorial_metrics(db, tutorial_metrics)
               
            _set_transform_status(db, "completed", file_id)
                
        except Exception as e:
            logger.exception(f"Failed to transform niche row. ERROR: {e}")
            # _set_transform_status(db, "failed", file_id, str(e))
            _delete_file_from_storage(storage_path)
            raise


# ======================================================
# LIBCAL TRANSFORMATION LOGIC
# ======================================================


def run_libcal_transform_logic(db, source):
    
    while True:

        try:
            payload = queries.claim_transform_file(db, source)

            if payload is None:
                break

            storage_path = payload.storage_path
            file_id = payload.uploaded_file_id

            file_bytes = supabase.storage.from_("raw_uploads").download(storage_path)

            file_reader = _load_csv_reader(file_bytes)

            file_type = _classify_file(file_reader)

            if file_type not in ["libcal"]:
                raise admin.InvalidFileType("file is not a valid libcal file")
            
            # RAW rows
            rows = _get_rows(db, file_id)

            seen = set()
            events_batch = []

            for row in rows:

                attended = False
                online_event = False
                in_person_event = False

                event_id = None
                start_date = None
                end_date = None
                start_time = None
                end_time = None
                first_name = None
                last_name = None
                registrant_name = None
                organization = None
                tag = None
                event_title = None
                event_type = None
                total_confirmed_registrants = None # how many people actually went
                total_number_registrants = None    # how many people registered
                
                for header, value in row.items():

                    keyword = _classify_libcal(header)

                    if keyword == "event id":

                        if value:
                            event_id = value.strip()

                    elif keyword == "start date":

                        if value:

                            try:
                                start_date = parser.parse(value).date()
                            except:
                                break

                    elif keyword == "end date":
                        
                        if value:

                            try:
                                end_date = parser.parse(value).date()
                            except:
                                break

                    elif keyword == "start time":

                        if value:

                            try:
                                start_time = time.fromisoformat(value)
                            except:
                                break

                    elif keyword == "end time":
                        
                        if value:

                            try:
                                end_time = time.fromisoformat(value)
                            except:
                                break

                    elif keyword == "tag":
                        
                        if value:
                            tag = value.strip()
                    
                    elif keyword == "attended":

                        if value:
                        
                            if value.lower().strip() == "yes":
                                attended = True

                    elif keyword == "in-person seats":

                        if value:

                            try:
                                total_seats = int(value)
                                if total_seats > 0:
                                    in_person_event = True
                            except:
                                break

                    elif keyword == "online seats":
                        
                        if value:

                            try:
                                total_seats = int(value)
                                if total_seats > 0:
                                    online_event = True
                            except:
                                break

                    elif keyword == "first name":

                        if value:
                            first_name = value.lower().strip()
                
                    elif keyword == "last name":

                        if value:
                            last_name = value.lower().strip()

                    elif keyword == "full name":

                        if value:
                            first_name, last_name = value.split()
                            first_name = first_name.lower().strip()
                            last_name = last_name.lower().strip()

                    elif keyword == "registrant name":

                        if value:
                            first_name, last_name = value.split()
                            first_name = first_name.lower().strip()
                            last_name = last_name.lower().strip()

                    elif keyword == "affiliated organization":

                        if value:

                            if value.lower().strip() != "other":
                                organization = value.lower().strip()

                    elif keyword == "not-affiliated organization":

                        if value:

                            if not organization:
                                organization = value.lower().strip()

                    elif keyword == "event title":

                        if value:
                            event_title = value.lower().strip()

                    elif keyword == "confirmed registrants":

                        if value:

                            try:
                                total_number_registrants = int(value)
                            except:
                                break

                    elif keyword == "confirmed attendance":

                        if value:

                            try:
                                total_confirmed_registrants = int(value)
                            except:
                                break

                # check row is valid for insertion

                if not attended:
                    continue

                if not first_name:
                    continue

                if not last_name:
                    continue

                if not event_title:
                    continue

                if in_person_event and online_event:
                    event_type = "hybrid"
                
                elif in_person_event:
                    event_type = "in-person"
                
                elif online_event:
                    event_type = "online"

                else:
                    continue

                key = (event_id, first_name, last_name, event_title, start_time, end_time, start_date, end_date)
            
                if key in seen:
                    continue

                seen.add(key)
            
                registrant_name = first_name + " " + last_name

                events_batch.append({
                    "event_id": event_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "registrant_name": registrant_name,
                    "organization": organization,
                    "tag": tag,
                    "event_title": event_title,
                    "event_type": event_type,
                    "total_confirmed_registrants": total_confirmed_registrants,
                    "total_number_registrants": total_number_registrants,
                    "uploaded_file_id": file_id
                })
               
            if events_batch:
                _insert_events_data(db, events_batch)

            _set_transform_status(db, "completed", file_id)

        except Exception as e:
            logger.exception(f"Failed to transform libcal row. ERROR: {e}")
            # _set_transform_status(db, "failed", file_id, str(e))
            _delete_file_from_storage(storage_path)
            raise


# ======================================================
# MYTURN TRANSFORMATION LOGIC
# ======================================================


def run_myturn_transform_logic(db, source):
    
    while True:

        try:
            payload = queries.claim_transform_file(db, source)

            if payload is None:
                break

            storage_path = payload.storage_path
            file_id = payload.uploaded_file_id

            file_bytes = supabase.storage.from_("raw_uploads").download(storage_path)

            file_reader = _load_csv_reader(file_bytes)

            file_type = _classify_file(file_reader)

            if file_type not in ["loans", "items"]:
                raise admin.InvalidFileType("file is not a valid myturn file")
            
            # RAW rows
            rows = _get_rows(db, file_id)

            loan_batch = []
            items_batch = []

            if file_type == "loans":
                
                for row in rows:

                    first_name = None
                    last_name = None
                    
                    loan_id = None
                    client_name = None
                    organization = None
                    item_name = None
                    item_id = None
                    checkout_at = None
                    returned_at = None
                    renewal = False

                    for header, value in row.items():
                
                        keyword = _classify_myturn(header)

                        if keyword == "loan id":
                
                            try:
                                loan_id = int(value.strip())

                            except:
                                break
                        
                        elif keyword == "first name":
                        
                                try:
                                    first_name = value.lower().strip()

                                except:
                                    break

                        
                        elif keyword == "last name":
                         
                                try:
                                    last_name = value.lower().strip()

                                except:
                                    break
    
                        elif keyword == "organization":

                                try:
                                    organization = value.lower().strip()
                                
                                except:
                                    break

                    

                        elif keyword == "item id":

                                try:
                                    item_id = int(value.strip())
                                
                                except:
                                    break
                           
                        elif keyword == "item name":

                                try:
                                    item_name = value.lower().strip()

                                except:
                                    break

                        elif keyword == "checked out":

                                try:
                                    checkout_at = parser.parse(value)

                                except:
                                    break
                            
                        elif keyword == "checked in":

                                try:
                                    returned_at = parser.parse(value)

                                except:
                                    break

                        elif keyword == "renewal":

                                if value.lower().strip() == "renewal":

                                    renewal = True

                                else:
                                    continue
                                
                    if not loan_id:
                        continue

                    if not first_name:
                        continue

                    if not last_name:
                        continue

                    if not organization:
                        continue

                    if not item_name:
                        continue

                    if not item_id:
                        continue

                    if not checkout_at:
                        continue

                    if not returned_at:
                        continue
                    
                    
                    client_name = first_name + " " + last_name

                    duration = returned_at - checkout_at

                    loan_batch.append({
                        "loan_id": loan_id,
                        "client_name": client_name,
                        "organization": organization,
                        "item_name": item_name,
                        "item_id": item_id,
                        "checkout_at": checkout_at,
                        "returned_at": returned_at,
                        "duration": duration,
                        "renewal": renewal,
                        "uploaded_file_id": file_id
                    })                                
                                
            else:

                for row in rows:

                    item_id = None
                    cost = 0.0

                    for header, value in row.items():
                        
                        keyword = _classify_myturn(header)

                        if keyword == "item id":

                                try:
                                    item_id = int(value)
                        
                                except:
                                    break
                        
                        elif keyword == "cost":

                                try:
                                    value = value.replace(",", "")
                                    cost = float(value)
            
                                except:
                                    break
                    
                    if item_id is None:
                        continue

                    items_batch.append({
                        "uploaded_file_id": file_id,
                        "item_id": item_id,
                        "cost": cost
                    })

            if loan_batch:
                queries.insert_loan_metadata(db, loan_batch)
            
            if items_batch:
                queries.insert_items_metadata(db, items_batch)
            
            _set_transform_status(db, "completed", file_id)

        except Exception as e:
            logger.exception(f"Failed to transform myturn row. ERROR: {e}")
            # _set_transform_status(db, "failed", file_id, str(e))
            _delete_file_from_storage(storage_path)
            raise


# ======================================================
# SET FILE STATUS
# ======================================================


def _set_ingestion_status(db, status: Literal["pending", "processing", "completed", "failed"], file_id: UUID):
    
    queries.update_ingestion_status(db, status, file_id)


def _set_transform_status(db, status: Literal["pending", "processing", "completed", "failed"], file_id: UUID):
    
    queries.update_transform_status(db, status, file_id)


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


def _build_tutorial_views_dto(rows: list[dict]) -> TutorialViews:
    
    # A row has data if at least 2 dictionaries else there is no data.
    VALID_ROWS_LEN = 2

    total = 0 # sum of all views
    data = []

    if len(rows) >= VALID_ROWS_LEN:
        for row in rows:
            date = row.get("metric_date")
            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                # means we got the total "date" alias
                total = int(row.get("views"))
                continue
            views = row.get("views")
            data.append({"date": date, "views": views})

        return TutorialViews(data=data, total=total)
    return TutorialViews(data=data, total=total)


def _classify_niche(header: str) -> Literal["tutorial", "total", "date"]:

    h = header.lower().strip()

    if "tutorial" in h or "tutorial title" in h or "course" in h:
        return "tutorial"
    
    elif "total" in h or "sum" in h or "total views" in h or "attendance" in h:
        return "total"
    
    return "date"


def _normalize_year(two_digit_year: int) -> int:
    
    CURRENT_CENTURY = 2000
    return CURRENT_CENTURY + two_digit_year


# ======================================================
# LIBCAL HELPER FUNCTIONS
# ======================================================


def _insert_events_data(db, batch) -> None:

    queries.insert_event_metadata(db, batch)

def _classify_libcal(header: str) -> str | None:

    h = header.lower().strip()

    if "event" in h and "id" in h:
        return "event id"

    elif "start date" in h or "start-date" in h:
        return "start date"

    elif "end date" in h or "end-date" in h:
        return "end date"

    elif "start time" in h or "start-time" in h:
        return "start time"

    elif "end time" in h or "end-time" in h:
        return "end time"

    elif "internal tag" in h:
        return "tag"

    elif "tag" in h:
        return "tag"
    
    elif "attended" in h or "present" in h:
        return "attended"

    elif "in-person" in h:
        return "in-person seats"

    elif "online" in h:
        return "online seats"
    
    elif "first" in h and "name" in h:
        return "first name"
    
    elif "last" in h and "name" in h:
        return "last name"
    
    elif "full name" in h:
        return "full name"

    elif any(word in h for word in ["registrant name", "person name", "registrant"]):
        return "registrant name"
    
    elif any(word in h for word in ["organization", "affiliation"]):
        return "affiliated organization"
    
    elif "not" in h and ("member" in h or "organization" in h):
        return "not-affiliated organization"
    
    elif "event" in h and "title" in h or "title" in h:
        return "event title"
    
    elif "confirmed" in h and "registration" in h:
        return "confirmed registrants"
    
    elif "confirmed" in h and "attend" in h:
        return "confirmed attendance"

    return None

def _build_event_count_dto(rows: list[dict]) -> TotalEvents:

    total = 0
    data = []
    for row in rows:

        if row.get("event_type") == "total":
            total = row.get("total_events")
        else:
            data.append({"event_type": row.get("event_type"), "total": row.get("total_events")})
    
    return TotalEvents(data=data, total=total)


# ======================================================
# MYTURN HELPER FUNCTIONS
# ======================================================


def _classify_myturn(header: str) -> str | None:

    # logger.debug(f"header original: {header}")

    h = header.lower().strip()

    # logger.debug(f"header after: {h}")

    if "loan" in h and "id" in h:
        return "loan id"
    
    elif "first" in h and "name" in h:
        return "first name"
    
    elif "last" in h and "name" in h:
        return "last name"
    
    elif "organization" in h:
        return "organization"
    
    elif "item" in h and "id" in h:
        return "item id"
    
    elif "item" in h and "name" in h:
        return "item name"
    
    elif "checked" in h and "out" in h:
        return "checked out"
    
    elif "checked" in h and "in" in h:
        return "checked in"
    
    elif "renewal" in h:
        return "renewal"
    
    elif "cost" in h:
        return "cost"
    
    return None


# ======================================================
# FETCHES TOP TUTORIALS
# ======================================================


def top_tutorials(db, limit, start_date, end_date) -> list[TopTutorials]:

    rows = queries.get_top_tutorials(db, limit, start_date, end_date)
    return _build_top_tutorials_dto(rows)


# ======================================================
# FETCHES TUTORIAL VIEWS BY MONTH
# ======================================================


def tutorial_views(db, start_date, end_date) -> TutorialViews:

    rows = queries.get_tutorial_views(db, start_date, end_date)
    return _build_tutorial_views_dto(rows)


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
        

# ======================================================
# EVENT COUNT BY TYPE
# ======================================================

def event_count(db, start_date, end_date) -> TotalEvents:

    rows = queries.get_event_count_by_type(db, start_date, end_date)
    return _build_event_count_dto(rows)


# ======================================================
# GET MOST FREQUENTLY BOUGHT ITEMS
# ======================================================


def get_top_items(db, start_date, end_date, limit) -> TopCheckedOutItems:

    data = queries.get_most_checkedout_items(db, start_date, end_date, limit)

    return TopCheckedOutItems(data=data)


# ======================================================
# TOP ORGANIZATIONS
# ======================================================

def fetch_top_organizations(db, start_date, end_date, limit) -> TopOrganizations:

    data = queries.get_top_organizations(db, start_date, end_date, limit)

    return TopOrganizations(data=data)


# ======================================================
# FIND ALL ITEMS WITH NO COST OR COST = 0
# ======================================================

def free_items(db) -> FreeItems:

    rows = queries.get_all_free_items(db)
    
    total = len(rows)

    return FreeItems(data=rows, total=total)

# ======================================================
# VALIDATE DATE RANGE
# ======================================================

def is_valid_date_range(start_date: date, end_date: date) -> None:
    
    if not start_date <= end_date:
        raise admin.InvalidDateRange