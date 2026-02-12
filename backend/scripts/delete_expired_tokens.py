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


from backend import queries


def run_delete_expired_tokens() -> None:
    queries.delete_expired_tokens()


if __name__ == "__main__":
    run_delete_expired_tokens()
    