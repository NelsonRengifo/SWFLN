# Supabase        → runs PostgreSQL database
# SQLAlchemy      → connects to DB and executes queries via sessions
# FastAPI routes  → use sessions (SQLAlchemy) to handle requests (Client or Frontend)

from fastapi import FastAPI


app = FastAPI()
