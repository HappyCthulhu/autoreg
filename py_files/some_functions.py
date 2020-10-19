import sys
from loguru import logger


def set_logger():
    logger.remove()

    # настраиваем логгирование
    def debug_only(record):
        return record["level"].name == "DEBUG"

    def critical_only(record):
        return record["level"].name == "CRITICAL"

    def info_only(record):
        return record["level"].name == "INFO"

    logger_format_debug = "<green>{time:DD-MM-YY HH:mm:ss}</> | <bold><blue>{level}</></> | " \
                          "<cyan>{file}:{function}:{line}</> | <blue>{message}</> | <blue>🛠</>"
    logger_format_info = "<green>{time:DD-MM-YY HH:mm:ss}</> | <bold><fg 255,255,255>{level}</></> | " \
                         "<cyan>{file}:{function}:{line}</> | <fg 255,255,255>{message}</> | <fg 255,255,255>✔</>"
    logger_format_critical = "<green>{time:DD-MM-YY HH:mm:ss}</> | <RED><fg 255,255,255>{level}</></> | " \
                             "<cyan>{file}:{function}:{line}</> | <fg 255,255,255><RED>{message}</></> | <RED><fg 255,255,255>❌</></>"

    logger.add(sys.stderr, format=logger_format_debug, level='DEBUG', filter=debug_only)
    logger.add(sys.stderr, format=logger_format_info, level='INFO', filter=info_only)
    logger.add(sys.stderr, format=logger_format_critical, level='CRITICAL', filter=critical_only)
