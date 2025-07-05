import logging
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
DEBUG = os.getenv("DEBUG")

def setup_logging():
    logger = logging.getLogger("TelegramTextApp")
    
    logger.handlers.clear()
    
    log_level = logging.DEBUG if DEBUG else logging.INFO
    logger.setLevel(log_level)
    
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    
    if DEBUG == "False":
        LOG_FILE = os.path.join("bot.log")
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()