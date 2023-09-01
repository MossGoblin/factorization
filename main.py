import collections
import math
import os
from datetime import datetime

import pandas as pd
from progress.bar import Bar

import toolbox.logger_service as logger_service
import toolbox.mappings as mappings
from toolbox.bokeh_agent import Bokeh_Agent
from toolbox.config_agent import ConfigAgent
from toolbox.number import Number
from toolbox.utils import (
    generate_number_list,
    generate_timestamp,
    get_bucket_base,
    get_factors,
    get_number_of_colors_in_palette,
    get_palette,
    get_power_of_n,
    int_list_to_str,
    prep_output_folder,
    split_prime_factors,
)


project_title = 'Factorization'

output_file_name = 'main.html'
output_file_title = project_title
logger_file_name = 'run.log'
config_file_name = 'config.toml'

logger = logger_service.get_logger(logger_file_name)
cfg = ConfigAgent(config_path=config_file_name)

lowerbound = cfg.range.lowerbound
upperbound = cfg.range.upperbound

# RUN parameters
include_primes = cfg.run.include_primes
create_csv = cfg.run.create_csv

# GRAPH parameters
use_bucket_colorization = cfg.graph.use_color_buckets
use_bucket_colorization = cfg.graph.use_color_buckets
palette_name = cfg.graph.palette
graph_mode = cfg.graph.visualization_mode
colorization_mode = cfg.graph.colorization_mode
if colorization_mode == 'default':
    colorization_mode = graph_mode
property_rounding = cfg.graph.property_rounding
full_antislope_display = cfg.graph.full_antislope_display
graph_point_size = cfg.graph.point_size
try:
    families_filter = cfg.filter.families
except AttributeError:
    families_filter = []

x_axis = 'number'
y_axis = mappings.y_axis_values[graph_mode]
palette_color_range = 0
CSV_OUTPUT_FOLDER = 'output'


def collate_date(number_list: list[Number], palette):
    if use_bucket_colorization:
        # [x] separate numbers into binary buckets by closest integer to a given property
        # [x] get primary slope buckets
        buckets_list, property_buckets = get_property_buckets(number_list, parameter = colorization_mode, use_rounding = property_rounding)

        # [x] pour numbers into binary buckets
        sorted_property_buckets = collections.OrderedDict(sorted(property_buckets.items()))
        sorted_buckets_list = sorted(buckets_list)
        binary_buckets = get_buckets(sorted_buckets_list, sorted_property_buckets, palette)

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

    return binary_buckets, data_dict


def create_graph_params(data_dict: dict, binary_buckets: dict, palette):
    if use_bucket_colorization:
        number_of_colors = len(binary_buckets)
    plot_width = cfg.graph.width
    plot_height = cfg.graph.height
    family_filter_text = " All families."
    if len(families_filter) > 0 and len(families_filter) <= 5:
        family_filter_text = " Families: " + ", ".join([str(family) for family in families_filter]) + "."
    elif len(families_filter) > 0:
        family_filter_text = " Families: " + "...".join([str(families_filter[0]), str(families_filter[-1])]) + "."
    primes_included_text = " Primes included" if include_primes else " Primes excluded."

    graph_params = {}
    graph_params['output_file_path'] = output_file_name
    graph_params['output_file_title'] = output_file_title
    graph_params['title'] = mappings.graph_title[graph_mode].format(
        data_dict['number'][0], data_dict['number'][-1]) + family_filter_text + primes_included_text
    graph_params['y_axis_label'] = mappings.y_axis_label[graph_mode]
    graph_params['width'] = plot_width
    graph_params['height'] = plot_height
    graph_params['use_bucket_colorization'] = use_bucket_colorization
    graph_params['number_of_colors'] = number_of_colors
    graph_params['factors_list'] = get_factors(number_of_colors)
    graph_params['palette'] = palette
    graph_params['point_size'] = graph_point_size
    graph_params['x_axis'] = x_axis
    graph_params['y_axis'] = y_axis

    return graph_params


def create_plot_tooltips():
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
    
    return tooltips


def create_colorization(graph_params: dict) -> (list[int], str):
    '''
    Creates a scatter plot by given parameters
    '''

    coloring = ''
    use_bucket_colorization = graph_params['use_bucket_colorization']
    if use_bucket_colorization:
        number_of_colors_required = graph_params['number_of_colors']
        factors_list = graph_params['factors_list']
    palette = graph_params['palette']

    if use_bucket_colorization and number_of_colors_required <= palette_color_range:
        factors_list = get_factors(number_of_colors_required)
        requested_number_of_colors = number_of_colors_required
        if not number_of_colors_required in palette:
            number_of_colors_required = list(palette)[-1]
        if requested_number_of_colors != number_of_colors_required:
            logger.info(f'{requested_number_of_colors} colors unavailable. {number_of_colors_required} color buckets created')
        else:
            logger.info(f'{number_of_colors_required} color buckets created')
        coloring = palette_name.lower()
    elif number_of_colors_required > palette_color_range:
        logger.info(f'Base coloring - {number_of_colors_required} colors exceeds palette range')
        coloring = 'monocolor'
    else:
        logger.info('Base coloring - bucket colorization disabled')
        coloring = 'monocolor'

    return factors_list, coloring


def visualize_data(number_list: list[Number], palette):
    '''
    Prepares the generated number data and uses it to create the visualization
    '''
    
    # plot
    plot = Bokeh_Agent()

    # data
    binary_buckets, data_dict = collate_date(number_list, palette)
    data_df = pd.DataFrame(data_dict)
    data_df.reset_index()
    plot.set_data(data_df)
    logger.info(f'Data collated')    

    # graph parameters
    graph_params = create_graph_params(data_dict, binary_buckets, palette)
    plot.set_params(graph_params)
    logger.debug('Graph params collated')

    # coloring
    color_factors, coloring = create_colorization(graph_params)
    plot.set_color_factors(color_factors)
    logger.debug('Color factors set')

    # tooltips
    tooltips = create_plot_tooltips()
    plot.set_tooltips(tooltips)
    logger.debug('Tooltips set')

    # generate plot
    plot.generate()
    logger.info('Graph generated')

    # [x] show
    plot.display_graph()

    return data_df, coloring


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


def filter_property_buckets(sorted_property_buckets: dict, cut_off_value: int):
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


def get_buckets(sorted_buckets_list: list, sorted_property_buckets: dict, palette) -> dict:
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


def get_binary_bucket_index(property: int, binary_bucket_index_map: dict) -> int:
    '''
    Get the index of the binary bucket by property
    '''

    for bucket_index, property_list in binary_bucket_index_map.items():
        if property in property_list:
            return bucket_index
        
    raise Exception(f'Property {property} not found in binary_bucket_index_map')


def get_property_buckets(number_list: list, parameter: str, use_rounding: str = 'full') -> (list[int], dict):
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


def get_colour_bucket_index(binary_buckets: dict, value: int) -> int:
    '''
    Get the index of the binary bucket that a number in
    '''
    for index, numbers in binary_buckets.items():
        for number in numbers:
            if value == number.value:
                return str(index)


def create_hard_copies(data_df, coloring):
    # [x] 'hard copy'
    graph_mode_chunk = mappings.graph_mode_filename_chunk[graph_mode]
    timestamp_format = generate_timestamp(cfg.run.hard_copy_timestamp_granularity)
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
        prep_output_folder(CSV_OUTPUT_FOLDER, cfg.run.reset_output_data)
        data_df.to_csv(path + full_hard_copy_filename)
        logger.info(f'Data saved as output\full_hard_copy_filename')

    return full_hard_copy_filename


def init_log(start: datetime.time):
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


def run(lowerbound=2, upperbound=10):
    # logger dump
    start = datetime.now()
    init_log(start)

    # prepate plot data
    palette = get_palette(palette_name=palette_name)

    number_list = generate_number_list(logger, cfg, lowerbound=lowerbound, upperbound=upperbound, families_filter=families_filter)
    if len(number_list) == 0:
        logger.info(f'No composites generated. Terminating the program.')
        end = datetime.now()
        logger.info(f'End at {end}')
        logger.info(f'Total time: {end-start}')
        quit()
    logger.info(f'Numbers iterated {lowerbound}..{upperbound}')
    logger.info(f'Total composites: {len(number_list)}')

    # create plot
    data_df, coloring = visualize_data(number_list, palette)

    # create_hard_copy
    hard_copy_filename = create_hard_copies(data_df, coloring)

    end = datetime.now()
    logger.info(f'End at {end}')
    logger.info(f'Total time: {end-start}')
 
    stash_graph_html(CSV_OUTPUT_FOLDER, hard_copy_filename)
    stash_log_file(CSV_OUTPUT_FOLDER, hard_copy_filename)


if __name__ == "__main__":
    run(lowerbound=lowerbound, upperbound=upperbound)
