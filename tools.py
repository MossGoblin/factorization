from configparser import ConfigParser
from bokeh.palettes import Turbo


class SettingsHolder():
    def __init__(self, config_file='config.ini') -> None:
        self.config_file = config_file
        self.config = ConfigParser()
        self.read_settings(self.config_file)

    def read_settings(self, config_file='config.ini'):
        if not config_file:
            config_file = self.config_file
        self.config.read(self.config_file)

        # RANGE
        self.lowerbound = int(self.config.get('range', 'lowerbound'))
        self.upperbound = int(self.config.get('range', 'upperbound'))

        # RUN
        self.create_csv = self.config.get('run', 'crate_csv')
        self.hard_copy_timestamp_granularity = int(self.config.get('run', 'hard_copy_timestamp_granularity'))
        self.reset_output_data = True if self.config.get(
            'run', 'reset_output_data') == 'true' else False
        self.include_primes = True if self.config.get(
            'run', 'include_primes') == 'true' else False

        # GRAPH
        self.graph_mode = self.config.get('graph', 'mode')
        self.graph_width = int(self.config.get('graph', 'width'))
        self.graph_height = int(self.config.get('graph', 'height'))
        self.graph_point_size = int(self.config.get('graph', 'point_size'))
        self.use_bucket_colorization = True if self.config.get(
            'graph', 'use_color_buckets') == 'true' else False
        self.palette = Turbo
        self.palette_name = self.config.get('graph', 'palette')