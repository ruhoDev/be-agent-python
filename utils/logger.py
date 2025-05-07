"""
Structured logging module for the Simple Chat Agency.
Provides standardized logging configuration and helper functions.
"""
import logging
import uuid
import traceback
import json
import sys
from contextvars import ContextVar
from datetime import datetime

# Create context variable for request ID
request_id_var = ContextVar('request_id', default=None)

class RequestIdFilter(logging.Filter):
    """Filter that adds request_id to log records"""
    def filter(self, record):
        record.request_id = request_id_var.get() or 'no-request-id'
        return True

class JSONFormatter(logging.Formatter):
    """Formatter that outputs JSON strings after gathering all the log record info"""
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'request_id': getattr(record, 'request_id', 'no-request-id'),
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        # Add extra fields provided in the log record
        for key, value in record.__dict__.items():
            if key not in ['args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
                          'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
                          'msecs', 'message', 'msg', 'name', 'pathname', 'process',
                          'processName', 'relativeCreated', 'request_id', 'stack_info',
                          'thread', 'threadName']:
                log_data[key] = value
                
        return json.dumps(log_data)

def get_logger(name):
    """
    Get a logger instance with consistent configuration.
    
    Args:
        name: The logger name, typically __name__ from the calling module
        
    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if handlers haven't been added yet
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        logger.addHandler(console_handler)
        
        # Add request ID filter
        logger.addFilter(RequestIdFilter())
        
        # Don't propagate to root logger
        logger.propagate = False
    
    return logger

def set_request_context():
    """Set a unique request ID for the current async context"""
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id

def get_request_id():
    """Get the current request ID"""
    return request_id_var.get()

def log_exceptions(logger):
    """
    Decorator to log exceptions from functions
    
    Args:
        logger: Logger instance to use
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Exception in {func.__name__}: {str(e)}",
                    exc_info=True,
                    extra={"function": func.__name__}
                )
                raise
        return wrapper
    return decorator
