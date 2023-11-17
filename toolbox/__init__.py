import os


parent_dir = os.path.dirname(__file__)
project_path = os.path.abspath(os.path.join(parent_dir, os.pardir))

DATA_FOLDER = os.path.join(project_path, 'data')
STASH_FOLDER = os.path.join(project_path, 'stash')
OUTPUT_FOLDER = os.path.join(project_path, 'output')

LOGGER_FILENAME = 'generate.log'
LOGGER_FILEPATH = os.path.join(project_path, LOGGER_FILENAME)
CONFIG_FILENAME = "config.toml"
CONFIG_FILEPATH = os.path.join(project_path, CONFIG_FILENAME)