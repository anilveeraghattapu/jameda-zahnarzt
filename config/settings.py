import logging
from logging.handlers import RotatingFileHandler

# Create log directory if it doesn't exist
import os
os.makedirs("log", exist_ok=True)

# Configure root logger (optional, but good practice)
logging.basicConfig(level=logging.INFO)
logging.getLogger().handlers = []

# --- ERROR LOGGER (errors.log) ---
error_handler = RotatingFileHandler(
    'log/errors.log',
    maxBytes=1024 * 1024,  # 1MB per file
    backupCount=3  # Keep 3 backup files
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))

# --- INFO LOGGER (info.log) ---
info_handler = RotatingFileHandler(
    'log/info.log',
    maxBytes=1024 * 1024,  # 1MB per file
    backupCount=3
)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))

# Attach handlers to the root logger
logging.getLogger().addHandler(error_handler)
logging.getLogger().addHandler(info_handler)

# --- TEST LOGGING ---
#logging.info("This goes to info.log")
#logging.error("This goes to errors.log AND info.log (since ERROR > INFO)")