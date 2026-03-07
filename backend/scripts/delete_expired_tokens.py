# WORKER SCRIPT

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


def run_delete_expired_tokens() -> None:
    
    db = SessionLocal()
    
    try:
        queries.delete_expired_tokens(db)
        db.commit()
    
    except Exception as e:
        db.rollback()
        logger.exception(f"Failed to delete expired tokens. ERROR: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    run_delete_expired_tokens()
    