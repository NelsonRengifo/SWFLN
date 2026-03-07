# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from dotenv import load_dotenv
from pathlib import Path


# ======================================================
# LOAD .env
# ======================================================


backend = Path(__file__).resolve().parent.parent
env_path = backend / ".env"
load_dotenv(env_path, override=True)


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.core.database_config import SessionLocal
from backend import queries



def create_tables() -> None:

    db = SessionLocal()

    try:
        queries.generate_schema(db)
        db.commit()
        print("schema created")
    
    except Exception as e:
        db.rollback()
        print(f"failed to generate schema. ERROR: {e}")
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
