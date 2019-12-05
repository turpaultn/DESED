import logging
import sys


def create_logger(logger_name, log_file, terminal_level=logging.DEBUG, file_level=logging.INFO):
    '''
    Create a logger.
    The same logger object will be active all through out the python
    interpreter process.
    https://docs.python.org/2/howto/logging-cookbook.html
    Use   logger = logging.getLogger(logger_name) to obtain logging all
    through out
    '''
    logger = logging.getLogger(logger_name)
    # Remove the stdout handler
    logger_handlers = logger.handlers[:]
    for handler in logger_handlers:
        if handler.name == 'std_out':
            logger.removeHandler(handler)
    logger.setLevel(terminal_level)
    file_h = logging.FileHandler(log_file)
    file_h.setLevel(file_level)
    file_h.set_name('file_handler')
    terminal_h = logging.StreamHandler(sys.stdout)
    terminal_h.setLevel(terminal_level)
    terminal_h.set_name('stdout')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    tool_formatter = logging.Formatter(' %(levelname)s - %(message)s')
    file_h.setFormatter(formatter)
    terminal_h.setFormatter(tool_formatter)
    logger.addHandler(file_h)
    logger.addHandler(terminal_h)
    return logger


LOG = create_logger("DESED", "Desed.log", terminal_level=logging.INFO, file_level=logging.INFO)
