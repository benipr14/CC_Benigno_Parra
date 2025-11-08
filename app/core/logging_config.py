import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(log_dir: str = "logs", log_file: str = "app.log", max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
    """Setup console logging and a size-rotating file handler.

    By default rotates when the file reaches ~10MB and keeps 5 backups.
    """
    # ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # formatter
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    # console handler (stdout)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # size-based rotating file handler (rotate when file reaches max_bytes, keep backup_count files)
    fh = RotatingFileHandler(
        filename=os.path.join(log_dir, log_file), maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)
    logger.addHandler(fh)
