import logging
from typing import Optional

from .app import AppConfig


def setup_logging(app_config: AppConfig) -> logging.Logger:
    """
    Configure root logger with level/format, optionally file output.
    """
    logger = logging.getLogger()
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(app_config.log_level)
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s %(message)s"
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    if app_config.log_path:
        file_handler = logging.FileHandler(app_config.log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def with_context(logger: logging.Logger, **context):
    """
    Attach contextual fields (e.g., session_id) to log records.
    """
    return logging.LoggerAdapter(logger, extra=context)
