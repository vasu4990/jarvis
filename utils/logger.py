"""
Structured logging setup for JARVIS
"""

import sys
import structlog
from pathlib import Path
from structlog.stdlib import LoggerFactory


def setup_logging(config):
    """Configure structured logging with file and console outputs"""
    
    log_level = config.get("app.log_level", "INFO")
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer() if config.get("logging.console_output", True)
            else structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Set log level
    import logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
