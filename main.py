import os
from processor import Processor
from toolbox import (
    get_config_filepath,
    get_data_folder,
    get_logger_filepath,
    get_output_folder,
    get_stash_folder,
)
from pytoolbox.config_agent import ConfigAgent
import toolbox.logger_agent as logger_agent


project_title = 'Composites project'

project_path = os.path.dirname(__file__)
HTML_FILENAME = 'main.html'
html_filepath = os.path.join(project_path, HTML_FILENAME)
config_filepath = get_config_filepath()
config = ConfigAgent(config_path=config_filepath)
logger_level = config.logger.level
logger_filepath = get_logger_filepath()
logger = logger_agent.get_logger(logger_filepath, logger_level)
data_folder = get_data_folder()
stash_folder = get_stash_folder()
output_folder = get_output_folder()
data_filepath = os.path.join(data_folder, config.files.data_file_name)

def main():
    pr = Processor(logger=logger, config=config)
    pr.run()


if __name__ == "__main__":
    main()
