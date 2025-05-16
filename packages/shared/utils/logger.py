import logging
import sys
import os

DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def get_logger(name: str, level: int = None, log_format: str = None, log_file: str = None):
    """
    Configures and returns a logger instance.

    Args:
        name (str): The name of the logger, typically __name__.
        level (int, optional): The logging level. Defaults to DEFAULT_LOG_LEVEL (INFO).
        log_format (str, optional): The log message format. Defaults to DEFAULT_LOG_FORMAT.
        log_file (str, optional): Path to a log file. If provided, logs will be written to this file.
                                  If None, logs will be output to stdout. Defaults to None.

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
        handler = logging.FileHandler(log_file, mode='a') # Append mode
    else:
        handler = logging.StreamHandler(sys.stdout)
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    logger.propagate = False # Avoid passing messages to the root logger if handlers are set

    return logger

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
    pass

