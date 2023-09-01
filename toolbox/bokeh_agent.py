from bokeh.plotting import figure, show
from bokeh import models as models
from bokeh.models import ColumnDataSource, CategoricalColorMapper
from bokeh.palettes import Turbo, Magma, Inferno, Plasma, Viridis, Cividis, Category10, Dark2, Palette

import pandas as pd


class Bokeh_Agent():

    def __init__(self, data: pd.DataFrame = None, params: dict = None, tooltips: list = None, color_factors: list[str] = None):
        self.data = data
        self.params = params
        self.tooltips = tooltips
        self.color_factors = color_factors
        self.figure = None


    def set_data(self, dataframe: pd.DataFrame):
        self.data = dataframe


    def set_params(self, params: dict):
        self.params = params


    def set_tooltips(self, tooltips: list):
        self.tooltips = tooltips

    
    def set_color_factors(self, color_factors: list):
        self.color_factors = color_factors

    
    def create_figure(self) -> figure:
        '''
        Returns a figure with the provided parameters
        '''
        title = self.params['title']
        y_axis_label = self.params['y_axis_label']
        width = self.params['width']
        height = self.params['height']

        return figure(title=title, x_axis_label='number', y_axis_label=y_axis_label, width=width, height=height)


    def get_palette(self, palette_name: str) -> Palette:
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


    def display_graph(self):
        show(self.figure)


    def create_graph(self):
        x_value = self.params['x_axis']
        y_value = self.params['y_axis']
        palette = self.get_palette(self.params['palette'])
        graph_point_size = self.params['point_size']
        color_mapper = CategoricalColorMapper(factors=self.color_factors, palette=palette[11])
        data = ColumnDataSource(data=self.data)

        self.figure.scatter(source=data, x=x_value, y=y_value, color={'field': 'color_bucket', 'transform': color_mapper}, size=graph_point_size)
        hover = models.HoverTool(tooltips=self.tooltips)
        self.figure.add_tools(hover)
        

    def generate(self) -> None:
        '''
        Returns a figure with the provided parameters
        '''
        if self.data.empty == True:
            raise Exception ('Dataframe not set')
        if self.params == None:
            raise Exception ('Graph params not set')
        if self.tooltips == None:
            raise Exception ('Tooltips not set')
        if self.color_factors == None:
            raise Exception ('Color factors not set')
        
        title = self.params['title']
        y_axis_label = self.params['y_axis_label']
        width = self.params['width']
        height = self.params['height']

        self.figure = figure(title=title, x_axis_label='number', y_axis_label=y_axis_label, width=width, height=height)

        hover = models.HoverTool(tooltips=self.tooltips)
        self.figure.add_tools(hover)

        self.create_graph()