# REFACTOR: Check if using RETURNING incorrectly...

# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from pathlib import Path
from sqlalchemy import text, bindparam, delete, func
from sqlalchemy.engine import Row
from uuid import UUID
from sqlalchemy.dialects.postgresql import ARRAY, TEXT, insert
import logging

logger = logging.getLogger(__name__)

# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.models.raw_rows import RawRows
from backend.models.tutorials import Tutorials
from backend.models.tutorial_metrics import TutorialMetrics
from backend.models.events import Events
from backend.models.uploaded_files import UploadedFiles
from backend.models.loans import Loans
from backend.models.items import Items


# ======================================================
# CREATES ABS PATH TO SQL FOLDER & LOADS .sql FILES
# ======================================================


backend_path = Path(__file__).resolve().parent
sql_path = backend_path / "sql"


def load_sql(filename, folder=None) -> str:
    """
    returns the content of a .sql file

    :param filename: the .sql file to load
    """
    if not folder:
        filepath = f"{sql_path}/{filename}.sql"

    else:
        filepath = f"{sql_path}/{folder}/{filename}.sql"

    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


# ======================================================
# GENERATES ENTIRE SCHEMA
# ======================================================


def generate_schema(db) -> None:

    sql = load_sql("schema")
    db.execute(text(sql))


# ======================================================
# CREATES THE SUPER ADMIN
# ======================================================


def create_super_admin(db, param) -> None:

    sql = load_sql("create_super_admin", "auth")
    db.execute(text(sql), param)
       


# ======================================================
# AUTH FUNCTIONS
# ======================================================


def get_user_for_auth_by_username(db, username) -> Row | None:

    sql = load_sql("get_user_for_auth_by_username", "auth")
    return db.execute(text(sql), {"username": username}).one_or_none()


def exists_username(db, username) -> bool:

    sql = load_sql("exists_username", "auth")
    return db.execute(text(sql), {"username": username}).scalar()


def exists_user_role(db, token_hash, roles: list[str]) -> bool:

    param = {"token_hash": token_hash, "valid_roles": roles}

    sql = load_sql("exists_user_role", "auth")
    return db.execute(text(sql).bindparams(bindparam("valid_roles", type_=ARRAY(TEXT))), param).scalar()


def exists_email(db, email) -> bool:

    sql = load_sql("exists_email", "auth")
    return db.execute(text(sql), {"email": email}).scalar()


def create_user(db, username, password_hash, email, first_name, last_name, user_role) -> UUID:

    sql = load_sql("create_user", "auth")
    param = {
        "username": username,
        "password_hash": password_hash,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "user_role": user_role
    }

    return db.execute(text(sql), param).scalar_one()


def create_session_token(db, user_id, token_hash) -> UUID:

    sql = load_sql("create_session_token", "auth")
    params = {"user_id": user_id, "token_hash": token_hash}
    return db.execute(text(sql), params).scalar_one()


def get_session_info_by_token_hash(db, token_hash) -> Row | None:

    sql = load_sql("get_session_info_by_token_hash", "auth")
    return db.execute(text(sql), {"token_hash": token_hash}).one_or_none()


def delete_session_token_by_token_hash(db, token_hash) -> Row | None:

    sql = load_sql("delete_session_token_by_token_hash", "auth")
    return db.execute(text(sql), {"token_hash": token_hash}).one_or_none()


def extend_session_expiry(db, user_id, token_hash) -> None:

    params = {
        "user_id": user_id,
        "token_hash": token_hash
    }
    sql = load_sql("extend_session_expiry", "auth")
    db.execute(text(sql), params)


def get_user_password_by_user_id(db, user_id) -> Row | None:

    sql = load_sql("get_user_password_by_user_id", "auth")
    return db.execute(text(sql), {"user_id": user_id}).scalar_one()


def update_user_password_by_user_id(db, password_hash, user_id) -> UUID:

    sql = load_sql("update_user_password_by_user_id", "auth")
    params = {"password_hash": password_hash, "user_id": user_id}
    return db.execute(text(sql), params).scalar_one()


def delete_sessions_by_user_id(db, user_id) -> None:

    sql = load_sql("delete_sessions_by_user_id", "auth")
    db.execute(text(sql), {"user_id": user_id})


def update_user_username_by_user_id(db, new_username, user_id) -> UUID:

    sql = load_sql("update_user_username_by_user_id", "auth")
    params = {"username": new_username, "user_id": user_id}
    db.execute(text(sql), params).scalar_one()


def get_user_id_for_transaction_by_email(db, email) -> UUID | None:

    sql = load_sql("get_user_id_for_transaction_by_email", "auth")
    return db.execute(text(sql), {"email": email}).scalar_one_or_none()


def create_password_reset_token(db, user_id, token_hash) -> UUID:

    sql = load_sql("create_password_reset_token", "auth")
    params = {"user_id": user_id, "token_hash": token_hash}
    return db.execute(text(sql), params).scalar_one()


def get_reset_session_info_by_token_hash(db, token_hash) -> Row | None:

    sql = load_sql("get_reset_session_info_by_token_hash", "auth")
    return db.execute(text(sql), {"token_hash": token_hash}).one_or_none()


def get_user_username_by_email(db, email) -> str | None:

    sql = load_sql("get_user_username_by_email", "auth")
    return db.execute(text(sql), {"email": email}).scalar_one_or_none()


# ======================================================
# ADMIN FUNCTIONS
# ======================================================


def exists_file(db, checksum_sha256) -> bool:

    sql = load_sql("exists_file", "admin")
    return db.execute(text(sql), {"checksum_sha256": checksum_sha256}).scalar()


def create_new_file(db, data) -> UUID:

    sql = load_sql("create_new_file", "admin")
    return db.execute(text(sql), data).scalar_one()


def get_top_tutorials(db, limit, start_date, end_date) -> list[Row]:

    params = {
        "limit": limit,
        "start_date": start_date,
        "end_date": end_date
    }
    sql = load_sql("get_top_tutorials", "admin")
    return db.execute(text(sql), params).all()


def delete_uploaded_files(db, file_ids: list[UUID]) -> list[str]:
    # returns a list of storage paths

    delete_obj = delete(UploadedFiles).where(UploadedFiles.uploaded_file_id.in_(file_ids)).returning(UploadedFiles.storage_path)
    return db.execute(delete_obj).scalars().all()


def get_file_data(db, offset_value, source) -> list[Row]:

    params = {
        "OFFSET": offset_value,
        "source": source
    }
    sql = load_sql("get_file_data", "admin")
    return db.execute(text(sql), params).all()


def get_tutorial_views(db, start_date, end_date) -> list[dict]:

    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    sql = load_sql("get_tutorial_views", "admin")
    return db.execute(text(sql), params).mappings().all()


def get_event_count_by_type(db, start_date, end_date) -> list[dict]:

    sql = load_sql("get_event_count_by_type", "admin")
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    return db.execute(text(sql), params).mappings()


def get_most_checkedout_items(db, start_date, end_date, limit) -> list[dict]:

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit
    }

    sql = load_sql("get_most_checkedout_items", "admin")
    return db.execute(text(sql), params).mappings()


def get_top_organizations(db, start_date, end_date, limit) -> list[dict]:
    
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit
    }

    sql = load_sql("get_top_organizations", "admin")
    return db.execute(text(sql), params).mappings()


def get_all_free_items(db) -> list[dict]:

    sql = load_sql("get_all_free_items", "admin")
    return db.execute(text(sql)).mappings().all()

# ======================================================
# WORKER FUNCTIONS
# ======================================================


def delete_expired_tokens(db) -> None:

  
    sql1 = load_sql("delete_expired_reset_tokens", "jobs")
    sql2 = load_sql("delete_expired_sessions", "jobs")
    db.execute(text(sql1))
    db.execute(text(sql2))


def claim_ingestion_file(db, source) -> Row | None:

    sql = load_sql("claim_ingestion_file", "jobs")
    return db.execute(text(sql), {"source": source}).one_or_none()



def update_ingestion_status(db, file_status, uploaded_file_id) -> None:

    params = {
        "ingestion_status": file_status,
        "uploaded_file_id": uploaded_file_id
    }
    sql = load_sql("update_ingestion_status", "jobs")
    db.execute(text(sql), params)


# def recover_ingestion_job(db) -> None:

#     sql = load_sql("recover_ingestion_job", "jobs")
#     db.execute(text(sql))


def claim_transform_file(db, source) -> Row | None:
    
    sql = load_sql("claim_transform_file", "jobs")
    return db.execute(text(sql), {"source": source}).one_or_none()


def update_transform_status(db, file_status, uploaded_file_id) -> None:
    
    params = {
        "transform_status": file_status,
        "uploaded_file_id": uploaded_file_id
    }
    sql = load_sql("update_transform_status", "jobs")
    db.execute(text(sql), params)


# def recover_transform_job(db) -> None:
    
#     sql = load_sql("recover_transform_job", "jobs")
#     db.execute(text(sql))


def insert_raw_row_data(db, data) -> int:

    insert_obj = insert(RawRows).returning(1)
    rows = db.execute(insert_obj, data).all()
    return len(rows)


def fetch_raw_rows(db, file_id) -> list[dict]:
    
    sql = load_sql("fetch_raw_rows", "jobs")
    return db.execute(text(sql), {"uploaded_file_id": file_id}).scalars().all()


def insert_tutorial_names(db, tutorial_names) -> None:
    
    insert_obj = insert(Tutorials).on_conflict_do_nothing(index_elements=["tutorial_name"])
    db.execute(insert_obj, tutorial_names)


def tutorial_mapping(db) -> dict:

    sql = load_sql("tutorial_mapping", "jobs")
    return db.execute(text(sql)).mappings()


def insert_tutorial_data(db, tutorial_metrics) -> None:

    insert_obj = insert(TutorialMetrics)
    # index_elements specifies the column(s) that define the conflict key
    insert_obj = insert_obj.on_conflict_do_update(
        index_elements=["tutorial_id", "metric_date"], 
        set_={"total_views": insert_obj.excluded.total_views, "uploaded_file_id": insert_obj.excluded.uploaded_file_id}
    )
    db.execute(insert_obj, tutorial_metrics)


def delete_orphan_tutorials(db) -> None:

    sql = load_sql("delete_orphan_tutorials", "jobs")
    db.execute(text(sql))


def insert_event_metadata(db, events_batch) -> None:

    insert_obj = insert(Events)
    insert_obj = insert_obj.on_conflict_do_update(
        index_elements=["registrant_name", "start_date", "end_date", "event_title", "start_time", "end_time"],
        set_= {
            "total_confirmed_registrants": insert_obj.excluded.total_confirmed_registrants,
            "uploaded_file_id": insert_obj.excluded.uploaded_file_id,
            "total_number_registrants": insert_obj.excluded.total_number_registrants
        }
    )
    db.execute(insert_obj, events_batch)
    

def insert_loan_metadata(db, loans_batch) -> None:
    
    insert_obj = insert(Loans)
    insert_obj = insert_obj.on_conflict_do_nothing(index_elements=["loan_id"])
    db.execute(insert_obj, loans_batch)


def insert_items_metadata(db, items_batch) -> None:

    insert_obj = insert(Items)
    insert_obj = insert_obj.on_conflict_do_update(index_elements=["item_id"], set_= {"cost": insert_obj.excluded.cost})
    db.execute(insert_obj, items_batch)


def delete_old_uploaded_files(db) -> list[str]:
    # file is old at 2 year mark
    # returns a list of storage paths

    delete_obj = delete(UploadedFiles).where(UploadedFiles.uploaded_at + text("INTERVAL '2 years'") < func.now()).returning(UploadedFiles.storage_path)
    return db.execute(delete_obj).scalars().all()
