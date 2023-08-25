import os
import logging

def get_logger(logger_name: str) -> logging.Logger:
    if os.path.isfile(logger_name):
        os.remove(logger_name)
    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # create console handler
    sh = logging.StreamHandler()
    # create file handler
    fh = logging.FileHandler(logger_name)
    # create formatter
    # formatter = logging.Formatter(
    #     "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s")
    # add formatter to sh
    sh.setFormatter(formatter)
    # add formatter to fh
    fh.setFormatter(formatter)
    # add sh to logger
    logger.addHandler(sh)
    logger.addHandler(fh)

    return logger