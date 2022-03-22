from configparser import ConfigParser
from bokeh.plotting import figure, show
from bokeh import models as models
from bokeh.models import ColumnDataSource, CategoricalColorMapper
from bokeh.palettes import Magma, Inferno, Plasma, Viridis, Cividis, Turbo
from datetime import datetime
import logging
import math
import os
import pyprimes as pp
from typing import List, Dict, Tuple
import pandas as pd

import mappings
from number import Number

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create console handler and set level to debug
ch = logging.StreamHandler()
# create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - [%(levelname)-5s] %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


config = ConfigParser()

config.read('config.ini')

lowerbound = int(config.get('range', 'lowerbound'))
upperbound = int(config.get('range', 'upperbound'))

# RUN parameters
use_bucket_colorization = True if config.get(
    'graph', 'use_color_buckets') == 'true' else False
include_primes = True if config.get(
    'run', 'include_primes') == 'true' else False
create_csv = config.get('run', 'crate_csv')
palette = Turbo
palette_name = config.get('graph', 'palette')
graph_mode = config.get('graph', 'mode')


def run(lowerbound=2, upperbound=10):
    global include_primes
    global create_csv
    global use_bucket_colorization
    global palette_name
    global palette
    global graph_mode

    start = datetime.utcnow()
    logger.info(f'Start at {start}')
    logger.info(f'* Range [{lowerbound}..{upperbound}]')
    logger.info(f'* Mode: "{graph_mode}"')
    include_primes_message = '* Primes included' if include_primes else '* Primes NOT included'
    logger.info(include_primes_message)
    create_csv_message = '* CSV output included' if create_csv else '* No CVS output'
    logger.info(create_csv_message)
    palette_name_string = 'Default (Turbo)' if palette_name == 'Default' else palette_name
    bucket_colorization_message = f'* Bucket colorization enabled: {palette_name_string}' if use_bucket_colorization else '* Monocolor enabled'
    logger.info(bucket_colorization_message)
    palette = get_palette(palette_name=palette_name)

    # [x] iterate between bounds and cache numbers
    number_list = generate_number_list(
        lowerbound=lowerbound, upperbound=upperbound)
    logger.info(f'Numbers generated {lowerbound}..{upperbound}')

    # [x] create visualization
    create_visualization(number_list)
    end = datetime.utcnow()
    logger.info(f'End at {end}')
    logger.info(f'Total time: {end-start}')


def create_visualization(number_list: List[Number]):
    '''
    Prepares the generated number data and uses it to create the visualization
    '''

    if use_bucket_colorization:
        # [x] separate numbers into binary buckets by closest integer to number.anti_slope
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
    data_dict['ideal'] = []
    data_dict['deviation'] = []
    data_dict['one_over_slope'] = []
    data_dict['primes_before_largest'] = []
    data_dict['largest_prime_factor'] = []
    data_dict['div_family'] = []
    if use_bucket_colorization:
        data_dict['color_bucket'] = []
    for number in number_list:
        data_dict['number'].append(number.value)
        if include_primes:
            data_dict['is_prime'].append(
                'true' if number.is_prime else 'false')
        data_dict['prime_factors'].append(
            int_list_to_str(number.prime_factors))
        data_dict['ideal'].append(number.ideal_factor)
        data_dict['deviation'].append(number.mean_deviation)
        data_dict['one_over_slope'].append(number.anti_slope)
        if number.value == 1:
            data_dict['primes_before_largest'].append(0)
            data_dict['largest_prime_factor'].append(0)
            data_dict['div_family'].append(1)
        else:
            primes_before_largest, largest_prime_factor = split_prime_factors(
                number.prime_factors)
            data_dict['primes_before_largest'].append(
                int_list_to_str(primes_before_largest))
            data_dict['largest_prime_factor'].append(largest_prime_factor)
            data_dict['div_family'].append(number.value / largest_prime_factor)
        if use_bucket_colorization:
            data_dict['color_bucket'].append(
                get_bucket_index(binary_buckets, number.value))

    data_df = pd.DataFrame(data_dict)
    data_df.reset_index()
    data = ColumnDataSource(data=data_df)
    logger.info(f'Data collated')

    # [x] create plot
    plot_width = int(config.get('graph', 'width'))
    plot_height = int(config.get('graph', 'height'))
    primes_included_text = " Primes included" if include_primes else " Primes excluded"

    graph_params = {}
    graph_params['title'] = mappings.graph_title[graph_mode].format(
        data_dict['number'][0], data_dict['number'][-1]) + primes_included_text
    graph_params['y_axis_label'] = mappings.y_axis_label[graph_mode]
    graph_params['width'] = plot_width
    graph_params['height'] = plot_height

    graph = get_figure(graph_params)

    # [x] add hover tool
    tooltips = [('number', '@number')]
    if include_primes:
        tooltips.append(('prime', '@is_prime'))
    tooltips.extend([('factors', '@prime_factors'),
                    ('ideal factor value', '@ideal'),
                    ('mean factor deviation', '@deviation'),
                    ('anti-slope', '@one_over_slope'),
                    ('prime factors before largest', '@primes_before_largest'),
                    ('largest prime factor', '@largest_prime_factor'),
                    ('division family', '@div_family'),
                     ])

    hover = models.HoverTool(tooltips=tooltips)
    graph.add_tools(hover)

    # [x] add graph
    if use_bucket_colorization:
        number_of_colors = len(binary_buckets)
    graph_point_size = int(config.get('graph', 'point_size'))

    graph_params['type'] = 'scatter'
    graph_params['y_value'] = mappings.y_axis_values[graph_mode]
    graph_params['graph_point_size'] = graph_point_size
    graph_params['use_bucket_colorization'] = use_bucket_colorization
    if use_bucket_colorization:
        graph_params['number_of_colors'] = number_of_colors
        graph_params['factors_list'] = get_factors(number_of_colors)
    graph_params['palette'] = palette

    graph, coloring = create_graph(graph, data, graph_params)

    # [x] 'hard copy'
    graph_mode_chunk = mappings.graph_mode_filename_chunk[graph_mode]
    timestamp_format = generate_timestamp()
    timestamp = datetime.utcnow().strftime(timestamp_format)
    primes_included = 'primes' if include_primes else 'no_primes'
    hard_copy_filename = str(lowerbound) + '_' + str(upperbound) + \
        '_' + graph_mode_chunk + '_' + primes_included + '_' + coloring + '_' + timestamp
    csv_output_folder = 'output'
    if create_csv:
        full_hard_copy_filename = hard_copy_filename + '.csv'
        path = csv_output_folder + '\\'
        prep_output_folder(csv_output_folder)
        data_df.to_csv(path + full_hard_copy_filename)
        logger.info(f'Data saved as output\{full_hard_copy_filename}')

    # [x] show
    logger.info('Graph generated')
    show(graph)

    stash_graph_html(csv_output_folder, hard_copy_filename)


def create_graph(graph: figure, data: ColumnDataSource, graph_params: Dict) -> figure:
    '''
    Creates a scatter plot by given parameters
    '''

    coloring = ''
    use_bucket_colorization = graph_params['use_bucket_colorization']
    if use_bucket_colorization:
        number_of_colors = graph_params['number_of_colors']
        factors_list = graph_params['factors_list']
    y_value = graph_params['y_value']
    graph_point_size = graph_params['graph_point_size']
    palette = graph_params['palette']

    if use_bucket_colorization and number_of_colors <= 11:
        factors_list = get_factors(number_of_colors)
        color_mapper = CategoricalColorMapper(
            factors=factors_list, palette=palette[number_of_colors])
        logger.info(f'{number_of_colors} color buckets created')
        graph.scatter(source=data, x='number', y=y_value, color={
                      'field': 'color_bucket', 'transform': color_mapper}, size=graph_point_size)
        coloring = palette_name.lower()
    else:
        base_color = '#3030ff'
        logger.info('Base coloring')
        graph.scatter(source=data, x='number', y=y_value,
                      color=base_color, size=graph_point_size)
        coloring = 'monocolor'

    return graph, coloring


def stash_graph_html(csv_output_folder, graph_filename: str):
    full_stashed_filename = csv_output_folder + '\\' + graph_filename + '.html'
    with open('main.html', 'r') as html_output_file:
        content = html_output_file.read()
        with open(full_stashed_filename, 'wt') as stashed_html_output_file:
            stashed_html_output_file.write(content)
    logger.info(f'Graph saved as {full_stashed_filename}')


def get_palette(palette_name: str) -> palette:
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
    else:
        return Turbo


def get_figure(params: Dict) -> figure:
    '''
    Returns a figure with the provided parameters
    '''
    title = params['title']
    y_axis_label = params['y_axis_label']
    width = params['width']
    height = params['height']

    return figure(title=title, x_axis_label='number', y_axis_label=y_axis_label, width=width, height=height)


def split_prime_factors(int_list: List[int]) -> int:
    sorted_int_list = sorted(int_list)
    return sorted_int_list[:-1], sorted_int_list[-1]


def get_binary_buckets(sorted_buckets_list: List, slope_buckets: Dict) -> Dict:
    '''
    Split numbers into binary buckets by antislope

    The lowest bucket (highest index) contains half of the antislopes - the highest antislope
    Th next buckets contains half of the remaining antislopes - again the highest ones
    Each bucket above contains half as many members
    The top buket always has one antislope
    '''

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
    '''
    Get the index of the binary bucket by antislope value
    '''

    for bucket_index, slope_list in binary_bucket_index_map.items():
        if slope in slope_list:
            return bucket_index


def get_previous_power_of_two(value: int):
    '''
    Get the highest poewr of 2 that's loewr than a provide number
    '''

    running_product = 1
    counter = 0
    while running_product < value:
        running_product = running_product * 2
        counter = counter + 1
    return counter - 1


def get_slope_buckets(number_list: List) -> Tuple:
    '''
    Split numbers into buckets, based on the integer value their antislope converges to
    '''

    buckets_list = []
    slope_buckets = {}
    for number in number_list:
        if number.is_prime and not include_primes:
            continue
        else:
            slope_int = round(number.anti_slope)
            if slope_int not in buckets_list:
                buckets_list.append(slope_int)
                slope_buckets[slope_int] = []
            slope_buckets[slope_int].append(number)

    return buckets_list, slope_buckets


def prep_output_folder(folder_name: str):
    '''
    Prepare folder for output csv files
    '''

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        return
    else:
        if config.get('run', 'reset_output_data') == 'true':
            for root, directories, files in os.walk(folder_name):
                for file in files:
                    file_path = root + '/' + file
                    os.remove(file_path)
        return


def get_factors(number_of_colors: int) -> List:
    '''
    Compile the factors of a number as a list of strings
    '''

    factors_list = []
    for index in range(number_of_colors):
        factors_list.append(str(index))

    return factors_list


def get_bucket_index(binary_buckets: Dict, value: int) -> int:
    '''
    Get the index of the binary bucket that a number in
    '''

    for index, numbers in binary_buckets.items():
        for number in numbers:
            if value == number.value:
                return str(index)


def generate_timestamp():
    '''
    Generate timestamp string, depending on the desired granularity, set in config.ini
    '''

    timestamp_format = ''
    timestamp_granularity = int(config.get(
        'run', 'hard_copy_timestamp_granularity'))
    format_chunks = ['%d%m%Y', '_%H', '%M', '%S']
    for chunk_index in range(timestamp_granularity + 1):
        timestamp_format += format_chunks[chunk_index]
    return timestamp_format


def int_list_to_str(number_list: List[int], separator=', ', use_bookends=True, bookends=['[ ', ' ]']):
    '''
    Generate a string from a list of integers
    '''

    stringified_list = []
    for number in number_list:
        stringified_list.append(str(number))
    list_string = separator.join(stringified_list)
    if use_bookends:
        return bookends[0] + list_string + bookends[1]
    else:
        return list_string


def generate_number_list(lowerbound=2, upperbound=10):
    '''
    Generate a list of Number objects
    '''

    number_list = []
    for value in range(lowerbound, upperbound + 1):
        if pp.isprime(value) and not include_primes:
            continue
        number = Number(value=value)
        number_list.append(number)
    return number_list


if __name__ == "__main__":
    run(lowerbound=lowerbound, upperbound=upperbound)
