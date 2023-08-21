import os
import logging

def get_logger(logger_name: str) -> logging.Logger:
    if os.path.isfile('run.log'):
        os.remove('run.log')
    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # create console handler
    sh = logging.StreamHandler()
    # create file handler
    fh = logging.FileHandler('run.log')
    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to sh
    sh.setFormatter(formatter)
    # add formatter to fh
    fh.setFormatter(formatter)
    # add sh to logger
    logger.addHandler(sh)
    logger.addHandler(fh)

    return logger