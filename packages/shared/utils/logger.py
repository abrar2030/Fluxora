import logging
import sys
import os
import json
from datetime import datetime

DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def get_logger(name: str, level: int = None, log_format: str = None, log_file: str = None,
               rotate: bool = False, max_bytes: int = 10485760, backup_count: int = 5):
    """
    Configures and returns a logger instance.

    Args:
        name (str): The name of the logger, typically __name__.
        level (int, optional): The logging level. Defaults to DEFAULT_LOG_LEVEL (INFO).
        log_format (str, optional): The log message format. Defaults to DEFAULT_LOG_FORMAT.
        log_file (str, optional): Path to a log file. If provided, logs will be written to this file.
                                  If None, logs will be output to stdout. Defaults to None.
        rotate (bool, optional): Whether to use a rotating file handler. Defaults to False.
        max_bytes (int, optional): Maximum size in bytes for rotating file handler. Defaults to 10MB.
        backup_count (int, optional): Number of backup files to keep for rotating handler. Defaults to 5.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers if logger is already configured
    if logger.hasHandlers():
        logger.handlers.clear()

    log_level = level if level is not None else DEFAULT_LOG_LEVEL
    formatter = logging.Formatter(log_format if log_format is not None else DEFAULT_LOG_FORMAT)

    logger.setLevel(log_level)

    if log_file:
        # Ensure directory for log file exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        if rotate:
            try:
                from logging.handlers import RotatingFileHandler
                handler = RotatingFileHandler(
                    log_file,
                    mode='a',
                    maxBytes=max_bytes,
                    backupCount=backup_count
                )
            except ImportError:
                # Fall back to regular file handler if RotatingFileHandler is not available
                handler = logging.FileHandler(log_file, mode='a')
                logger.warning("RotatingFileHandler not available, using regular FileHandler")
        else:
            handler = logging.FileHandler(log_file, mode='a') # Append mode
    else:
        handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.propagate = False # Avoid passing messages to the root logger if handlers are set

    return logger

def configure_json_logging(name: str, log_file: str = None, level: int = None,
                          include_timestamp: bool = True, include_hostname: bool = False):
    """
    Configures and returns a logger that outputs in JSON format, useful for log aggregation systems.

    Args:
        name (str): The name of the logger, typically __name__.
        log_file (str, optional): Path to a log file. If provided, logs will be written to this file.
                                  If None, logs will be output to stdout. Defaults to None.
        level (int, optional): The logging level. Defaults to DEFAULT_LOG_LEVEL (INFO).
        include_timestamp (bool, optional): Whether to include timestamp in JSON. Defaults to True.
        include_hostname (bool, optional): Whether to include hostname in JSON. Defaults to False.

    Returns:
        logging.Logger: Configured logger instance with JSON formatting.
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers if logger is already configured
    if logger.hasHandlers():
        logger.handlers.clear()

    log_level = level if level is not None else DEFAULT_LOG_LEVEL
    logger.setLevel(log_level)

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                'level': record.levelname,
                'name': record.name,
                'message': record.getMessage(),
            }

            if include_timestamp:
                log_data['timestamp'] = datetime.utcnow().isoformat() + 'Z'

            if include_hostname:
                import socket
                log_data['hostname'] = socket.gethostname()

            if hasattr(record, 'exc_info') and record.exc_info:
                log_data['exception'] = self.formatException(record.exc_info)

            # Add any extra attributes
            for key, value in record.__dict__.items():
                if key not in ['args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
                              'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
                              'msecs', 'message', 'msg', 'name', 'pathname', 'process',
                              'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName']:
                    log_data[key] = value

            return json.dumps(log_data)

    if log_file:
        # Ensure directory for log file exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        handler = logging.FileHandler(log_file, mode='a')
    else:
        handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False

    return logger

def get_metrics_logger(name: str, log_file: str = None):
    """
    Creates a specialized logger for metrics and monitoring data in JSON format.

    Args:
        name (str): The name of the logger, typically __name__ + '.metrics'
        log_file (str, optional): Path to a log file. If None, logs to stdout.

    Returns:
        logging.Logger: Configured metrics logger instance.
    """
    return configure_json_logging(
        name=name,
        log_file=log_file,
        include_timestamp=True,
        include_hostname=True
    )

# Example usage (optional, can be removed or commented out)
if __name__ == "__main__":
    # Example: Log to console
    console_logger = get_logger("my_console_app")
    console_logger.info("This is an info message to the console.")
    console_logger.warning("This is a warning message to the console.")

    # Example: Log to file
    # Ensure you have write permissions to the specified path
    # For example, create a 'logs' directory in the same directory as this script
    if not os.path.exists("logs"):
        os.makedirs("logs")
    file_logger = get_logger("my_file_app", log_file="logs/app.log")
    file_logger.error("This is an error message to the log file.")
    file_logger.debug("This is a debug message (won't show with INFO level by default).")

    # Example: Logger with debug level
    debug_logger = get_logger("my_debug_app", level=logging.DEBUG)
    debug_logger.debug("This is a detailed debug message.")

    # Example: JSON logger
    json_logger = configure_json_logging("json_logger", log_file="logs/json_logs.log")
    json_logger.info("This is a JSON formatted log message")
    json_logger.error("This is an error in JSON format", extra={"context": "example", "user_id": 12345})
