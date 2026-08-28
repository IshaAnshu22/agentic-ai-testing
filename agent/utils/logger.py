import json
import logging
import os
import yaml
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_info"):
            log_record["extra_info"] = record.extra_info
            
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logger(name):
    # Read config for log level and dir
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            log_level_str = config.get("logging", {}).get("log_level", "INFO")
            log_dir = config.get("logging", {}).get("log_dir", "logs")
            log_file = config.get("logging", {}).get("log_file", "trace.log")
    except Exception:
        log_level_str = "INFO"
        log_dir = "logs"
        log_file = "trace.log"

    # Make absolute path to log dir based on config_path
    log_dir_path = os.path.join(os.path.dirname(config_path), log_dir)

    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    os.makedirs(log_dir_path, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Prevent duplicate handlers
    if not logger.handlers:
        file_handler = logging.FileHandler(os.path.join(log_dir_path, log_file))
        file_handler.setFormatter(JSONFormatter())
        
        console_handler = logging.StreamHandler()
        # For console, standard formatter is easier to read, but we'll use JSON for the file
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger
