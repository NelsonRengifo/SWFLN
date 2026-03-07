# PENDING if status = failed: debug, change to pending or keep as fail.
# PENDING: REFACTOR db session logic to avoid opening closing twice


# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from dotenv import load_dotenv
from pathlib import Path
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

from backend import queries
from backend.core.database_config import SessionLocal


def run_ingestion_worker():

    db = SessionLocal()

    try:
        queries.recover_ingestion_job(db)
        db.commit()
    
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to recover uploaded files. ERROR: {e}")
        raise
    
    finally:
        db.close()


def run_transform_worker():

    db = SessionLocal()

    try:
        queries.recover_transform_job(db)
        db.commit()
    
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to run transform recovery. ERROR: {e}")
        raise
    
    finally:
        db.close()



if __name__ == "__main__":
    run_ingestion_worker()
    run_transform_worker()