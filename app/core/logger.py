import logging
import sys

# Define log format
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

# Create logger
logger = logging.getLogger("fastapi-logger")
logger.setLevel(logging.INFO)

# Prevent adding duplicate handlers
if not logger.handlers:
    # Console handler to print logs in the terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    
    # Add handler to logger
    logger.addHandler(console_handler)

logger.propagate = True