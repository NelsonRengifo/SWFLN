# WORKER SCRIPT
# PENDING: REFACTOR db session logic to open and close once.

# ======================================================
# EXTERNAL IMPORTS
# ======================================================

from sqlalchemy.engine import Row
from dotenv import load_dotenv
from pathlib import Path
from typing import Literal
from uuid import UUID
from dateutil import parser
import logging
import io
import csv

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
from backend.clients.supabase import supabase
from backend.core.database_config import SessionLocal
import backend.models
import logging

logger = logging.getLogger(__name__)

# ======================================================
# HELPER FUNCTIONS
# ======================================================


def _set_ingestion_status(db, status: Literal["pending", "processing", "completed", "failed"], file_id: UUID, error_message=None):
    
    queries.update_ingestion_status(db, status, file_id, error_message)


def _set_transform_status(db, status: Literal["pending", "processing", "completed", "failed"], file_id: UUID, error_message=None):
    
    queries.update_transform_status(db, status, file_id, error_message)


def _insert_raw_row(db, data: list[dict]) -> int:
    
    return queries.insert_raw_row_data(db, data)


def _get_rows(db, file_id) -> list[dict]:
    
    return queries.fetch_raw_rows(db, file_id)


def _insert_tutorials(db, tutorial_names) -> None:

    return queries.insert_tutorial_names(db, tutorial_names)


def _insert_tutorial_metrics(db, tutorial_metrics) -> None:

    queries.insert_tutorial_data(db, tutorial_metrics)


def _get_tutorial_mapping(db) -> dict:

    return queries.tutorial_mapping(db)



# ======================================================
# INGESTION LOGIC
# ======================================================


def run_ingestion_logic() -> None:
    
    db = SessionLocal()

    try:
        
        while True:

            try:
                payload  = queries.claim_ingestion_file(db)
                if payload is None:
                    break # There are no files waiting to be processed

                storage_path = payload.storage_path
                file_id = payload.uploaded_file_id
                file_bytes = supabase.storage.from_("raw_uploads").download(storage_path)

                file_text = file_bytes.decode()
                file_stream = io.StringIO(file_text)
                file_reader = csv.DictReader(file_stream)
                if not file_reader.fieldnames:
                    logger.warning(f"Missing CSV headers {storage_path}")
                    _set_ingestion_status(db, "failed", file_id, "missing csv headers")
                    continue

                # Multi-value insert method
                batch = []
                BATCH_LIMIT = 5000
                for row_number, row in enumerate(file_reader, start=1):
                    batch.append({
                        "uploaded_file_id": file_id,
                        "raw_data": row,
                        "row_number": row_number
                    })
                    # 5000 rows of data
                    if len(batch) >= BATCH_LIMIT:
                        inserted_ids = _insert_raw_row(db, batch)
                        # check we actually inserted 5000 rows of data
                        assert inserted_ids == len(batch)
                        batch.clear()

                if batch:
                    inserted_ids = _insert_raw_row(db, batch)
                    assert inserted_ids == len(batch)
                
                _set_ingestion_status(db, "completed", file_id)
                db.commit()
    

            except Exception as e:
                db.rollback()
                logger.exception(f"Failed to process uploaded files. ERROR: {e}")
                _set_ingestion_status(db, "failed", file_id, str(e))
                db.commit()

    finally:
        db.close()


# ======================================================
# TRANSFORMATION LOGIC
# ======================================================


def run_transform_logic() -> None:

    db = SessionLocal()

    try:

        while True:

            try:
                file_id = queries.claim_transform_file(db)
                if file_id is None:
                    break # There are no files waiting to be transformed
                
                # RAW rows
                rows = _get_rows(db, file_id)

                # collect tutorial names
                tutorial_names = list({"tutorial_name": row.get("Tutorial")} for row in rows[:-1])
                if None in tutorial_names:
                    raise ValueError("Missing tutorial name")
                
                # batch insert tutorials
                if tutorial_names:
                    _insert_tutorials(db, tutorial_names)

                # tutorial_name -> tutorial_id mapping
                result = _get_tutorial_mapping(db)
                tutorial_mapping = {row["tutorial_name"]: row["tutorial_id"] for row in result}
                 
                # build batch insert for metrics
                seen = set()
                tutorial_metrics = []
                for row in rows[:-1]:
                    tutorial_id = tutorial_mapping[row["Tutorial"]]
                    for key, value in row.items():
                        if key not in ["Tutorial", "Total"]:
                            metric_date = parser.parse(key).replace(day=1).date()
                            if (tutorial_id, metric_date) in seen:
                                continue
                            seen.add((tutorial_id, metric_date))
                            total_views = int(value)
                            tutorial_metrics.append({
                                "tutorial_id": tutorial_id,
                                "metric_date": metric_date,
                                "total_views": total_views,
                                "uploaded_file_id": file_id
                            })

                # batch insert tutorial_metric
                if tutorial_metrics:
                    _insert_tutorial_metrics(db, tutorial_metrics)

                _set_transform_status(db, "completed", file_id)
            
            except Exception as e:
                db.rollback()
                logger.exception(f"Failed to transform row. ERROR: {e}")
                _set_transform_status(db, "failed", file_id, str(e))
                db.commit()

    finally:
        db.close()


if __name__ == "__main__":
    run_ingestion_logic()
    run_transform_logic()