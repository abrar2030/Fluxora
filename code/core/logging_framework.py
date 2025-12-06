import json
import logging
import sys
import traceback
import uuid
from contextvars import ContextVar
from typing import Optional

request_id_var = ContextVar("request_id", default=None)
user_id_var = ContextVar("user_id", default=None)
correlation_id_var = ContextVar("correlation_id", default=None)


class JsonFormatter(logging.Formatter):
    """
    JSON formatter for structured logging
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as JSON
        """
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "path": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }
        for key, value in record.__dict__.items():
            if key.startswith("_") or key in (
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            ):
                continue
            log_data[key] = value
        return json.dumps(log_data)


def setup_logging(service_name: str, log_level: int = logging.INFO) -> Any:
    """
    Set up logging for the service
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    formatter = JsonFormatter()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


def set_request_context(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Any:
    """
    Set request context for logging
    """
    if request_id:
        request_id_var.set(request_id)
    else:
        request_id_var.set(str(uuid.uuid4()))
    if user_id:
        user_id_var.set(user_id)
    if correlation_id:
        correlation_id_var.set(correlation_id)
    else:
        correlation_id_var.set(request_id_var.get())


def get_request_id() -> Optional[str]:
    """
    Get the current request ID
    """
    return request_id_var.get()


def get_correlation_id() -> Optional[str]:
    """
    Get the current correlation ID
    """
    return correlation_id_var.get()


def clear_request_context() -> Any:
    """
    Clear request context
    """
    request_id_var.set(None)
    user_id_var.set(None)
    correlation_id_var.set(None)
