import logging
import sys
from app.config.settings import get_settings

settings = get_settings()


def setup_logger(name: str) -> logging.Logger:
    """Configure logger with appropriate format and level."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level))
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


logger = setup_logger(__name__)
