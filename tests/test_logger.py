import inspect
import logging

from desed.logger import create_logger


def test_logger_info():
    logger = create_logger(__name__ + "/" + inspect.currentframe().f_code.co_name)
    logger.info("bonjour")
    logger.debug("not shown")
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name, "info"
    )


def test_logger_debug():
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name, "debug"
    )


def test_logger_warning():
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name, "WARN"
    )
    logger.info("not shown")


def test_logger_error():
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name, "error"
    )
    logger.warn("not shown")


def test_logger_critical():
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name, "CRITICAL"
    )
    logger.error("not shown")


def test_logger_not_set():
    logger = create_logger(
        __name__ + "/" + inspect.currentframe().f_code.co_name, "Nothing"
    )
