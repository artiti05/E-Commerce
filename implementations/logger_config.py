import logging
import os

def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Standard formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler (Outputs to stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # File Handler (Outputs to app.log)
    file_handler = logging.FileHandler(os.path.join(log_dir, "app.log"), encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Get specific layer loggers
    logging.getLogger("app.domain").setLevel(logging.DEBUG)
    logging.getLogger("app.repository").setLevel(logging.DEBUG)
    logging.getLogger("app.service").setLevel(logging.DEBUG)
    logging.getLogger("app.main").setLevel(logging.DEBUG)

    logging.info("Logging configuration complete. Log file at logs/app.log")

setup_logging()
