from datetime import datetime
import logging
import toolbox.logger_agent as logger_agent
import os
from utils import ToolBox
from pytoolbox.config_agent import ConfigAgent


class Processor():

    def __init__(self, logger, config) -> None:
        self.cfg = config
        self.logger = logger

    def set_up_logger(self):
        # create logger
        logger = logging.getLogger(__name__)
        log_level = self.cfg.logger.level
        logger.setLevel(log_level)
        # create formatter and set level
        formatter = logging.Formatter(self.cfg.logger.format)

        reset_log_folder = self.cfg.logger.reset_files
        log_folder = self.cfg.logger.base_folder
        self.prep_folder(log_folder, reset_log_folder)

        logger_mode = self.cfg.logger.mode
        if logger_mode == 'console' or logger_mode == 'full':
            # create console handler
            handler = logging.StreamHandler()
            # add formatter to handler
            handler.setFormatter(formatter)
            # add handler to logger
            logger.addHandler(handler)

        if logger_mode == 'file' or logger_mode == 'full':
            # create file handler
            log_file_name = self.cfg.logger.file_name_string
            if not log_folder == 'none':
                log_file_name = log_folder + "/" + log_file_name
            handler = logging.FileHandler(
                log_file_name, mode='w', encoding='utf-8')
            # add formatter to handler
            handler.setFormatter(formatter)
            # add handler to logger
            logger.addHandler(handler)

        return logger

    def prep_folder(self, folder_name: str, reset_folder: bool):
        '''
        Prepare folder for output csv files
        '''

        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
            return
        else:
            if reset_folder:
                for root, directories, files in os.walk(folder_name):
                    for file in files:
                        file_path = root + '/' + file
                        os.remove(file_path)
            return

    def log_settings(self):
        '''
        Log settings pertinent to the current run
        '''
        self.logger.info('== SETTINGS ==')
        self.logger.info('NUMBER SET')
        self.logger.info(f'number generation mode: {self.cfg.set.mode}')
        if self.cfg.set.mode == 'family':
            self.logger.debug(f'families: {self.cfg.set.families}')
            self.logger.debug(
                f'identity factor mode: {self.cfg.set.identity_factor_mode}')
            if self.cfg.set.identity_factor_mode == 'range':
                self.logger.debug(
                    f'identity factor range: {self.cfg.set.identity_factor_range_min}..{self.cfg.set.identity_factor_range_max}')
            else:
                if self.cfg.set.identity_factor_minimum_mode == 'value':
                    ifm = f'value ({self.cfg.set.identity_factor_minimum_value})'
                else:
                    ifm = self.cfg.set.identity_factor_minimum_mode

                self.logger.debug(f'identity factor minimum: {ifm}')

        elif self.cfg.set.mode == 'range':
            self.logger.debug(
                f'range [{self.cfg.set.range_min}..{self.cfg.set.range_max}]')
            self.logger.debug(
                f'primes: {"included" if self.cfg.set.include_primes else "excluded"}]')

        self.logger.info('GRAPH')
        self.logger.info(
            f'graph size: {self.cfg.graph.width}/{self.cfg.graph.height} x {self.cfg.graph.point_size}pt')
        self.logger.info(f'Y-axis: {self.cfg.graph.mode}')
        self.logger.debug(f'Colorization: {self.cfg.graph.use_color_buckets}')

        self.logger.info('RUN')
        self.logger.info(f'csv output: {self.cfg.run.create_csv}')
        if self.cfg.run.hard_copy_timestamp_granularity == 0:
            timestamp_format = 'days'
        elif self.cfg.run.hard_copy_timestamp_granularity == 1:
            timestamp_format = 'hours'
        elif self.cfg.run.hard_copy_timestamp_granularity == 2:
            timestamp_format = 'minutes'
        else:
            timestamp_format = 'full'
        self.logger.debug(f'timestamp granularity: {timestamp_format}')
        self.logger.debug(
            f'output folder reset: {self.cfg.run.reset_output_data}')

        self.logger.info('==============')

    def run(self):
        start = datetime.utcnow()
        self.logger.info(f'Start at {start}')
        self.log_settings()
        # HERE
        tb = ToolBox(self.logger, self.cfg)
        number_list = tb.generate_number_list()
        end = datetime.utcnow()
        self.logger.info(f'End at {end}')
        self.logger.info(f'Total time: {end-start}')
