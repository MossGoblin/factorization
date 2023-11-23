import os
import shutil
from datetime import datetime
from logging import Logger

import numpy as np
import math
import pandas as pd
import pyprimes as pp
from progress.bar import Bar
from pytoolbox.config_agent import ConfigAgent
from pytoolbox.bokeh_agent import BokehScatterAgent

import toolbox.mappings as mappings
from toolbox import STASH_FOLDER
from toolbox.data_manager import DataManager
from toolbox.generator import decompose

import collections
from bokeh.palettes import (
    Category10,
    Cividis,
    Dark2,
    Inferno,
    Magma,
    Plasma,
    Turbo,
    Viridis,
)


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
                    f'[primes: {"included" if self.cfg.set.include_primes else "excluded"}]')
        else:
            self.logger.info('PLOT')
            self.logger.info(f'graph size: {self.cfg.plot.width}/{self.cfg.plot.height} x {self.cfg.plot.point_size}pt')
            self.logger.info(f'Y-axis: {self.cfg.plot.mode}')
            self.logger.debug(f'Colorization: {self.cfg.plot.use_color_buckets}')

        self.logger.info('==============')

    def get_graph_params(self, config: ConfigAgent, logger: Logger, project_title: str, html_filepath: str) -> dict:
        plot_width = config.plot.width
        plot_height = config.plot.height
        palette = config.plot.palette
        point_size = config.plot.point_size
        colorization_field_config = config.plot.colorization_value
        colorization_field = mappings.colorization_field[colorization_field_config]
        y_axis = config.plot.mode

        graph_params = {}
        # TODO check for filters
        # filter_text = ""
        # if config.filters.filter_data:
        #     filter_text = f" [ filter: {config.local.filter_name} ]"
        graph_params['title'] = f'Composites: {mappings.y_axis_label[y_axis]} [ Color: {mappings.colorization_title_suffix[colorization_field]} ]'
        graph_params['y_axis_label'] = mappings.y_axis_label[y_axis]
        graph_params['width'] = plot_width
        graph_params['height'] = plot_height
        graph_params['palette'] = palette
        graph_params['point_size'] = point_size
        graph_params['x_axis'] = 'value'
        graph_params['y_axis'] = mappings.y_axis_values[y_axis]
        graph_params['output_file_title'] = project_title
        graph_params['output_file_path'] = html_filepath

        return graph_params


    def get_color_factors(self, palette_range: int) -> list[str]:
        factors_list = []
        for index in range(palette_range):
            factors_list.append(str(index))

        return factors_list


    def generate_plot(self, logger: Logger, config: ConfigAgent, data: pd.DataFrame, project_title: str, html_filepath: str):
        plot = BokehScatterAgent()
        plot.set_data(data)
        logger.debug('Plot data set')

        palette_range = config.plot.palette_range
        config.add_parameter('local', 'plot_points', len(data))

        graph_params = self.get_graph_params(config, logger, project_title, html_filepath)
        plot.set_params(graph_params)
        logger.debug('Graph params collated')

        tooltips = [('number', '@value')]
        if self.cfg.set.include_primes:
            tooltips.append('is_prime', '@prime_factors')
        tooltips.extend([
                    ('factors', '@prime_factors'),
                    ('mean factor value', '@ideal_factor'),
                    ('mean factor deviation', '@mean_deviation'),
                    ('antislope', '@antislope'),
                    ('division family', '@division_family')])

        plot.set_tooltips(tooltips)
        logger.debug('Tooltips set')

        color_factors = self.get_color_factors(palette_range)
        plot.set_color_factors(color_factors)
        logger.debug('Color factors set')

        plot.generate()
        logger.info('Plot generated')

        return plot
    

    def get_data(self, logger: Logger, config: ConfigAgent, data_manager: DataManager) -> pd.DataFrame:
        logger.debug('Loading data from file')
        value_list = self.generate_number_list()
        data_df = data_manager.load_data(value_list)
        if len(data_df) < len(value_list):
            if not self.cfg.set.ignore_missing_plot_values:
                self.logger.error(f'Requested data is not in the db; {len(value_list) - len(data_df)} records missing')
                end = datetime.utcnow()
                self.logger.info(f'End at {end}')
                self.logger.info(f'Total time: {end-self.cfg.local.start}')

                self.stash_log_file('PLOT')
                exit()

        # TODO do we need filters before plotting ?
        # if config.filters.filter_data:
        #      logger.info(f'Filtering data: {config.filters.filter_name}')
        #      data_df = filter_data(config, data_df)
        #      config.add_parameter('local', 'filter_name', config.filters.filter_name)

        return data_df



    def generate_number_list(self):
        self.logger.info('Generating values')
        step_start = datetime.utcnow()
        if self.cfg.set.mode == 'family':
            self.logger.debug('Processing families')
            number_list = self.generate_number_families()
        elif self.cfg.set.mode == 'range':
            self.logger.debug('Processing range')
            number_list = self.generate_continuous_number_list()
        step_end = datetime.utcnow()
        self.logger.debug(f'...done in {step_end-step_start}')
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


    def generate(self):
        number_list = self.generate_number_list()
        # filter existing data
        terminate = False
        try:
            starting_value_count = len(number_list)
            existing_data = self.data_manager.load_value_data(number_list)
            if len(existing_data) == len(number_list):
                self.logger.info('Data is already in the db')
                end = datetime.utcnow()
                self.logger.info(f'End at {end}')
                self.logger.info(f'Total time: {end-self.cfg.local.start}')
                terminate = True
            else:
                number_list = [value for value in number_list if value not in existing_data['value'].tolist()]
                if starting_value_count > len(number_list):
                    self.logger.debug(f'Some records found in the db; proceeding with {len(number_list)} values')
                else:
                    self.logger.debug('All values are new; proceeding with values')
        except Exception as e:
            self.logger.debug(f'Could not load existing data records : {e}')
            self.logger.debug('Proceeding with all values')
        if terminate:
            exit()
        collection_df = decompose(self.logger, number_list)
        self.logger.info('Saving data')
        step_start = datetime.utcnow()
        self.data_manager.save_data(collection_df)
        step_end = datetime.utcnow()
        self.logger.debug(f'...done in {step_end-step_start}')


    def parse_factors(self, factors_string: str) -> list[int]:
        factors_str_list = factors_string.split(sep=",")
        factors_int_list = [int(value) for value in factors_str_list]

        return factors_int_list


    def get_property_buckets(self, data: pd.DataFrame, parameter: str, use_rounding: str = 'full') -> (list[int], dict):
        '''
        Split numbers into buckets, based in the provided parameter
        '''
        buckets_list = []
        param_buckets = {}
        for index, number in data.iterrows():
            if number['is_prime'] and not self.cfg.set.include_primes:
                continue
            else:
                try:
                    property = number[parameter]
                except:
                    raise Exception

                if use_rounding == 'full':
                    property = round(property)
                elif use_rounding == 'down':
                    property = math.floor(property)
                elif use_rounding == 'up':
                    property = math.ceil(property)

                if property not in buckets_list:
                    buckets_list.append(property)
                    param_buckets[property] = []
                param_buckets[property].append(number)

        return buckets_list, param_buckets


    def get_max_sum(self, limit: int, base: int):
        '''
        Get the sum of the first 'power' powers of 'base'
        '''

        counter = 0
        sum = 0
        while counter < limit:
            sum += base**counter
            counter += 1

        return sum


    def get_bucket_base(self, limit: int, volume: int):
        '''
        Calculate the base that offers bucket coverage for a maximum number of powers
        '''

        base = 1
        max_sum = 0
        while max_sum < volume:
            base += 1
            max_sum = self.get_max_sum(limit, base)

        return base


    def get_number_of_colors_in_palette(self, palette: dict):
        '''
        Get the maximum number of colors, supported by the palette
        '''
        count = sorted(palette.keys())[-1]
        return count


    def get_power_of_n(self, value: int, base: int):
        '''
        Get the lowest power of a base that's equal or higher than the provided number
        '''

        if value == 1:
            return 1

        counter = 0
        intermediate_product = 1
        while intermediate_product < value:
            intermediate_product += base**counter
            counter += 1

        return counter


    def filter_property_buckets(self, sorted_property_buckets: dict, cut_off_value: int):
        trimmed_property_buckets = {}
        for index, item in sorted_property_buckets.items():
            trimmed_property_buckets[index] = item

        filtered_property_buckets = []
        counter = 1
        while counter <= cut_off_value and len(trimmed_property_buckets) > 0:
            item = next(iter(trimmed_property_buckets.items()))
            filtered_property_buckets.extend(item[1])
            trimmed_property_buckets.pop(item[0])
            counter += 1

        return filtered_property_buckets, trimmed_property_buckets


    def get_buckets(self, sorted_buckets_list: list, sorted_property_buckets: dict, palette) -> dict:
        '''
        Split numbers into buckets by a given property

        The first bucket contains numbers with one property value
        The next bucket contains X times more property values than the previous one
        X is determined so that the palette can cover all property values
        '''

        global palette_color_range

        number_of_unassigned_buckets = len(sorted_buckets_list)
        palette_color_range = self.get_number_of_colors_in_palette(palette=palette)
        bucket_base = self.get_bucket_base(palette_color_range, number_of_unassigned_buckets)
        self.logger.info(f'Buckets to be distributed: {number_of_unassigned_buckets}')
        self.logger.info(f'Base chosen: {bucket_base}')
        number_of_binary_buckets = self.get_power_of_n(number_of_unassigned_buckets, base=bucket_base)

        # create binary bucket index map
        binary_bucket_index_map = {}
        binary_buckets = {}

        for counter in range(number_of_binary_buckets + 1):
            bucket_count = pow(bucket_base, counter)
            binary_bucket_index = counter
            binary_buckets[binary_bucket_index] = []
            filtered_property_bucket, sorted_property_buckets = self.filter_property_buckets(sorted_property_buckets, bucket_count)
            if len(filtered_property_bucket) > 0:
                binary_buckets[binary_bucket_index].extend(filtered_property_bucket)
                binary_bucket_index_map[binary_bucket_index] = []
                binary_bucket_index_map[binary_bucket_index].extend(sorted_buckets_list[:bucket_count])
                sorted_buckets_list = sorted_buckets_list[bucket_count:]
            else:
                binary_buckets.pop(binary_bucket_index)

        return binary_buckets


    def get_palette(self, palette_name: str) -> dict:
        '''
        Returns a bokeh palette, corresponding to a given str palette name
        '''

        # Magma, Inferno, Plasma, Viridis, Cividis, Turbo
        if palette_name == 'Magma':
            return Magma
        elif palette_name == 'Inferno':
            return Inferno
        elif palette_name == 'Plasma':
            return Plasma
        elif palette_name == 'Viridis':
            return Viridis
        elif palette_name == 'Cividis':
            return Cividis
        elif palette_name == 'Turbo':
            return Turbo
        elif palette_name == 'Category10':
            return Category10
        elif palette_name == 'Dark2':
            return Dark2
        else:
            return Turbo
    

    def get_binary_buckets_map(self, binary_buckets):
        bucket_map = {}
        for index, numbers in binary_buckets.items():
            for number in numbers:
                bucket_map[number[0]] = index

        return bucket_map


    def get_colour_bucket_index_(self, binary_bucket_map, value):
        index = binary_bucket_map[value]
        return index


    def collection_to_df(self, data: pd.DataFrame, palette_range: int, colorization_field: str) -> pd.DataFrame:
        # add coloration index column
        rawdict = data.to_dict(orient='records')
        data_dict = {}
        data_dict['value'] = []
        data_dict['is_prime'] = []
        data_dict['prime_factors'] = []
        data_dict['small_factors'] = []
        data_dict['largest_factor'] = []
        data_dict['division_family'] = []
        data_dict['ideal_factor'] = []
        data_dict['mean_deviation'] = []
        data_dict['antislope'] = []
        data_dict['color_bucket'] = []

        # TODO OPTIMIZE BUCKETS
        # BUCKETS
        colorization_field = mappings.colorization_field[self.cfg.plot.colorization_value]
        buckets_list, property_buckets = self.get_property_buckets(data, parameter = colorization_field, use_rounding = self.cfg.plot.property_rounding)

        # [x] pour numbers into binary buckets
        sorted_property_buckets = collections.OrderedDict(sorted(property_buckets.items()))
        sorted_buckets_list = sorted(buckets_list)
        palette = self.get_palette(palette_name=self.cfg.plot.palette)
        binary_buckets = self.get_buckets(sorted_buckets_list, sorted_property_buckets, palette)
        binary_buckets_map = self.get_binary_buckets_map(binary_buckets)


        max_value = (data[colorization_field].max())
        # check for values
        if max_value == 0:
            return None

        with Bar('Generating plot data', max=len(rawdict)) as bar:
            for item in rawdict:
                data_dict['value'].append(item['value'])
                data_dict['is_prime'].append('True' if item['is_prime'] else 'False')
                prime_factors = self.parse_factors(item['prime_factors'])
                data_dict['prime_factors'].append(prime_factors)
                family_factors = prime_factors[:-1]
                data_dict['small_factors'].append(family_factors)
                data_dict['largest_factor'].append(prime_factors[-1])
                data_dict['division_family'].append(item['division_family'])
                data_dict['ideal_factor'].append(item['ideal_factor'])
                data_dict['mean_deviation'].append(item['mean_deviation'])
                data_dict['antislope'].append(item['antislope'])

                # TODO HERE OPTIMIZE BUCKET SEARCH
                data_dict['color_bucket'].append(self.get_colour_bucket_index_(binary_buckets_map, item['value']))
                bar.next()

        data_df = pd.DataFrame(data_dict)

        return data_df        


    def prepare_data(self, config: ConfigAgent, data: pd.DataFrame) -> pd.DataFrame:
        # enchancing data
        palette_range = config.plot.palette_range
        colorization_field_config = config.plot.colorization_value
        colorization_field = mappings.colorization_field[colorization_field_config]
        data_df = self.collection_to_df(data=data, palette_range=palette_range, colorization_field=colorization_field)

        return data_df

    def plot(self):
        data = self.get_data(self.logger, self.cfg, self.data_manager)

        # prepare data for plot
        self.logger.info('Preparing data')
        data = self.prepare_data(self.cfg, data)

        # plot data
        html_filepath = self.cfg.local.html_filepath
        project_title = self.cfg.local.project_title
        plot = self.generate_plot(self.logger, self.cfg, data, project_title, html_filepath)

        plot.display_plot()
        self.logger.info('Displaying plot')

    def run(self):
        self.logger.info(f'Start at {self.cfg.local.start}')
        self.log_settings()
        mode = self.cfg.mode.mode
        if mode == 'generate':
            self.generate()
            logger_filename_prefix = 'GEN'
        else:
            self.plot()
            logger_filename_prefix = 'PLOT'

        end = datetime.utcnow()
        self.logger.info(f'End at {end}')
        self.logger.info(f'Total time: {end-self.cfg.local.start}')

        self.stash_log_file(logger_filename_prefix)
        # TODO Stash html
