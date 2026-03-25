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


def run_cleanup_orphan_tutorials() -> None:

    db = SessionLocal()

    try:
        queries.delete_orphan_tutorials(db)
        
    except Exception as e:
        logger.exception(f"Failed to run cleanup orphan tutorials job | ERROR: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    run_cleanup_orphan_tutorials()