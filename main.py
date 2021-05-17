from configparser import ConfigParser
from bokeh.plotting import figure, show
from bokeh import models as models
from bokeh.models import ColumnDataSource, CategoricalColorMapper
import logging
from typing import List
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


def run(lowerbound=2, upperbound=10):
    # [x] iterate between bounds and cache numbers
    number_list = generate_number_list(
        lowerbound=lowerbound, upperbound=upperbound)
    logger.info(f'Numbers generated {lowerbound}..{upperbound}')

    # [...] split data
    running_maximum_deviation = 0
    for number in number_list:
        deviation = number.mean_deviation
        if deviation > running_maximum_deviation:
            number.first_row = True
            running_maximum_deviation = deviation

    # [...] create visualization
    create_visualization(number_list)


def create_visualization(number_list: List[Number]):
    # [ ] prep vis data
    # prep x-axis and y-axix
    data_dict = {}
    data_dict['number'] = []
    data_dict['is_prime'] = []
    data_dict['prime_factors'] = []
    data_dict['mean'] = []
    data_dict['deviation'] = []
    data_dict['slope'] = []
    data_dict['first_row'] = []
    for number in number_list:
        data_dict['number'].append(number.value)
        data_dict['is_prime'].append('true' if number.is_prime else 'false')
        data_dict['prime_factors'].append(number.prime_factors)
        data_dict['mean'].append(number.prime_mean)
        data_dict['deviation'].append(number.mean_deviation)
        data_dict['slope'].append(number.slope)
        data_dict['first_row'].append('true' if number.first_row else 'false')

    data_df = pd.DataFrame(data_dict)
    data_df.reset_index()
    data = ColumnDataSource(data=data_df)

    # [x] create plot
    plot_width = 1600
    plot_height = 900
    graph = figure(title=f"Mean prime factor deviations for numbers {data_dict['number'][0]} to {data_dict['number'][-1]}",
                   x_axis_label='number', y_axis_label='mean prime factor deviation', width=plot_width, height=plot_height)

    # [...] add hover tool
    hover = models.HoverTool(tooltips=[('number', '@number'),
                                       ('prime', '@is_prime'),
                                       ('factors', '@prime_factors'),
                                       ('mean factor value', '@mean'),
                                       ('mean factor deviation', '@deviation'),
                                       ('slope', '@slope')])
    graph.add_tools(hover)

    # [] colorize by type
    prime_color = config.get('graph', 'prime_color')
    composite_color = config.get('graph', 'composite_color')
    first_row_color = config.get('graph', 'first_row_color')
    unmarked_color = config.get('graph', 'unmarked_color')
    color_mapper = CategoricalColorMapper(factors=['true', 'false'], palette=[first_row_color, unmarked_color]
                                          )

    # [x] add graph
    # graph.scatter(source=data, x='number', y='deviation', color="#386CB0", size=5)
    graph.scatter(source=data, x='number', y='deviation', color={
                  'field': 'first_row', 'transform': color_mapper}, size=5)

    # [x] show
    show(graph)


def int_list_to_str(number_list: List[int], separator=', '):
    stringified_list = []
    for number in number_list:
        stringified_list.append(str(number))

    return separator.join(stringified_list)


def generate_number_list(lowerbound=2, upperbound=10):
    number_list = []
    for value in range(lowerbound, upperbound + 1):
        number = Number(value=value)
        number_list.append(number)
    return number_list


if __name__ == "__main__":
    run(lowerbound=lowerbound, upperbound=upperbound)
