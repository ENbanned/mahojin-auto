import os
import sys
from loguru import logger


def setup_logging(log_dir="files", log_filename="app.log"):
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, log_filename)
    
    logger.remove()
    
    logger.add(
        log_file,
        rotation="10 MB", 
        retention="1 week",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    )
    
    logger.add(
        sys.stderr,
        level="ERROR",
        format="{level} | {message}"
    )
    
    return logger