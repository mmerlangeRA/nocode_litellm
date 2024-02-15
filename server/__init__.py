"""Server."""
import logging
import os
from logging.handlers import RotatingFileHandler
date_format = "%Y-%m-%d %H:%M:%S"

log_directory="logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_file_path = os.path.join(log_directory, "logfile.log") 

env_mode = os.getenv("LLMPROFILE", "local")

PRETTY_LOG_FORMAT = (
    "%(asctime)s.%(msecs)03d [%(levelname)-8s] %(name)+25s - %(message)s"
)


# Configure logging based on the mode
if env_mode == "local":
    # In production mode, log to a file
    logging.basicConfig(
        level=logging.INFO,
        format=PRETTY_LOG_FORMAT,
        datefmt=date_format,
        handlers=[RotatingFileHandler(log_file_path, maxBytes=10000000, backupCount=5)]
    )
else:
    # In development mode, log to stdout
    logging.basicConfig(
        level=logging.DEBUG,
        format=PRETTY_LOG_FORMAT,
        datefmt=date_format,
        handlers=[logging.StreamHandler(),RotatingFileHandler(log_file_path, maxBytes=10000000, backupCount=5)]
    )

logging.captureWarnings(True)