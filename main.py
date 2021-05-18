from configparser import ConfigParser
from bokeh.plotting import figure, show
from bokeh import models as models
from bokeh.models import ColumnDataSource, CategoricalColorMapper
from bokeh.palettes import Magma, Inferno, Plasma, Viridis, Cividis, Turbo, Greys
from bokeh.palettes import Magma256, Inferno256, Plasma256, Viridis256, Cividis256, Turbo256, Greys256
from datetime import datetime
import logging
import math
import os
from typing import List, Dict, Tuple
import pandas as pd

from number import Number

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create console handler and set level to debug
ch = logging.StreamHandler()
# create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


config = ConfigParser()

config.read('config.ini')

lowerbound = int(config.get('range', 'lowerbound'))
upperbound = int(config.get('range', 'upperbound'))


include_primes = False


def run(lowerbound=2, upperbound=10):
    logger.info('start')
    global include_primes
    include_primes = True if config.get(
        'run', 'include_primes') == 'True' else False

    # [x] iterate between bounds and cache numbers
    number_list = generate_number_list(
        lowerbound=lowerbound, upperbound=upperbound)
    logger.info(f'Numbers generated {lowerbound}..{upperbound}')

    # [x] create visualization
    create_visualization(number_list)


def get_binary_buckets(sorted_buckets_list: List, slope_buckets: Dict) -> Dict:
    number_of_unassigned_buckets = len(sorted_buckets_list)
    number_of_binary_buckets = get_previous_power_of_two(
        number_of_unassigned_buckets)

    # create binary bucket index map
    binary_bucket_index_map = {}
    binary_slope_buckets = {}
    for counter in range(number_of_binary_buckets + 1):
        binary_bucket_index = number_of_binary_buckets - counter
        binary_bucket_index_map[binary_bucket_index] = []
        binary_slope_buckets[binary_bucket_index] = []
        cutoff = math.floor(len(sorted_buckets_list)/2)
        binary_bucket_index_map[binary_bucket_index].extend(
            sorted_buckets_list[cutoff:])
        sorted_buckets_list = sorted_buckets_list[:cutoff]

    # distribute numbers in the binary buckets according to slope
    for number in slope_buckets.items():
        binary_bucket_index = get_binary_bucket_index(
            number[0], binary_bucket_index_map)
        binary_slope_buckets[binary_bucket_index].extend(number[1])

    return binary_slope_buckets


def get_binary_bucket_index(slope: int, binary_bucket_index_map: Dict) -> int:
    for bucket_index, slope_list in binary_bucket_index_map.items():
        if slope in slope_list:
            return bucket_index


def get_previous_power_of_two(number: int):
    running_product = 1
    counter = 0
    while running_product < number:
        running_product = running_product * 2
        counter = counter + 1
    return counter - 1


def get_slope_buckets(number_list: List) -> Tuple:
    buckets_list = []
    slope_buckets = {}
    for number in number_list:
        if number.is_prime and not include_primes:
            continue
        else:
            slope_int = round(number.slope)
            if slope_int not in buckets_list:
                buckets_list.append(slope_int)
                slope_buckets[slope_int] = []
            slope_buckets[slope_int].append(number)

    return buckets_list, slope_buckets


def create_visualization(number_list: List[Number]):

    use_bucket_colorization = True if config.get(
        'run', 'use_color_buckets') == 'true' else False

    if use_bucket_colorization:
        # [x] separate numbers into binary buckets by closest integer to number.slope
        # [x] get primary slope buckets
        buckets_list, slope_buckets = get_slope_buckets(number_list)

        # [x] pour numbers into binary buckets
        binary_buckets = get_binary_buckets(
            sorted(buckets_list), slope_buckets)

    # [x] prep visualization data
    data_dict = {}
    data_dict['number'] = []
    if include_primes:
        data_dict['is_prime'] = []
    data_dict['prime_factors'] = []
    data_dict['mean'] = []
    data_dict['deviation'] = []
    data_dict['one_over_slope'] = []
    if use_bucket_colorization:
        data_dict['color_bucket'] = []
    for number in number_list:
        if number.is_prime:
            continue
        data_dict['number'].append(number.value)
        if include_primes:
            data_dict['is_prime'].append(
                'true' if number.is_prime else 'false')
        data_dict['prime_factors'].append(
            int_list_to_str(number.prime_factors))
        data_dict['mean'].append(number.prime_mean)
        data_dict['deviation'].append(number.mean_deviation)
        data_dict['one_over_slope'].append(number.slope)
        if use_bucket_colorization:
            data_dict['color_bucket'].append(
                get_bucket_index(binary_buckets, number.value))

    data_df = pd.DataFrame(data_dict)
    data_df.reset_index()
    data = ColumnDataSource(data=data_df)
    logger.info(f'Data collated')

    # [x] 'hard copy'
    if config.get('run', 'crate_csv'):
        timestamp_format = generate_timestamp()
        timestamp = datetime.utcnow().strftime(timestamp_format)
        primes_included = 'primes_' if include_primes else 'no_primes_'
        hard_copy_filename = str(lowerbound) + '_' + str(upperbound) + \
            '_' + primes_included + '_' + timestamp + '.csv'
        csv_output_folder = 'csv_output_folder'
        path = csv_output_folder + '\\'
        if not os.path.exists(csv_output_folder):
            os.mkdir(csv_output_folder)
        data_df.to_csv(path + hard_copy_filename)
        logger.info(f'Saved data as {hard_copy_filename}')

    # [x] create plot
    plot_width = int(config.get('graph', 'width'))
    plot_height = int(config.get('graph', 'height'))
    graph = figure(title=f"Mean prime factor deviations for numbers {data_dict['number'][0]} to {data_dict['number'][-1]}",
                   x_axis_label='number', y_axis_label='mean prime factor deviation', width=plot_width, height=plot_height)

    # [x] add hover tool
    if primes_included:
        hover = models.HoverTool(tooltips=[('number', '@number'),
                                           ('prime', '@is_prime'),
                                           ('factors', '@prime_factors'),
                                           ('mean factor value', '@mean'),
                                           ('mean factor deviation', '@deviation'),
                                           ('anti-slope', '@one_over_slope')])
    else:
        hover = models.HoverTool(tooltips=[('number', '@number'),
                                           ('factors', '@prime_factors'),
                                           ('mean factor value', '@mean'),
                                           ('mean factor deviation', '@deviation'),
                                           ('anti-slope', '@one_over_slope')])
    graph.add_tools(hover)

    # [x] add graph
    number_of_colors = len(binary_buckets)
    if use_bucket_colorization and number_of_colors <= 11:
        factors_list = get_factors(number_of_colors)
        color_mapper = CategoricalColorMapper(factors=factors_list, palette=Turbo[number_of_colors])
        logger.info(f'{number_of_colors} color buckets created')
        graph.scatter(source=data, x='number', y='deviation', color={
                      'field': 'color_bucket', 'transform': color_mapper}, size=5)
    else:
        base_color = '#' + config.get('graph', 'base_color')
        logger.info('Base coloring')
        graph.scatter(source=data, x='number', y='deviation',
                      color=base_color, size=5)

    # [x] show
    logger.info('Graph generated')
    show(graph)


def get_factors(number_of_colors: int) -> List:
    factors_list = []
    for index in range(number_of_colors):
        factors_list.append(str(index))

    return factors_list


def get_bucket_index(binary_buckets: Dict, value: int) -> int:
    for index, numbers in binary_buckets.items():
        for number in numbers:
            if value == number.value:
                return str(index)


def generate_timestamp():
    # '%d%m%Y_%H%M%S'
    timestamp_format = ''
    timestamp_granularity = int(config.get(
        'run', 'hard_copy_timestamp_granularity'))
    format_chunks = ['%d%m%Y', '_%H', '%M', '%S']
    for chunk_index in range(timestamp_granularity + 1):
        timestamp_format += format_chunks[chunk_index]
    return timestamp_format


def int_list_to_str(number_list: List[int], separator=', ', use_bookends=True, bookends=['[ ', ' ]']):
    stringified_list = []
    for number in number_list:
        stringified_list.append(str(number))
    list_string = separator.join(stringified_list)
    if use_bookends:
        return bookends[0] + list_string + bookends[1]
    else:
        return list_string


def generate_number_list(lowerbound=2, upperbound=10):
    number_list = []
    for value in range(lowerbound, upperbound + 1):
        number = Number(value=value)
        number_list.append(number)
    return number_list


if __name__ == "__main__":
    run(lowerbound=lowerbound, upperbound=upperbound)
