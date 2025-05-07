"""
Error handling module for the Simple Chat Agency.
Provides standardized error handling and reporting functions.
"""
import traceback
import uuid
import time
from functools import wraps
from . import logger

# Get a logger instance
log = logger.get_logger(__name__)

class AppError(Exception):
    """Base exception class for application errors"""
    def __init__(self, message, error_code=None, status_code=500):
        self.message = message
        self.error_id = str(uuid.uuid4())
        self.error_code = error_code
        self.status_code = status_code
        self.timestamp = time.time()
        super().__init__(self.message)

class ValidationError(AppError):
    """Error raised when input validation fails"""
    def __init__(self, message, error_code=None):
        super().__init__(message, error_code, status_code=400)

class ResourceNotFoundError(AppError):
    """Error raised when a requested resource is not found"""
    def __init__(self, message, resource_type, resource_id):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(
            message or f"{resource_type} not found with ID: {resource_id}", 
            error_code="resource_not_found",
            status_code=404
        )

class ExternalServiceError(AppError):
    """Error raised when an external service call fails"""
    def __init__(self, message, service_name, original_error=None):
        self.service_name = service_name
        self.original_error = original_error
        super().__init__(
            f"Error in {service_name} service: {message}",
            error_code=f"{service_name.lower()}_service_error"
        )

def generate_error_id():
    """Generate a unique error ID for tracking"""
    return str(uuid.uuid4())

def format_error_for_user(error, include_details=False):
    """
    Format an error message suitable for end users.
    
    Args:
        error: The exception to format
        include_details: Whether to include technical details
        
    Returns:
        A user-friendly error message string
    """
    if isinstance(error, AppError):
        error_id = error.error_id
        if include_details:
            return f"❌ Error (ID: {error_id}): {error.message}"
        else:
            return f"❌ Sorry, something went wrong (Error ID: {error_id}). Our team has been notified."
    else:
        error_id = generate_error_id()
        if include_details:
            return f"❌ Error (ID: {error_id}): {str(error)}"
        else:
            return f"❌ Sorry, something went wrong (Error ID: {error_id}). Our team has been notified."

def report_error(error_id, error, stack_trace=None, context=None):
    """
    Log an error to the monitoring system.
    
    Args:
        error_id: Unique ID for the error
        error: The exception object
        stack_trace: Optional stack trace as string
        context: Optional dictionary of context information
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    if stack_trace is None and hasattr(error, '__traceback__'):
        stack_trace = ''.join(traceback.format_tb(error.__traceback__))
    
    log.error(
        f"Error ID: {error_id}, Type: {error_type}, Message: {error_message}",
        extra={
            "error_id": error_id,
            "error_type": error_type,
            "stack_trace": stack_trace,
            "context": context or {}
        }
    )

def handle_errors(func):
    """
    Decorator to standardize error handling.
    Catches exceptions, formats user messages, and logs details.
    
    Args:
        func: The function to wrap
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AppError as e:
            # Application errors already have an error_id
            report_error(e.error_id, e)
            return format_error_for_user(e)
        except Exception as e:
            # Generate an error_id for unexpected errors
            error_id = generate_error_id()
            report_error(error_id, e, traceback.format_exc())
            return format_error_for_user(e)
    return wrapper

def async_handle_errors(func):
    """
    Decorator to standardize error handling for async functions.
    
    Args:
        func: The async function to wrap
        
    Returns:
        Wrapped async function with error handling
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppError as e:
            # Application errors already have an error_id
            report_error(e.error_id, e)
            return format_error_for_user(e)
        except Exception as e:
            # Generate an error_id for unexpected errors
            error_id = generate_error_id()
            report_error(error_id, e, traceback.format_exc())
            return format_error_for_user(e)
    return wrapper
