# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path


# ======================================================
# LOAD .env
# ======================================================

backend = Path(__file__).resolve().parent
env_path = backend / ".env"
load_dotenv(env_path, override=True)


# ======================================================
# INTERNAL IMPORTS
# ======================================================


from backend.routes.auth import auth_route
from backend.core.logging_config import setup_logging

# ======================================================
# APP
# ======================================================

setup_logging()
app = FastAPI()


# ======================================================
# ROUTE REGISTRATION
# ======================================================


app.include_router(auth_route)
