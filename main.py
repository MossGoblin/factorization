import collections
import math
import os
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd
import pyprimes as pp
from bokeh import models as models
from bokeh.models import CategoricalColorMapper, ColumnDataSource
from bokeh.palettes import (Category10, Cividis, Dark2, Inferno, Magma, Plasma,
                            Turbo, Viridis)
from bokeh.plotting import figure, show
from progress.bar import Bar

import toolbox.logger_service as logger_service
import toolbox.mappings as mappings
from toolbox.config_agent import ConfigAgent
from toolbox.number import Number

logger_name = 'run.log'
config_name = 'config.toml'

logger = logger_service.get_logger(logger_name)
cfg = ConfigAgent(config_path=config_name)

lowerbound = cfg.range.lowerbound
upperbound = cfg.range.upperbound

# RUN parameters
use_bucket_colorization = cfg.graph.use_color_buckets
include_primes = cfg.run.include_primes
create_csv = cfg.run.create_csv
palette = Turbo
palette_name = cfg.graph.palette
graph_mode = cfg.graph.visualization_mode
colorization_mode = cfg.graph.colorization_mode
if colorization_mode == 'default':
    colorization_mode = graph_mode
property_rounding = cfg.graph.property_rounding
full_antislope_display = cfg.graph.full_antislope_display
try:
    families_filter = cfg.filter.families
except AttributeError:
    families_filter = []

palette_color_range = 0
CSV_OUTPUT_FOLDER = 'output'

def run(lowerbound=2, upperbound=10):
    global include_primes
    global create_csv
    global use_bucket_colorization
    global palette_name
    global palette
    global graph_mode
    global palette_color_range


    start = datetime.now()
    logger.info(f'Start at {start}')
    logger.info(f'* Range [{lowerbound}..{upperbound}]')
    families_list_str = [str(family) for family in families_filter]
    filter_text = ": All" if len(families_filter) == 0 else " [ " + ", ".join(families_list_str) + " ]"
    logger.info(f'* Families{filter_text}')
    logger.info(f'* Graph mode: "{graph_mode}"')
    logger.info(f'* Colorization mode: "{colorization_mode}"')
    include_primes_message = '* Primes included' if include_primes else '* Primes NOT included'
    logger.info(include_primes_message)
    create_csv_message = '* CSV output included' if create_csv else '* No CVS output'
    logger.info(create_csv_message)
    palette_name_string = 'Default (Turbo)' if palette_name == 'Default' else palette_name
    bucket_colorization_message = f'* Bucket colorization enabled: {palette_name_string}' if use_bucket_colorization else '* Monocolor enabled'
    logger.info(bucket_colorization_message)
    palette = get_palette(palette_name=palette_name)

    # [x] iterate between bounds and cache numbers
    number_list = generate_number_list(lowerbound=lowerbound, upperbound=upperbound, families_filter=families_filter)
    if len(number_list) == 0:
        logger.info(f'No composites generated. Terminating the program.')
        end = datetime.now()
        logger.info(f'End at {end}')
        logger.info(f'Total time: {end-start}')
        quit()
    logger.info(f'Numbers iterated {lowerbound}..{upperbound}')
    logger.info(f'Total composites: {len(number_list)}')

    # [x] create visualization
    hard_copy_filename = create_visualization(number_list)
    end = datetime.now()
    logger.info(f'End at {end}')
    logger.info(f'Total time: {end-start}')
 
    stash_graph_html(CSV_OUTPUT_FOLDER, hard_copy_filename)
    stash_log_file(CSV_OUTPUT_FOLDER, hard_copy_filename)


def get_max_sum(limit: int, base: int):
    '''
    Get the sum of the first 'power' powers of 'base'
    '''

    counter = 0
    sum = 0
    while counter < limit:
        sum += base**counter
        counter += 1
    
    return sum


def get_bucket_base(limit: int, volume: int):
    '''
    Calculate the base that offers bucket coverage for a maximum number of powers
    '''

    base = 1
    max_sum = 0
    while max_sum < volume:
        base += 1
        max_sum = get_max_sum(limit, base)
    
    return base


def get_number_of_colors_in_palette(palette: Dict):
    '''
    Get the maximum number of colors, supported by the palette
    '''
    # HERE
    count = sorted(palette.keys())[-1]
    return count


def create_visualization(number_list: List[Number]):
    '''
    Prepares the generated number data and uses it to create the visualization
    '''

    if use_bucket_colorization:
        # [x] separate numbers into binary buckets by closest integer to a given property
        # [x] get primary slope buckets
        buckets_list, property_buckets = get_property_buckets(number_list, parameter = colorization_mode, use_rounding = property_rounding)

        # [x] pour numbers into binary buckets
        sorted_property_buckets = collections.OrderedDict(sorted(property_buckets.items()))
        sorted_buckets_list = sorted(buckets_list)
        binary_buckets = get_buckets(sorted_buckets_list, sorted_property_buckets)

    # [x] prep visualization data
    data_dict = {}
    data_dict['number'] = []
    if include_primes:
        data_dict['is_prime'] = []
    data_dict['prime_factors'] = []
    data_dict['mean'] = []
    data_dict['deviation'] = []
    data_dict['one_over_slope'] = []
    data_dict['primes_before_largest'] = []
    data_dict['largest_prime_factor'] = []
    data_dict['div_family'] = []
    if use_bucket_colorization:
        data_dict['color_bucket'] = []

    with Bar('Collating data', max=len(number_list)) as bar:
        for number in number_list:
            bar.next()
            data_dict['number'].append(number.value)
            if include_primes:
                data_dict['is_prime'].append(
                    'true' if number.is_prime else 'false')
            data_dict['prime_factors'].append(
                int_list_to_str(number.prime_factors))
            data_dict['mean'].append(number.prime_mean)
            data_dict['deviation'].append(number.mean_deviation)
            if full_antislope_display:
                data_dict['one_over_slope'].append(number.antislope_string)
            else:
                data_dict['one_over_slope'].append(float(number.antislope))
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
                data_dict['div_family'].append(number.division_family)
            if use_bucket_colorization:
                data_dict['color_bucket'].append(get_colour_bucket_index(binary_buckets, number.value))

    data_df = pd.DataFrame(data_dict)
    data_df.reset_index()
    data = ColumnDataSource(data=data_df)
    logger.info(f'Data collated')

    # [x] create plot
    plot_width = cfg.graph.width
    plot_height = cfg.graph.height
    family_filter_text = " All families."
    if len(families_filter) > 0 and len(families_filter) <= 5:
        family_filter_text = " Families: " + ", ".join([str(family) for family in families_filter]) + "."
    elif len(families_filter) > 0:
        family_filter_text = " Families: " + "...".join([str(families_filter[0]), str(families_filter[-1])]) + "."
    primes_included_text = " Primes included" if include_primes else " Primes excluded."

    graph_params = {}
    graph_params['title'] = mappings.graph_title[graph_mode].format(
        data_dict['number'][0], data_dict['number'][-1]) + family_filter_text + primes_included_text
    graph_params['y_axis_label'] = mappings.y_axis_label[graph_mode]
    graph_params['width'] = plot_width
    graph_params['height'] = plot_height

    graph = get_figure(graph_params)

    # [x] add hover tool
    tooltips = [('number', '@number')]
    if include_primes:
        tooltips.append(('prime', '@is_prime'))
    tooltips.extend([('factors', '@prime_factors'),
                    ('mean factor value', '@mean'),
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
    graph_point_size = cfg.graph.point_size

    # graph_params['type'] = 'scatter' # This does not seem to be necessary
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
    families_string = "All"
    if len(families_filter) > 0 and len(families_filter) <= 5:
        families_string = "_".join([str(family) for family in families_filter])
    elif len(families_filter) > 0:
        families_string = "__".join([str(families_filter[0]), str(families_filter[-1])])
    hard_copy_filename = str(lowerbound) + '_' + str(upperbound) + \
        '_' + graph_mode_chunk + '_' + primes_included + '_' + families_string + '_' + coloring + '_' + timestamp
    if create_csv:
        full_hard_copy_filename = hard_copy_filename + '.csv'
        path = CSV_OUTPUT_FOLDER + '\\'
        prep_output_folder(CSV_OUTPUT_FOLDER)
        data_df.to_csv(path + full_hard_copy_filename)
        logger.info(f'Data saved as output\full_hard_copy_filename')

    # [x] show
    logger.info('Graph generated')
    show(graph)

    return hard_copy_filename


def create_graph(graph: figure, data: ColumnDataSource, graph_params: Dict) -> figure:
    '''
    Creates a scatter plot by given parameters
    '''

    coloring = ''
    use_bucket_colorization = graph_params['use_bucket_colorization']
    if use_bucket_colorization:
        number_of_colors_required = graph_params['number_of_colors']
        factors_list = graph_params['factors_list']
    y_value = graph_params['y_value']
    graph_point_size = graph_params['graph_point_size']
    palette = graph_params['palette']

    if use_bucket_colorization and number_of_colors_required <= palette_color_range:
        factors_list = get_factors(number_of_colors_required)
        requested_number_of_colors = number_of_colors_required
        # HERE failsafe; should be redundant;
        # if the required number of colors does not exist in the palette, default to the 256 version of the palette
        if not number_of_colors_required in palette:
            number_of_colors_required = list(palette)[-1]
        color_mapper = CategoricalColorMapper(factors=factors_list, palette=palette[number_of_colors_required])
        if requested_number_of_colors != number_of_colors_required:
            logger.info(f'{requested_number_of_colors} colors unavailable. {number_of_colors_required} color buckets created')
        else:
            logger.info(f'{number_of_colors_required} color buckets created')
        graph.scatter(source=data, x='number', y=y_value, color={'field': 'color_bucket', 'transform': color_mapper}, size=graph_point_size)
        coloring = palette_name.lower()
    # HERE should be redundant case
    elif number_of_colors_required > palette_color_range:
        logger.info(f'Base coloring - {number_of_colors_required} colors exceeds palette range')
        base_color = '#3030ff'
        coloring = 'monocolor'
        graph.scatter(source=data, x='number', y=y_value, color=base_color, size=graph_point_size)
    else:
        logger.info('Base coloring - bucket colorization disabled')
        base_color = '#3030ff'
        coloring = 'monocolor'
        graph.scatter(source=data, x='number', y=y_value, color=base_color, size=graph_point_size)

    return graph, coloring


def stash_graph_html(csv_output_folder, graph_filename: str):
    '''Copy the last html file into the output folder'''
    full_stashed_filename = csv_output_folder + '\\' + graph_filename + '.html'
    if os.path.isfile(full_stashed_filename):
        os.remove(full_stashed_filename)
    with open('main.html', 'r') as html_input_file:
        content = html_input_file.read()
        with open(full_stashed_filename, 'wt') as stashed_html_output_file:
            stashed_html_output_file.write(content)


def stash_log_file(csv_output_folder, log_filename):
    '''Copy the log file into the output folder'''
    if os.path.isfile(log_filename):
        os.remove(log_filename)
    full_stashed_graph_filename = csv_output_folder + '\\' + log_filename + '.log'
    with open('run.log', 'r') as log_input_file:
        content = log_input_file.read()
        with open(full_stashed_graph_filename, 'wt') as stashed_log_output_file:
            stashed_log_output_file.write(content)


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
    elif palette_name == 'Category10':
        return Category10
    elif palette_name == 'Dark2':
        return Dark2
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


def filter_property_buckets(sorted_property_buckets: Dict, cut_off_value: int):
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


def get_buckets(sorted_buckets_list: List, sorted_property_buckets: Dict) -> Dict:
    '''
    Split numbers into buckets by a given property

    The first bucket contains numbers with one property value
    The next bucket contains X times more property values than the previous one
    X is determined so that the palette can cover all property values
    '''

    global palette_color_range

    number_of_unassigned_buckets = len(sorted_buckets_list)
    palette_color_range = get_number_of_colors_in_palette(palette=palette)
    bucket_base = get_bucket_base(palette_color_range, number_of_unassigned_buckets)
    logger.info(f'Buckets to be distributed: {number_of_unassigned_buckets}')
    logger.info(f'Base chosen: {bucket_base}')
    number_of_binary_buckets = get_power_of_n(number_of_unassigned_buckets, base=bucket_base)

    # create binary bucket index map
    binary_bucket_index_map = {}
    binary_buckets = {}

    for counter in range(number_of_binary_buckets + 1):
        bucket_count = pow(bucket_base, counter)
        binary_bucket_index = counter
        binary_buckets[binary_bucket_index] = []
        filtered_property_bucket, sorted_property_buckets = filter_property_buckets(sorted_property_buckets, bucket_count)
        if len(filtered_property_bucket) > 0:
            binary_buckets[binary_bucket_index].extend(filtered_property_bucket)
            binary_bucket_index_map[binary_bucket_index] = []
            binary_bucket_index_map[binary_bucket_index].extend(sorted_buckets_list[:bucket_count])
            sorted_buckets_list = sorted_buckets_list[bucket_count:]
        else:
            binary_buckets.pop(binary_bucket_index)


    return binary_buckets


def get_binary_bucket_index(property: int, binary_bucket_index_map: Dict) -> int:
    '''
    Get the index of the binary bucket by property
    '''

    for bucket_index, property_list in binary_bucket_index_map.items():
        if property in property_list:
            return bucket_index
    raise Exception(f'Property {property} not found in binary_bucket_index_map')


def get_power_of_n(value: int, base: int):
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


def get_property_buckets(number_list: List, parameter: str, use_rounding: str = 'full') -> Tuple:
    '''
    Split numbers into buckets, based in the provided parameter
    '''

    buckets_list = []
    param_buckets = {}
    for number in number_list:
        if number.is_prime and not include_primes:
            continue
        else:
            try:
                property = getattr(number, parameter)
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




def prep_output_folder(folder_name: str):
    '''
    Prepare folder for output csv files
    '''

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        return
    else:
        if cfg.run.reset_output_data:
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


def get_colour_bucket_index(binary_buckets: Dict, value: int) -> int:
    '''
    Get the index of the binary bucket that a number in
    '''

    for index, numbers in binary_buckets.items():
        for number in numbers:
            if value == number.value:
                return str(index)


def generate_timestamp():
    '''
    Generate timestamp string, depending on the desired granularity, set in config.toml
    '''

    timestamp_format = ''
    timestamp_granularity = cfg.run.hard_copy_timestamp_granularity
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


def generate_number_list(lowerbound: str = 2, upperbound: str = 10, families_filter: list[int] = []):
    '''
    Generate a list of Number objects
    '''

    families_filter_counter = []
    filter_families_string = [str(item) for item in families_filter]
    if len(families_filter) > 0:
        families_filter_counter = [0 for item in families_filter]
    number_list = []
    with Bar('Generating numbers', max=(upperbound - lowerbound + 1)) as bar:
        for value in range(lowerbound, upperbound + 1):
            bar.next()

            # exclude primes
            if not include_primes and pp.isprime(value):
                continue
            
            division_family = 1
            # exclude number if it fails the families filter
            if len(families_filter) > 0:
                calculate_division_family = False
                division_family = Number.get_division_family(value)
                if not division_family in families_filter:
                    continue
            else:
                calculate_division_family = True

            number = Number(value=value, division_family=division_family, calculate_division_family=calculate_division_family)

            number_list.append(number)
            if len(families_filter) > 0:
                filter_index = families_filter.index(division_family)
                families_filter_counter[filter_index] += 1

    if len(families_filter) > 0:
        if families_filter_counter.count(0) == len(families_filter_counter):
            logger.info(f"None of the generated numbers belong to families [ {', '.join(filter_families_string)} ]")
        else:
            for index, item in enumerate(families_filter):
                logger.info(f"Numbers count in family {item}: {families_filter_counter[index]}")


    return number_list


if __name__ == "__main__":
    run(lowerbound=lowerbound, upperbound=upperbound)
