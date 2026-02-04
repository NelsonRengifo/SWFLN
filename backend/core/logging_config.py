import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():

    root = logging.getLogger()

    if root.handlers:
        return

    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    BASE_DIR = Path(__file__).resolve().parent.parent
    LOG_FILE = BASE_DIR / "logs" / "logs.log"

    # Creates the log folder if it does not exist
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    root.addHandler(stream_handler)
    root.addHandler(file_handler)
