# Labels
__RESOURCE_TYPE__ = "STRUCTURAL"

# Library import
import sys
import os

# Constants definition
ConfigurationsTable = {   'shared.communication_architecture.layers.communication.modules.client': {   'SERVER_PROFILES': {   'DESCRIPTION': 'It '
                                                                                                                       'includes '
                                                                                                                       'a '
                                                                                                                       'list '
                                                                                                                       'of '
                                                                                                                       'ServerProfile '
                                                                                                                       'instances, '
                                                                                                                       'with '
                                                                                                                       'information '
                                                                                                                       'to '
                                                                                                                       'search '
                                                                                                                       'it '
                                                                                                                       'to '
                                                                                                                       'establish '
                                                                                                                       'a '
                                                                                                                       'connection',
                                                                                                        'OPTIONAL': False,
                                                                                                        'PRIVATE': False,
                                                                                                        'SYMBOLIC_NAME': 'Server '
                                                                                                                         'profiles',
                                                                                                        'SYSTEM_NAME': 'SERVER_PROFILES',
                                                                                                        'VALUE': {   'DATA_CLASS': True,
                                                                                                                     'DATA_TYPE': 'dict',
                                                                                                                     'MAXIMUM_LENGTH': None,
                                                                                                                     'MINIMUM_LENGTH': None,
                                                                                                                     'POSSIBLE_VALUES': [   [   'TRANSPORT',
                                                                                                                                                'ADDRESSES'],
                                                                                                                                            [   'INTERNET',
                                                                                                                                                'BLUETOOTH',
                                                                                                                                                'SERIAL',
                                                                                                                                                {   '__type__': 'ComplexData',
                                                                                                                                                    'content': {   'DATA_CLASS': True,
                                                                                                                                                                   'DATA_TYPE': 'list',
                                                                                                                                                                   'MAXIMUM_LENGTH': None,
                                                                                                                                                                   'MINIMUM_LENGTH': 1,
                                                                                                                                                                   'POSSIBLE_VALUES': [   {   '__type__': 'ComplexData',
                                                                                                                                                                                              'content': {   'DATA_CLASS': True,
                                                                                                                                                                                                             'DATA_TYPE': 'dict',
                                                                                                                                                                                                             'MAXIMUM_LENGTH': None,
                                                                                                                                                                                                             'MINIMUM_LENGTH': 1,
                                                                                                                                                                                                             'POSSIBLE_VALUES': [   [   'ADDRESS',
                                                                                                                                                                                                                                        'PORT'],
                                                                                                                                                                                                                                    [   {   '__type__': 'PrimitiveData',
                                                                                                                                                                                                                                            'content': {   'DATA_CLASS': True,
                                                                                                                                                                                                                                                           'DATA_TYPE': 'str',
                                                                                                                                                                                                                                                           'MAXIMUM_LENGTH': None,
                                                                                                                                                                                                                                                           'MAXIMUM_SIZE': 15,
                                                                                                                                                                                                                                                           'MINIMUM_LENGTH': None,
                                                                                                                                                                                                                                                           'MINIMUM_SIZE': 7,
                                                                                                                                                                                                                                                           'POSSIBLE_VALUES': None,
                                                                                                                                                                                                                                                           'REGULAR_EXPRESSION': '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
                                                                                                                                                                                                                                                           'VALUE': None,
                                                                                                                                                                                                                                                           '__type__': 'PrimitiveData'}},
                                                                                                                                                                                                                                        {   '__type__': 'PrimitiveData',
                                                                                                                                                                                                                                            'content': {   'DATA_CLASS': True,
                                                                                                                                                                                                                                                           'DATA_TYPE': 'str',
                                                                                                                                                                                                                                                           'MAXIMUM_LENGTH': None,
                                                                                                                                                                                                                                                           'MAXIMUM_SIZE': 39,
                                                                                                                                                                                                                                                           'MINIMUM_LENGTH': None,
                                                                                                                                                                                                                                                           'MINIMUM_SIZE': 2,
                                                                                                                                                                                                                                                           'POSSIBLE_VALUES': None,
                                                                                                                                                                                                                                                           'REGULAR_EXPRESSION': '^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$',
                                                                                                                                                                                                                                                           'VALUE': None,
                                                                                                                                                                                                                                                           '__type__': 'PrimitiveData'}},
                                                                                                                                                                                                                                        {   '__type__': 'PrimitiveData',
                                                                                                                                                                                                                                            'content': {   'DATA_CLASS': True,
                                                                                                                                                                                                                                                           'DATA_TYPE': 'str',
                                                                                                                                                                                                                                                           'MAXIMUM_LENGTH': None,
                                                                                                                                                                                                                                                           'MAXIMUM_SIZE': 17,
                                                                                                                                                                                                                                                           'MINIMUM_LENGTH': None,
                                                                                                                                                                                                                                                           'MINIMUM_SIZE': 17,
                                                                                                                                                                                                                                                           'POSSIBLE_VALUES': None,
                                                                                                                                                                                                                                                           'REGULAR_EXPRESSION': '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$',
                                                                                                                                                                                                                                                           'VALUE': None,
                                                                                                                                                                                                                                                           '__type__': 'PrimitiveData'}},
                                                                                                                                                                                                                                        {   '__type__': 'PrimitiveData',
                                                                                                                                                                                                                                            'content': {   'DATA_CLASS': True,
                                                                                                                                                                                                                                                           'DATA_TYPE': 'str',
                                                                                                                                                                                                                                                           'MAXIMUM_LENGTH': None,
                                                                                                                                                                                                                                                           'MAXIMUM_SIZE': None,
                                                                                                                                                                                                                                                           'MINIMUM_LENGTH': None,
                                                                                                                                                                                                                                                           'MINIMUM_SIZE': None,
                                                                                                                                                                                                                                                           'POSSIBLE_VALUES': None,
                                                                                                                                                                                                                                                           'REGULAR_EXPRESSION': '^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\\.)+[a-zA-Z]{2,}$',
                                                                                                                                                                                                                                                           'VALUE': None,
                                                                                                                                                                                                                                                           '__type__': 'PrimitiveData'}},
                                                                                                                                                                                                                                        {   '__type__': 'PrimitiveData',
                                                                                                                                                                                                                                            'content': {   'DATA_CLASS': True,
                                                                                                                                                                                                                                                           'DATA_TYPE': 'int',
                                                                                                                                                                                                                                                           'MAXIMUM_LENGTH': 65535,
                                                                                                                                                                                                                                                           'MAXIMUM_SIZE': None,
                                                                                                                                                                                                                                                           'MINIMUM_LENGTH': 1,
                                                                                                                                                                                                                                                           'MINIMUM_SIZE': None,
                                                                                                                                                                                                                                                           'POSSIBLE_VALUES': None,
                                                                                                                                                                                                                                                           'REGULAR_EXPRESSION': None,
                                                                                                                                                                                                                                                           'VALUE': None,
                                                                                                                                                                                                                                                           '__type__': 'PrimitiveData'}}]],
                                                                                                                                                                                                             'VALUE': None,
                                                                                                                                                                                                             '__type__': 'ComplexData'}}],
                                                                                                                                                                   'VALUE': None,
                                                                                                                                                                   '__type__': 'ComplexData'}}]],
                                                                                                                     'VALUE': {   'ADDRESSES': 'BLUETOOTH',
                                                                                                                                  'TRANSPORT': 'INTERNET'},
                                                                                                                     '__type__': 'ComplexData'}}},
    'system.install.modules.persistence_crontab_linux': {   'EXECUTION_INTERVAL': {   'DESCRIPTION': 'Specify the '
                                                                                                     'interval between '
                                                                                                     'executions of '
                                                                                                     'the software',
                                                                                      'OPTIONAL': False,
                                                                                      'PRIVATE': False,
                                                                                      'SYMBOLIC_NAME': 'Execution '
                                                                                                       'interval',
                                                                                      'SYSTEM_NAME': 'EXECUTION_INTERVAL',
                                                                                      'VALUE': {   'DATA_CLASS': True,
                                                                                                   'DATA_TYPE': 'int',
                                                                                                   'MAXIMUM_LENGTH': None,
                                                                                                   'MAXIMUM_SIZE': None,
                                                                                                   'MINIMUM_LENGTH': 0,
                                                                                                   'MINIMUM_SIZE': None,
                                                                                                   'POSSIBLE_VALUES': None,
                                                                                                   'REGULAR_EXPRESSION': None,
                                                                                                   'VALUE': 100,
                                                                                                   '__type__': 'PrimitiveData'}}}}
    
# Classes definition
class ConfigurationsManager:
    _instance = None

    def __new__(cls):
        """Implementación de Singleton para acceso global único."""
        if cls._instance is None:
            cls._instance = super(ConfigurationsManager, cls).__new__(cls)
            # Al inicializarse, ya tiene acceso a la tabla inyectada
            cls._instance._table = ConfigurationsTable
        return cls._instance

    def query_configuration(self, element_name: str) -> dict:
        """Recupera la configuración de un elemento por su identificador único."""
        return self._table.get(element_name, {})

    def get_all(self) -> dict:
        """Retorna la base de datos completa de configuración."""
        return self._table
