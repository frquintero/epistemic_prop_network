"""Logging configuration for the Epistemological Propagation Network."""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

from .config import get_config


def setup_logging(
    level: Optional[str] = None,
    enable_structured: Optional[bool] = None,
    log_file: Optional[str] = None,
) -> None:
    """Setup logging configuration for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_structured: Whether to enable structured logging
        log_file: Optional log file path
    """
    # Get configuration
    try:
        config = get_config()
        level = level or config.log_level
        enable_structured = (
            enable_structured
            if enable_structured is not None
            else config.enable_structured_logging
        )
    except RuntimeError:
        # Configuration not initialized, use defaults
        level = level or "INFO"
        enable_structured = enable_structured if enable_structured is not None else True

    # If structured logging is disabled, suppress all logging output
    if not enable_structured:
        numeric_level = (
            logging.CRITICAL + 1
        )  # Higher than CRITICAL to suppress all output
    else:
        # Convert string level to logging level
        numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Setup handlers
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    handlers.append(console_handler)

    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(numeric_level)
        handlers.append(file_handler)

    # Configure structlog if available and enabled
    if STRUCTLOG_AVAILABLE and enable_structured:
        _setup_structlog(handlers, numeric_level)
    else:
        _setup_standard_logging(handlers, numeric_level)


def _setup_structlog(handlers: list, level: int) -> None:
    """Setup structured logging with structlog."""
    import structlog

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging to work with structlog
    for handler in handlers:
        handler.setFormatter(logging.Formatter("%(message)s"))

    # Get the root logger and configure it
    logger = logging.getLogger()
    logger.setLevel(level)
    for handler in handlers:
        logger.addHandler(handler)


def _setup_standard_logging(handlers: list, level: int) -> None:
    """Setup standard Python logging."""

    # Create custom formatter to match the desired style
    class CustomFormatter(logging.Formatter):
        def format(self, record):
            # Convert level name to lowercase and format like the template
            level = record.levelname.lower()
            record.levelname = f"{level:>8}"
            return super().format(record)

    formatter = CustomFormatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Apply formatter to all handlers
    for handler in handlers:
        handler.setFormatter(formatter)

    # Get the root logger and configure it
    logger = logging.getLogger()
    logger.setLevel(level)
    for handler in handlers:
        logger.addHandler(handler)


def get_logger(name: str) -> Any:
    """Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance (structlog or standard logging)
    """
    config = None
    try:
        config = get_config()
    except RuntimeError:
        pass

    if STRUCTLOG_AVAILABLE and config and config.enable_structured_logging:
        import structlog

        return structlog.get_logger(name)
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to classes."""

    @property
    def logger(self) -> Any:
        """Get logger for this class."""
        return get_logger(self.__class__.__module__ + "." + self.__class__.__name__)


def log_function_call(
    func_name: str, args: Optional[Dict[str, Any]] = None, **kwargs
) -> None:
    """Log a function call with parameters.

    Args:
        func_name: Name of the function being called
        args: Function arguments
        **kwargs: Additional logging context
    """
    logger = get_logger(__name__)
    log_data = {"function": func_name, "args": args or {}, **kwargs}

    if STRUCTLOG_AVAILABLE and get_config().enable_structured_logging:
        logger.info("Function call", **log_data)
    else:
        logger.info(f"Function call: {func_name}", extra=log_data)


def log_performance(func_name: str, duration: float, **kwargs) -> None:
    """Log performance metrics for a function.

    Args:
        func_name: Name of the function
        duration: Execution duration in seconds
        **kwargs: Additional metrics
    """
    logger = get_logger(__name__)
    log_data = {"function": func_name, "duration_seconds": duration, **kwargs}

    if STRUCTLOG_AVAILABLE and get_config().enable_structured_logging:
        logger.info("Performance metric", **log_data)
    else:
        logger.info(f"Performance: {func_name} took {duration:.3f}s", extra=log_data)


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log an error with context.

    Args:
        error: The exception that occurred
        context: Additional context information
    """
    from .exceptions import format_error_details

    logger = get_logger(__name__)
    error_details = format_error_details(error)
    log_data = {**error_details, **(context or {})}

    if STRUCTLOG_AVAILABLE and get_config().enable_structured_logging:
        logger.error("Error occurred", **log_data)
    else:
        logger.error(f"Error: {error_details['message']}", extra=log_data)
