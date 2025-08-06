# app/utils/logger.py
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
    # Create logs directories
    # Individual service logs go to /app/logs (mounted to ../logs/)
    individual_logs_dir = Path("/app/logs")
    # Global logs go to /app/global_logs (mounted to ../global_logs/)
    global_logs_dir = Path("/app/global_logs")
    
    individual_logs_dir.mkdir(exist_ok=True)
    global_logs_dir.mkdir(exist_ok=True)
    
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
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_obj)
    console_handler.setFormatter(json_formatter)
    
    # Individual service log file handler
    # This will be mounted to ../logs/{service_name}.log on host
    service_log_file = individual_logs_dir / f"{service_name}.log"
    individual_file_handler = logging.handlers.RotatingFileHandler(
        service_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    individual_file_handler.setLevel(log_level_obj)
    individual_file_handler.setFormatter(json_formatter)
    
    # Global log file handler - all services write to this
    # This will be mounted to ../global_logs/all_services.log on host
    global_log_file = global_logs_dir / "all_services.log"
    global_handler = logging.handlers.RotatingFileHandler(
        global_log_file,
        maxBytes=50*1024*1024,  # 50MB
        backupCount=10
    )
    global_handler.setLevel(log_level_obj)
    global_handler.setFormatter(json_formatter)
    
    # Service-specific log in global directory
    # This will be mounted to ../global_logs/{service_name}.log on host
    service_global_log_file = global_logs_dir / f"{service_name}.log"
    service_global_handler = logging.handlers.RotatingFileHandler(
        service_global_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    service_global_handler.setLevel(log_level_obj)
    service_global_handler.setFormatter(json_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level_obj)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add handlers
    root_logger.addHandler(console_handler)                # Console output
    root_logger.addHandler(individual_file_handler)        # Individual service log
    root_logger.addHandler(global_handler)                 # Global combined log
    root_logger.addHandler(service_global_handler)         # Service log in global directory
    
    # Create logger with service context
    logger = structlog.get_logger(service=service_name)
    
    # Log the logger initialization
    logger.info("logging_initialized", 
               service=service_name, 
               log_level=log_level,
               individual_log_file=str(service_log_file),
               global_log_file=str(global_log_file),
               service_global_log_file=str(service_global_log_file))
    
    return logger

def get_logger(name: str = None):
    """
    Get a logger instance with optional name context
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()