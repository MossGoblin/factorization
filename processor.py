from datetime import datetime
import os
import pyprimes as pp
import numpy as np
from toolbox import STASH_FOLDER
from toolbox.generator import decompose
import shutil


class Processor():
    def __init__(self, logger, config, data_manager) -> None:
        self.cfg = config
        self.logger = logger
        self.data_manager = data_manager

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
        if self.cfg.mode.mode == 'generate':
            self.logger.info('GENERATE')
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
        else:
            self.logger.info('PLOT')
            self.logger.info(f'graph size: {self.cfg.graph.width}/{self.cfg.graph.height} x {self.cfg.graph.point_size}pt')
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

    def generate_number_list(self):
        self.logger.info('Generating numbers')
        if self.cfg.set.mode == 'family':
            self.logger.debug('Processing families')
            number_list = self.generate_number_families()
        elif self.cfg.set.mode == 'range':
            self.logger.debug('Processing range')
            number_list = self.generate_continuous_number_list()
        return number_list

    def generate_continuous_number_list(self):
        lowerbound = self.cfg.set.range_min
        upperbound = self.cfg.set.range_max
        if lowerbound < 2:
            lowerbound = 2
        number_list = []
        for value in range(lowerbound, upperbound + 1):
            if pp.isprime(value) and not self.cfg.set.include_primes:
                continue
            number_list.append(int(value))
        return number_list

    def generate_number_families(self):
        processed_numbers = []
        for family in self.cfg.set.families:
            # order family
            family = sorted(family)
            family_product = np.prod(family)
            if self.cfg.set.identity_factor_mode == 'count':
                if self.cfg.set.identity_factor_minimum_mode == 'family':
                    largest_family_factor = family[-1]
                    larger_primes = pp.primes_above(largest_family_factor)
                    first_identity_factor = next(larger_primes)
                elif self.cfg.set.identity_factor_minimum_mode == 'origin':
                    first_identity_factor = 2
                else:
                    first_identity_factor = self.cfg.set.identity_factor_minimum_value
                number_of_composites = self.cfg.set.identity_factor_count
            else:
                first_identity_factor = self.cfg.set.identity_factor_range_min
                number_of_composites = pp.prime_count(self.cfg.set.identity_factor_range_max) - pp.prime_count(self.cfg.set.identity_factor_range_min)
            # iterate identity factors
            processed_numbers.append(int(family_product * first_identity_factor))
            prime_generator = pp.primes_above(first_identity_factor)
            for count in range(number_of_composites):
                processed_numbers.append(int(family_product * next(prime_generator)))

        return processed_numbers

    def stash_log_file(self, log_filename_prefix: str):
        # ensure stash folder exists
        start = self.cfg.local.start
        stash_folder = self.cfg.local.stash_folder
        logger_filepath = self.cfg.local.logger_filepath
        if not os.path.exists(STASH_FOLDER):
            os.makedirs(STASH_FOLDER)
        # copy the latest log file in the stash folder
        start_string = start.strftime("%d%m%Y_%H%M%S")
        stashed_log_filename = "_".join([log_filename_prefix, start_string]) + ".log"
        stashed_log_filepath = os.path.join(stash_folder, stashed_log_filename)
        shutil.copy(logger_filepath, stashed_log_filepath)

        # reset main log file
        open(logger_filepath, 'w').close()


    # def get_primes_between(self, previous: int, total_count: int):
    #     primes = []
    #     prime_generator = pp.primes_above(previous)
    #     for count in range(total_count):
    #         primes.append(next(prime_generator))
    #     return primes

    def run(self):
        self.logger.info(f'Start at {self.cfg.local.start}')
        self.log_settings()
        mode = self.cfg.mode.mode
        if mode == 'generate':
            number_list = self.generate_number_list()
            # HERE
            # create dataframe
            collection_df = decompose(self.logger, number_list)
            
            self.data_manager.save_data(collection_df)

        end = datetime.utcnow()
        self.logger.info(f'End at {end}')
        self.logger.info(f'Total time: {end-self.cfg.local.start}')

        logger_filename_prefix = 'GEN'
        # HERE
        self.stash_log_file(logger_filename_prefix)
