import structlog
import logging
import logging.handlers
import sys
import os
from datetime import datetime
from pathlib import Path


def setup_logging(service_name: str, log_level: str = "INFO"):
    """
    Setup structured logging for the microservice with both individual and global logging
    """
    # Create logs directories with fallback for testing
    # Individual service logs go to /app/logs (mounted to ../logs/)
    individual_logs_dir = Path("/app/logs")
    # Global logs go to /app/global_logs (mounted to ../global_logs/)
    global_logs_dir = Path("/app/global_logs")
    
    # For testing environment, create alternative paths
    if not individual_logs_dir.parent.exists():
        # We're likely in a test environment, use current directory
        individual_logs_dir = Path("./logs")
        global_logs_dir = Path("./global_logs")
    
    # Create directories if they don't exist
    try:
        individual_logs_dir.mkdir(parents=True, exist_ok=True)
        global_logs_dir.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        # If we can't create directories, fall back to current directory
        print(f"Warning: Could not create log directories: {e}")
        individual_logs_dir = Path(".")
        global_logs_dir = Path(".")

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure Python logging
    log_level_obj = getattr(logging, log_level.upper())

    # Create formatters
    json_formatter = logging.Formatter('%(message)s')

    # Console handler (stdout) - always works
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_obj)
    console_handler.setFormatter(json_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level_obj)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Always add console handler
    root_logger.addHandler(console_handler)

    # Try to add file handlers if directories are writable
    try:
        # Individual service log file handler
        service_log_file = individual_logs_dir / f"{service_name}.log"
        individual_file_handler = logging.handlers.RotatingFileHandler(
            service_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        individual_file_handler.setLevel(log_level_obj)
        individual_file_handler.setFormatter(json_formatter)
        root_logger.addHandler(individual_file_handler)

        # Global log file handler - all services write to this
        global_log_file = global_logs_dir / "all_services.log"
        global_handler = logging.handlers.RotatingFileHandler(
            global_log_file,
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10
        )
        global_handler.setLevel(log_level_obj)
        global_handler.setFormatter(json_formatter)
        root_logger.addHandler(global_handler)

        # Service-specific log in global directory
        service_global_log_file = global_logs_dir / f"{service_name}.log"
        service_global_handler = logging.handlers.RotatingFileHandler(
            service_global_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        service_global_handler.setLevel(log_level_obj)
        service_global_handler.setFormatter(json_formatter)
        root_logger.addHandler(service_global_handler)

    except (PermissionError, OSError) as e:
        # If file logging fails, just use console logging
        print(f"Warning: File logging disabled due to: {e}")
        service_log_file = None
        global_log_file = None
        service_global_log_file = None

    # Create logger with service context
    logger = structlog.get_logger(service=service_name)

    # Log the logger initialization
    try:
        logger.info("logging_initialized",
                    service=service_name,
                    log_level=log_level,
                    individual_log_file=str(service_log_file) if service_log_file else "console_only",
                    global_log_file=str(global_log_file) if global_log_file else "console_only",
                    service_global_log_file=str(service_global_log_file) if service_global_log_file else "console_only")
    except Exception as e:
        # Fallback logging if structlog fails
        print(f"Logger initialized for {service_name} (console only due to: {e})")

    return logger


def get_logger(name: str = None):
    """
    Get a logger instance with optional name context
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()