"""Logging configuration for the backend system.

This module provides centralized logging configuration for the entire backend system,
ensuring consistent log formatting and handling across all components.
"""

import logging
import sys
from typing import Optional


def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Set up and configure a logger instance.

    Args:
        name: Optional name for the logger. If None, returns the root logger.

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only add handlers if they haven't been added already
    if not logger.handlers:
        # Configure console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)

    return logger
