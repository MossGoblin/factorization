from configparser import ConfigParser
import toml


class ConfigCategory():
    def __init__(self, category_name: str):
        self.name = category_name

class ConfigAgent():
    """
        A class used to load a timl config file

        For each config category an instance of ConfigCategory() is created as a class attribute of ConfigAgent

        Each parameter in a category is set a class attribute of the corresponding ConfigCategory()
        ...

        Attributes
        ----------
        config_path : str
            full file path for the config file
        config : ConfigParser
            a dictionary of values, as read with toml
        
        [loaded_parameters] : [variable]
            parameters loaded from the config file

        Methods
        -------
        get_config()
            Returns the dictionary as read with toml
        """

    def __init__(self, 
                 config_path: str, 
                 category_prefix: str = ''):
        """
        Parameters
        ----------
        config_path : str
            The full path of the config file
        category_prefix : bool, optional
            If True the names of the category objects will be prefixed by the passed string (default is an empty string)
        """
        self.config_path = config_path
        self._read_data(category_prefix)


    def get_config(self) -> ConfigParser:
        return self.config

    def _read_data(self, category_prefix: str):
        self.config = toml.load(self.config_path)
        for section in self.config.items():
            section_name = category_prefix + '_' + section[0] if category_prefix != '' else section[0]
            new_section = ConfigCategory(section_name)
            for parameter in section[1]:
                    parameter_value = section[1][parameter]
                    setattr(new_section, parameter, parameter_value)
            setattr(self, section_name, new_section)