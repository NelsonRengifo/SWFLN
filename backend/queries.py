# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from pathlib import Path
from sqlalchemy import text, bindparam
from sqlalchemy.engine import Row
from uuid import UUID
from sqlalchemy.dialects.postgresql import ARRAY, TEXT


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.core.database_config import SessionLocal


# ======================================================
# CREATES ABS PATH TO SQL FOLDER & LOADS .sql FILES
# ======================================================


backend_path = Path(__file__).resolve().parent
sql_path = backend_path / "sql"


def load_sql(filename, folder=None) -> None:
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


def generate_schema() -> None:

    db = SessionLocal()

    try:
        sql = load_sql("schema")
        db.execute(text(sql))
        db.commit()
        print("schema created")
    except Exception:
        db.rollback()
        print("failed to generate schema")
        raise
    finally:
        db.close()

# ======================================================
# CREATES THE SUPER ADMIN
# ======================================================


def create_super_admin(param) -> None:

    db = SessionLocal()

    try:
        sql = load_sql("create_super_admin", "auth")
        user_id = db.execute(text(sql), param).scalar_one()
        db.commit()
        print(f"super admin created: ID {user_id}")
    except Exception:
        db.rollback()
        print(f"failed to generate super admin")
        raise
    finally:
        db.close()


# ======================================================
# AUTH FUNCTIONS
# ======================================================


def get_user_for_auth(db, username) -> Row | None:

    sql = load_sql("get_user_for_auth", "auth")
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


def get_session_token(db, token_hash) -> Row | None:

    sql = load_sql("get_session_token", "auth")
    return db.execute(text(sql), {"token_hash": token_hash}).one_or_none()


def delete_session_token(db, token_hash) -> Row | None:

    sql = load_sql("delete_session_token", "auth")
    return db.execute(text(sql), {"token_hash": token_hash}).one_or_none()


def extend_session_expiry(db, token_hash) -> None:

    sql = load_sql("extend_session_expiry", "auth")
    db.execute(text(sql), {"token_hash": token_hash})
