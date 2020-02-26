import logging
import sys
import logging.config


def create_logger(logger_name, log_file=None, terminal_level=logging.INFO, file_level=logging.INFO):
    """
    Create a logger.
    The same logger object will be active all through out the python
    interpreter process.
    https://docs.python.org/2/howto/logging-cookbook.html
    Use   logger = logging.getLogger(logger_name) to obtain logging all
    through out
    """
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
    })
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    tool_formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')

    if type(terminal_level) is str:
        if terminal_level.lower() == "debug":
            res_terminal_level = logging.DEBUG
        elif terminal_level.lower() == "info":
            res_terminal_level = logging.INFO
        elif "warn" in terminal_level.lower():
            res_terminal_level = logging.WARNING
        elif terminal_level.lower() == "error":
            res_terminal_level = logging.ERROR
        elif terminal_level.lower() == "critical":
            res_terminal_level = logging.CRITICAL
        else:
            res_terminal_level = logging.NOTSET
    else:
        res_terminal_level = terminal_level
    logger.setLevel(res_terminal_level)
    # Remove the stdout handler
    logger_handlers = logger.handlers[:]
    for handler in logger_handlers:
        if handler.name == 'std_out':
            logger.removeHandler(handler)
    if log_file is not None:
        file_h = logging.FileHandler(log_file)
        file_h.setLevel(file_level)
        file_h.set_name('file_handler')
        file_h.setFormatter(formatter)
        logger.addHandler(file_h)

    terminal_h = logging.StreamHandler(sys.stdout)
    terminal_h.setLevel(res_terminal_level)
    terminal_h.set_name('stdout')
    terminal_h.setFormatter(tool_formatter)
    logger.addHandler(terminal_h)
    return logger
