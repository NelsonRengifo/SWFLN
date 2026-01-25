# ======================================================
# app’s connection + access layer to the database.
# ======================================================

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"), pool_size=5, max_overflow=5, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
