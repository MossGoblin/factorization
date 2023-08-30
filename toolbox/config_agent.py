from configparser import ConfigParser

class ConfigCategory():
    def __init__(self, category_name: str):
        self.name = category_name



class ConfigAgent():
    """
        A class used to load a config file

        For each config category an instance of ConfigCategory() is created as a class attribute of ConfigAgent

        Each parameter in a category is set a class attribute of the corresponding ConfigCategory()
        ...

        Attributes
        ----------
        config_path : str
            full file path for the config file
        config : ConfigParser
            an instance of ConfigParser used to load and parse the config file
        
        [loaded_parameters] : [variable]
            parameters loaded from the config file

        Methods
        -------
        get_config()
            Returns the instance of ConfigParser used by the ConfigAgent
        """

    def __init__(self, 
                 config_path: str, 
                 autocast: bool = True, 
                 strict_autocast: bool = True,
                 category_prefix: str = ''):
        """
        Parameters
        ----------
        config_path : str
            The full path of the config file
        autocast : bool, optional
            If True, the ConfigAgent tries to cast each parameter to a type (default is True)
        strict_autocast : bool, optional
            If True and autocast == True, failing to cast a parameter raises an Exception (default is True)
        category_prefix : bool, optional
            If True the names of the category objects will be prefixed by the passed string (default is an empty string)
        """
        self.config_path = config_path
        self.config = ConfigParser()
        self._read_data(autocast, strict_autocast, category_prefix)


    def get_config(self) -> ConfigParser:
        return self.config

    def _read_data(self, autocast, strict_autocast: bool, category_prefix: str):
        self.config.read(self.config_path)
        for section in self.config.sections():
            section_name = category_prefix + '_' + section if category_prefix != '' else section
            new_section = ConfigCategory(section_name)
            for parameter in self.config[section]:
                    if autocast:
                        try:
                            parameter_value = self._try_cast(self.config[section][parameter])
                        except Exception as e:
                            if strict_autocast:
                                raise Exception (f'Autocast failed: {e}')
                            else:
                                pass
                    else:
                        parameter_value = self.config[section][parameter]
                    setattr(new_section, parameter, parameter_value)
            setattr(self, section_name, new_section)

    def _try_cast(self, param: str):
        try:
            cast_param = int(param)
            if cast_param != None:
                return cast_param
            else:
                pass
        except Exception as e:
            pass

        try:
            cast_param = float(param)
            if cast_param:
                return cast_param
            else:
                pass
        except Exception as e:
            pass
    
        try:
            if param.lower() not in ['true', 'false']:
                pass
            else:
                if param.lower() == 'true':
                    return True
                else:
                    return False
        except Exception as e:
            pass
    
        try:
            cast_param_list_string = param
            cast_param_list_string = cast_param_list_string.replace(' ', '')
            cast_param = [int(item) for item in cast_param_list_string.split(",")]
            if cast_param:
                return cast_param
            else:
                pass
        except Exception as e:
            pass
        
        cast_param = param
        
        if cast_param:
            return cast_param
        else:
            raise f'Could not cast {param}'