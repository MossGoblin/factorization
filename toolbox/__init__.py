import os


parent_dir = os.path.dirname(__file__)
project_path = os.path.abspath(os.path.join(parent_dir, os.pardir))

DATA_FOLDER = os.path.join(project_path, 'data')
STASH_FOLDER = os.path.join(project_path, 'stash')
OUTPUT_FOLDER = os.path.join(project_path, 'output')

LOGGER_FILENAME = 'generate.log'
logger_filepath = os.path.join(project_path, LOGGER_FILENAME)
CONFIG_FILENAME = "config.toml"
config_filepath = os.path.join(project_path, CONFIG_FILENAME)


def get_data_folder():
    return DATA_FOLDER

def get_logger_filepath():
    return logger_filepath

def get_config_filepath():
    return config_filepath

def get_stash_folder():
    return STASH_FOLDER

def get_output_folder():
    return OUTPUT_FOLDER