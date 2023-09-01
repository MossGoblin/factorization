import os

import pyprimes as pp
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
from progress.bar import Bar

from toolbox.number import Number


def get_palette(palette_name: str) -> dict:
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


def generate_number_list(logger, config, lowerbound: str = 2, upperbound: str = 10, families_filter: list[int] = []):
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
            if not config.run.include_primes and pp.isprime(value):
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


def get_number_of_colors_in_palette(palette: dict):
    '''
    Get the maximum number of colors, supported by the palette
    '''
    # HERE
    count = sorted(palette.keys())[-1]
    return count


def split_prime_factors(int_list: list[int]) -> int:
    sorted_int_list = sorted(int_list)
    
    return sorted_int_list[:-1], sorted_int_list[-1]


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


def prep_output_folder(folder_name: str, reset_output_data: bool):
    '''
    Prepare folder for output csv files
    '''

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
        return
    else:
        if reset_output_data:
            for root, directories, files in os.walk(folder_name):
                for file in files:
                    file_path = root + '/' + file
                    os.remove(file_path)
        return


def get_factors(number_of_colors: int) -> list:
    '''
    Compile the factors of a number as a list of strings
    '''

    factors_list = []
    for index in range(number_of_colors):
        factors_list.append(str(index))

    return factors_list


def int_list_to_str(number_list: list[int], separator=', ', use_bookends=True, bookends=['[ ', ' ]']):
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

def generate_timestamp(timestamp_granularity):
    '''
    Generate timestamp string, depending on the desired granularity, set in config.toml
    '''

    timestamp_format = ''
    format_chunks = ['%d%m%Y', '_%H', '%M', '%S']
    for chunk_index in range(timestamp_granularity + 1):
        timestamp_format += format_chunks[chunk_index]
    return timestamp_format

