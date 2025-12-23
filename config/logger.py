import logging
import os

def get_logger(log_file='app.log', level=logging.INFO, log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
    logger = logging.getLogger('server_tools')

    if not logger.handlers:
        logger.setLevel(level)

        # Ensure the directory for the log file exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        formatter = logging.Formatter(log_format)
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger