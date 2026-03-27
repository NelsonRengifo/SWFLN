# WORKER SCRIPT

# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ======================================================
# LOAD .env
# ======================================================


backend = Path(__file__).resolve().parent.parent
env_path = backend / ".env"
load_dotenv(env_path, override=True)


# ======================================================
# INTERNAL IMPORTS
# ======================================================

from backend.clients.supabase import supabase
from backend import queries
from backend.core.database_config import SessionLocal


def _delete_tutorials(db):
    
    queries.delete_orphan_tutorials(db)
        

def _delete_file_from_storage(file_path) -> None:
    
    supabase.storage.from_("raw_uploads").remove([f"{file_path}"])


def run_delete_old_uploaded_files() -> None:
    
    db = SessionLocal()
    
    try:
        storage_paths = queries.delete_old_uploaded_files(db)
        _delete_tutorials(db)
        for file_path in storage_paths:
            _delete_file_from_storage(file_path)
        db.commit()
        print(f"Successfully ran 'delete_old_files.py' on '{datetime.now()}'")
    
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to delete old files. ERROR: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    run_delete_old_uploaded_files()
    