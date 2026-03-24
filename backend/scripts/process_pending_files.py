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
from backend.exceptions import admin
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


# ======================================================
# CHECKS FILE HAS HEADERS
# ======================================================


def _is_valid_file(file_reader) -> bool:

    return False if not file_reader.fieldnames else True


# ======================================================
# CLASSIFY FILE TYPE
# ======================================================


def _classify_file(file_reader) -> Literal["niche", "libcal", "loans", "items"] | None:

    # loans and items are both myturn files with different data.
    NICHE = ["tutorial"]
    LIBCAL = ["event id", "attended", "start time", "end time", "start date", "end date"]
    LOANS = ["loan id", "checked out", "checked in", "renewal"]
    ITEMS = ["historical cost", "item cost"]

    # get the file headers -> list[str]
    headers = file_reader.fieldnames

    for h in headers:

        h = h.lower().strip()
        
        if h in NICHE:
            return "niche"
        
        elif h in LIBCAL:
            return "libcal"
        
        elif h in LOANS:
            return "loans"
        
        elif h in ITEMS:
            return "items"
    
    return None


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

            if not _is_valid_file(file_reader):
                logger.warning(f"Missing CSV headers {storage_path}")
                _set_ingestion_status(db, "failed", file_id, "missing csv headers")
                continue

            file_type = _classify_file(file_reader)

            if file_type != "niche":
                raise admin.InvalidFileType("file is not a valid niche file")
            
            _insert_raw_rows_batch(db, file_reader, file_id)
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

def _classify_niche(header: str) -> Literal["tutorial", "total", "date"]:

    h = header.lower().strip()

    if "tutorial" in h or "tutorial title" in h or "course" in h:
        return "tutorial"
    
    elif "total" in h or "sum" in h or "total views" in h or "attendance" in h:
        return "total"
    
    return "date"


# ======================================================
# NICHE TRANSFORMATION LOGIC
# ======================================================


def run_niche_transform_logic(db, source) -> None:

    while True:

        try:
            payload = queries.claim_transform_file(db, source)

            if payload is None:
                break # There are no files waiting to be transformed

            storage_path = payload.storage_path
            file_id = payload.uploaded_file_id
            
            file_bytes = supabase.storage.from_("raw_uploads").download(storage_path)

            file_reader = _load_csv_reader(file_bytes)

            file_type = _classify_file(file_reader)

            if file_type != "niche":
                raise admin.InvalidFileType("file is not a valid niche file")
            
            # RAW rows
            rows = _get_rows(db, file_id)

            filtered_rows = [] # store the valid rows

            for row in rows:
            
                name = None
                has_valid_value = False

                for header, value in row.items():    
                    keyword = _classify_niche(header)

                    if keyword == "tutorial":

                        if value: # we have a tutorial name

                            if value.lower().strip() == "total": # invalid tutorial name
                                break
                            
                            name = value # found a valid tutorial name

                        else: # tutorial has no name
                            break
                    
                    elif keyword == "total": # dont care about this header
                        continue
                        
                    else: # must be the date column
                        try:
                            val = int(value)
                            if val > 0: # we only care if tutorial has at least 1 view
                                has_valid_value = True
                                continue
                        except:
                            break
                
                if not name:
                    continue

                if not has_valid_value:
                    continue
                
                filtered_rows.append(row)

            # collect tutorial names
            tutorial_names = []

            for row in filtered_rows:
                
                for header, value in row.items():    
                    keyword = _classify_niche(header)

                    if keyword == "tutorial":
                        tutorial_names.append({"tutorial_name": value})
            
            # batch insert tutorials
            if tutorial_names:
                _insert_tutorials(db, tutorial_names)

            # tutorial_name -> tutorial_id mapping
            result = _get_tutorial_mapping(db)
            tutorial_mapping = {row["tutorial_name"]: row["tutorial_id"] for row in result}
                
            # build batch insert for metrics
            seen = set()
            tutorial_metrics = []

            for row in filtered_rows:
                
                tutorial_id = None
                metric_date = None
                total_views = None

                for header, value in row.items():
                    keyword = _classify_niche(header)

                    if keyword == "tutorial":
                        tutorial_id = tutorial_mapping[value]

                    elif keyword == "total":
                        continue

                    else:
                        metric_date = parser.parse(header).replace(day=1).date()
                        total_views = value

                if (tutorial_id, metric_date) in seen:
                    continue
                    
                seen.add((tutorial_id, metric_date))

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


def _classify_libcal(header: str) -> str | None:

    h = header.lower().strip()

    if "event" in h and "id" in h:
        return "event id"

    elif "start date" in h or "start-date" in h:
        return "start date"

    elif "end date" in h or "end-date" in h:
        return "end date"

    elif "start time" in h or "start-time" in h:
        return "start time"

    elif "end time" in h or "end-time" in h:
        return "end time"

    elif "internal tag" in h:
        return "tag"

    elif "tag" in h:
        return "tag"
    
    elif "attended" in h or "present" in h:
        return "attended"

    elif "in-person" in h:
        return "in-person seats"

    elif "online" in h:
        return "online seats"
    
    elif "first" in h and "name" in h:
        return "first name"
    
    elif "last" in h and "name" in h:
        return "last name"
    
    elif "full name" in h:
        return "full name"

    elif any(word in h for word in ["registrant name", "person name", "registrant"]):
        return "registrant name"
    
    elif any(word in h for word in ["organization", "affiliation"]):
        return "affiliated organization"
    
    elif "not" in h and ("member" in h or "organization" in h):
        return "not-affiliated organization"
    
    elif "event" in h and "title" in h or "title" in h:
        return "event title"
    
    elif "confirmed" in h and "registration" in h:
        return "confirmed registrants"
    
    elif "confirmed" in h and "attend" in h:
        return "confirmed attendance"

    return None


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

            if not _is_valid_file(file_reader):
                logger.warning(f"Missing CSV headers {storage_path}")
                _set_ingestion_status(db, "failed", file_id, "missing csv headers")
                continue

            file_type = _classify_file(file_reader)

            if file_type != "libcal":
                raise admin.InvalidFileType("file is not a valid libcal file")
            
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
            payload = queries.claim_transform_file(db, source)

            if payload is None:
                break

            storage_path = payload.storage_path
            file_id = payload.uploaded_file_id

            file_bytes = supabase.storage.from_("raw_uploads").download(storage_path)

            file_reader = _load_csv_reader(file_bytes)

            file_type = _classify_file(file_reader)

            if file_type != "libcal":
                raise admin.InvalidFileType("file is not a valid libcal file")
            
            # RAW rows
            rows = _get_rows(db, file_id)

            seen = set()
            events_batch = []

            for row in rows:

                attended = False
                online_event = False
                in_person_event = False

                event_id = None
                start_date = None
                end_date = None
                start_time = None
                end_time = None
                first_name = None
                last_name = None
                registrant_name = None
                organization = None
                tag = None
                event_title = None
                event_type = None
                total_confirmed_registrants = None # how many people actually went
                total_number_registrants = None    # how many people registered
                
                for header, value in row.items():

                    keyword = _classify_libcal(header)

                    if keyword == "event id":

                        if value:
                            event_id = value.strip()

                    elif keyword == "start date":

                        if value:

                            try:
                                start_date = parser.parse(value).date()
                            except:
                                break

                    elif keyword == "end date":
                        
                        if value:

                            try:
                                end_date = parser.parse(value).date()
                            except:
                                break

                    elif keyword == "start time":

                        if value:

                            try:
                                start_time = time.fromisoformat(value)
                            except:
                                break

                    elif keyword == "end time":
                        
                        if value:

                            try:
                                end_time = time.fromisoformat(value)
                            except:
                                break

                    elif keyword == "tag":
                        
                        if value:
                            tag = value.strip()
                    
                    elif keyword == "attended":

                        if value:
                        
                            if value.lower().strip() == "yes":
                                attended = True

                    elif keyword == "in-person seats":

                        if value:

                            try:
                                total_seats = int(value)
                                if total_seats > 0:
                                    in_person_event = True
                            except:
                                break

                    elif keyword == "online seats":
                        
                        if value:

                            try:
                                total_seats = int(value)
                                if total_seats > 0:
                                    online_event = True
                            except:
                                break

                    elif keyword == "first name":

                        if value:
                            first_name = value.lower().strip()
                
                    elif keyword == "last name":

                        if value:
                            last_name = value.lower().strip()

                    elif keyword == "full name":

                        if value:
                            first_name, last_name = value.split()
                            first_name = first_name.lower().strip()
                            last_name = last_name.lower().strip()

                    elif keyword == "registrant name":

                        if value:
                            first_name, last_name = value.split()
                            first_name = first_name.lower().strip()
                            last_name = last_name.lower().strip()

                    elif keyword == "affiliated organization":

                        if value:

                            if value.lower().strip() != "other":
                                organization = value.lower().strip()

                    elif keyword == "not-affiliated organization":

                        if value:

                            if not organization:
                                organization = value.lower().strip()

                    elif keyword == "event title":

                        if value:
                            event_title = value.lower().strip()

                    elif keyword == "confirmed registrants":

                        if value:

                            try:
                                total_number_registrants = int(value)
                            except:
                                break

                    elif keyword == "confirmed attendance":

                        if value:

                            try:
                                total_confirmed_registrants = int(value)
                            except:
                                break

                # check row is valid for insertion

                if not attended:
                    continue

                if not first_name:
                    continue

                if not last_name:
                    continue

                if not event_title:
                    continue

                if in_person_event and online_event:
                    event_type = "hybrid"
                
                elif in_person_event:
                    event_type = "in-person"
                
                elif online_event:
                    event_type = "online"

                else:
                    continue

                key = (event_id, first_name, last_name, event_title, start_time, end_time, start_date, end_date)
            
                if key in seen:
                    continue

                seen.add(key)
            
                registrant_name = first_name + " " + last_name

                events_batch.append({
                    "event_id": event_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "registrant_name": registrant_name,
                    "organization": organization,
                    "tag": tag,
                    "event_title": event_title,
                    "event_type": event_type,
                    "total_confirmed_registrants": total_confirmed_registrants,
                    "total_number_registrants": total_number_registrants,
                    "uploaded_file_id": file_id
                })
               
            if events_batch:
                _insert_events_data(db, events_batch)

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