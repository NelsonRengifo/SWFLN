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


from backend.queries import generate_schema



def create_tables():
    generate_schema()


if __name__ == "__main__":
    create_tables()
