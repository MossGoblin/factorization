from datetime import datetime
import os
from processor import Processor
from toolbox import (
    CONFIG_FILEPATH,
    DATA_FOLDER,
    LOGGER_FILEPATH,
    OUTPUT_FOLDER,
    STASH_FOLDER,
)
from pytoolbox.config_agent import ConfigAgent
import toolbox.logger_agent as logger_agent
from toolbox.data_manager import DataManager

project_title = 'Composites project'

project_path = os.path.dirname(__file__)
HTML_FILENAME = 'main.html'
html_filepath = os.path.join(project_path, HTML_FILENAME)
config_filepath = CONFIG_FILEPATH
config = ConfigAgent(config_path=config_filepath)
logger_level = config.logger.level
logger_filepath = LOGGER_FILEPATH
logger = logger_agent.get_logger(logger_filepath, logger_level)
data_folder = DATA_FOLDER
stash_folder = STASH_FOLDER
output_folder = OUTPUT_FOLDER
data_filepath = os.path.join(data_folder, config.files.data_file_name)
data_manager = DataManager(data_filepath)

def main():
    start = datetime.utcnow()
    config.add_parameter('local', 'start', start)
    config.add_parameter('local', 'project_title', project_title)
    config.add_parameter('local', 'data_folder', data_folder)
    config.add_parameter('local', 'logger_filepath', logger_filepath)
    config.add_parameter('local', 'stash_folder', stash_folder)
    config.add_parameter('local', 'output_folder', output_folder)
    config.add_parameter('local', 'html_filepath', html_filepath)
    config.add_parameter('local', 'data_filepath', data_filepath)

    pr = Processor(logger=logger, config=config, data_manager=data_manager)
    pr.run()


if __name__ == "__main__":
    main()
