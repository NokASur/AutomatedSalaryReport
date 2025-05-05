from logging.handlers import RotatingFileHandler
import os
import logging

logger = logging.getLogger(__name__)


def generate_handler(filename: str,
                     logging_level: int,
                     logging_formatter='%(asctime)s - %(name)s - %(levelname)s - %(message)s') -> RotatingFileHandler:
    """
    :param filename: example "/name.log".
    :param logging_level: higher int - higher priority, logging.info - 20, .debug - 10, etc.
    :param logging_formatter: presentation format
    :return: working rotating handler of decent size (10 mB)
    """
    handler = RotatingFileHandler(
        filename=os.path.dirname(os.path.abspath(__file__)) + filename,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8',
        mode='a',
    )
    handler.setFormatter(logging.Formatter(logging_formatter))
    handler.setLevel(logging_level)
    return handler


logger.addHandler(generate_handler("/google_drive_checker_all.log", logging.DEBUG))
logger.addHandler(generate_handler("/google_drive_checker_info.log", logging.INFO))
