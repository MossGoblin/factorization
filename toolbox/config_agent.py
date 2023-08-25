from configparser import ConfigParser


class ConfigAgent():
    """
        A class used to load a config file

        A class attribute is created for each parameter from the config file

            If autocast is set to True, the ConfigAgent tries to cast each variable in the following order:

            int, float, bool, list[int]

            If none of the casts succeeds, the parameter type defaults to string
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
                 autocast: bool = False, 
                 hierarchical_names: bool = True,
                 strict_autocast: bool = False, 
                 overwrite: bool = True):
        """
        Parameters
        ----------
        config_path : str
            The full path of the config file
        autocast : bool, optional
            If True, the ConfigAgent tries to cast each parameter to a type (default is False)
        hierarchical_names : bool, optional
            If True, the class attribute names are created as [section]_[parameter] (default is True)
        strict_autocast : bool, optional
            If True and autocast == True, failing to cast a parameter raises an Exception (default is False)
        overwrite : bool, optional
            If True and autocast == True, cast parameters replace non-cast ones; otherwise a duplicate set with the prefix 'cast_' is created (default is True)
        """
        self.config_path = config_path
        self.config = ConfigParser()
        self._read_data(hierarchical_names)
        if autocast:
            self._cast_content(strict_autocast, hierarchical_names, overwrite)

    def get_config(self) -> ConfigParser:
        return self.config

    def _read_data(self, hierarchical_names: bool) -> None:
        self.config.read(self.config_path)
        for section in self.config.sections():
            for parameter in self.config[section]:
                if hierarchical_names:
                    field_name = "_".join([section, parameter])
                else:
                    field_name = parameter
                setattr(self, field_name, self.config[section][parameter])

    def _cast_content(self, strict_autocast: bool, hierarchical_names: bool, overwrite: bool):
        for section in self.config.sections():
            for parameter in self.config[section]:
                try:
                    cast_param = self._try_cast(self.config[section][parameter])
                    if hierarchical_names:
                        prefix = "_".join([section, parameter])
                    else:
                        prefix = parameter
                    if overwrite:
                        field_name = prefix
                    else:
                        field_name = "_".join(['cast', prefix])
                    setattr(self, field_name, cast_param)
                except Exception as e:
                    if strict_autocast:
                        raise Exception (f'Autocast failed: {e}')
                    else:
                        pass

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