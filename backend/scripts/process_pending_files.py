# WORKER SCRIPT

# ======================================================
# EXTERNAL IMPORTS
# ======================================================

from datetime import time
from sqlalchemy.orm.session import Session
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

def _create_db_session() -> Session:

    return SessionLocal()


def _load_csv_reader(file_bytes: bytes) -> csv.DictReader:

    file_text = file_bytes.decode()
    # creates an in-memory file-like object for strings so it can be used by DictReader
    file_stream = io.StringIO(file_text)
    # reads a CSV file and returns each row as a dictionary instead of a list so we can access by name
    file_reader = csv.DictReader(file_stream)

    return file_reader


def _insert_raw_rows_batch(db, file_reader: bytes, file_id: UUID) -> None:

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


# ======================================================
# NICHE PENDING FILES
# ======================================================


def run_niche_ingestion_logic(db, source) -> None:

    while True:

        try:
            payload  = queries.claim_ingestion_file(db, source)
            if payload is None:
                break # There are no files waiting to be processed

            storage_path = payload.storage_path
            file_id = payload.uploaded_file_id

            file_bytes = supabase.storage.from_("raw_uploads").download(storage_path)

            file_reader = _load_csv_reader(file_bytes)
            if not file_reader.fieldnames:
                logger.warning(f"Missing CSV headers {storage_path}")
                _set_ingestion_status(db, "failed", file_id, "missing csv headers")
                continue

            _insert_raw_rows_batch(file_reader, file_id)
            _set_ingestion_status(db, "completed", file_id)
            db.commit()

        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to process niche uploaded file. ERROR: {e}")
            _set_ingestion_status(db, "failed", file_id, str(e))
            db.commit()

  

# ======================================================
# NICHE HELPER FUNCTIONS
# ======================================================


def _insert_tutorials(db, tutorial_names) -> None:

    return queries.insert_tutorial_names(db, tutorial_names)


def _insert_tutorial_metrics(db, tutorial_metrics) -> None:

    queries.insert_tutorial_data(db, tutorial_metrics)


def _get_tutorial_mapping(db) -> dict:

    return queries.tutorial_mapping(db)



# ======================================================
# NICHE TRANSFORMATION LOGIC
# ======================================================


def run_niche_transform_logic(db, source) -> None:

    while True:

        try:
            file_id = queries.claim_transform_file(db, source)
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
            db.commit()
        
        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to transform niche row. ERROR: {e}")
            _set_transform_status(db, "failed", file_id, str(e))
            db.commit()



# ======================================================
# LIBCAL HELPER FUNCTIONS
# ======================================================


def _insert_events_data(db, batch) -> None:

    queries.insert_event_metadata(db, batch)

def _get_event_mapping(db) -> dict:

    return queries.event_mapping(db)

def _insert_registrant_data(db, batch) -> None:
    
    queries.insert_registrant_metadata(db, batch)


# ======================================================
# LIBCAL PENDING FILES
# ======================================================


def run_libcal_ingestion_logic(db, source) -> None:

    while True:

        try:
            payload  = queries.claim_ingestion_file(db, source)
            if payload is None:
                break # There are no files waiting to be processed

            storage_path = payload.storage_path
            file_id = payload.uploaded_file_id
            file_bytes = supabase.storage.from_("raw_uploads").download(storage_path)

            file_reader = _load_csv_reader(file_bytes)
            if not file_reader.fieldnames:
                logger.warning(f"Missing CSV headers {storage_path}")
                _set_ingestion_status(db, "failed", file_id, "missing csv headers")
                continue
            
            _insert_raw_rows_batch(db, file_reader, file_id)
            _set_ingestion_status(db, "completed", file_id)
            db.commit()

        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to process libcal uploaded file. ERROR: {e}")
            _set_ingestion_status(db, "failed", file_id, str(e))
            db.commit()


# ======================================================
# LIBCAL TRANSFORMATION LOGIC 
# ======================================================


def run_libcal_transform_logic(db, source):
    
     while True:

        try:
            file_id = queries.claim_transform_file(db, source)
            if file_id is None:
                break # There are no files waiting to be transformed
            
            # RAW rows
            rows = _get_rows(db, file_id)

            seen = set()
            events_batch = []
            registrants_batch = []

            for row in rows:
                first_name = row.get("First Name")
                last_name = row.get("Last Name")
                if not first_name or not last_name:
                    continue
                
                attended = row.get("Attended")

                # attended field was left empty
                if not attended:
                    continue

                full_name = ""
                if attended.lower() == 'yes':
                        full_name += first_name.lower().strip() + " " + last_name.lower().strip()
                else:
                    # attended field == no
                    continue

                event_id = row.get("Event ID")
                event_title = row.get("Title")
                start_time = row.get("Start Time")
                end_time = row.get("End Time")
                start_date = row.get("Start Date")
                end_date = row.get("End Date")

                # Determines if duplicate row
                
                key = (event_id, first_name, last_name, event_title, start_time, end_time)

                if key in seen:
                    continue
                
                seen.add(key)

                # normalize data
                start_date = parser.parse(start_date).date()
                end_date = parser.parse(end_date).date()
                title = event_title.strip()
                start_time = time.fromisoformat(start_time)
                end_time = time.fromisoformat(end_time)
                # total people who registered for the event
                total_number_registrants = int(row.get("Confirmed Registrations"))
                # total people who actually showed up
                total_confirmed_registrants = int(row.get("Confirmed Attendance"))
                
                events_batch.append({
                    "start_date": start_date,
                    "end_date": end_date,
                    "registrant_name": full_name,
                    "event_title": title,
                    "total_confirmed_registrants": total_confirmed_registrants,
                    "total_number_registrants": total_number_registrants,
                    "uploaded_file_id": file_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "event_id": event_id
                })
               
            if events_batch:
                _insert_events_data(db, events_batch)
            
            # result = _get_event_mapping(db)
            # event_mapping = {row["registrant_name"]: row["id"] for row in result}

            # for row in events_batch:

            #     registrants_batch.append({
            #         "id": event_mapping[row["registrant_name"]],
            #         "registrant_name": row["registrant_name"]
            #     })
            
            # if registrants_batch:
            #     _insert_registrant_data(db, registrants_batch)

            _set_transform_status(db, "completed", file_id)
            db.commit()

        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to transform libcal row. ERROR: {e}")
            _set_transform_status(db, "failed", file_id, str(e))
            db.commit()


if __name__ == "__main__":
    
    db = _create_db_session()
    
    try:
        run_niche_ingestion_logic(db, 'niche')
        run_niche_transform_logic(db, 'niche')
        run_libcal_ingestion_logic(db, 'libcal')
        run_libcal_transform_logic(db, 'libcal')
    
    finally:
        db.close()