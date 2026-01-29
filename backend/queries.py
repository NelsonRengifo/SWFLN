from pathlib import Path
from backend.core.database_config import SessionLocal
from sqlalchemy import text

# ======================================================
# CREATES ABS PATH TO SQL FOLDER
# ======================================================
backend_path = Path(__file__).resolve().parent
sql_path = backend_path / "sql"


def load_sql(filename):
    """
    returns the content of a .sql file

    :param filename: the .sql file to load
    """
    filepath = f"{sql_path}/{filename}.sql"
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def generate_schema():

    db = SessionLocal()

    try:
        sql = load_sql("schema")
        db.execute(text(sql))
        db.commit()
    except Exception:
        db.rollback()
        print("failed to generate schema")
        raise
    finally:
        db.close()
