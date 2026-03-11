# ======================================================
# EXTERNAL IMPORTS
# ======================================================


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


from backend.routes.auth  import auth_route
from backend.routes.admin import admin_route
from backend.core.logging_config import setup_logging

# ======================================================
# APP
# ======================================================

setup_logging()
app = FastAPI()

# This enables the frontend and backend to communicate during development.
# In production REMOVE those and allow only your real frontend origin.
origins = ["http://127.0.0.1:5500", "http://localhost:5500"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


# ======================================================
# ROUTE REGISTRATION
# ======================================================


app.include_router(auth_route)
app.include_router(admin_route)
