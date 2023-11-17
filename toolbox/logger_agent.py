import logging

def get_logger(logger_name: str, logger_level: str) -> logging.Logger:
    logger = logging.getLogger(__name__)
    if logger_level == "ERROR":
        logger.setLevel(logging.ERROR)
    elif logger_level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    # create console handler
    sh = logging.StreamHandler()
    # create file handler
    fh = logging.FileHandler(logger_name)
    # create formatter
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