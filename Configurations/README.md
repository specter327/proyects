# Presentacion

**Configurations** es una libreria que proporciona una manera abstracta y rica para manejar configuraciones, estructuradas como un conjunto de **ajustes** compuestos. Hace uso de la libreria **DataValue** y sus clases **PrimitiveData** y **ComplexData** para ofrecer una definicion fuertemente estructurada y rigida para una validacion robusta.

Donde **Configurations** provee una representacion completa, cada **Setting** presenta un contexto de cada ajuste, y cada **DataValue** aplica validacion estricta de valores. Ademas, se ofrecen funciones de serializacion para la normalizacion, almacenamiento y transporte de datos entre sistemas.

# Uso
Su uso es tan simple como:
1. Importar configuraciones
```python
from configurations import Configurations
```

2. Importar ajustes
```python
from configurations import Setting
```

3. Definir ajustes
```python
# Library import
from datavalue import PrimitiveData

# Data definition
data = PrimitiveData(
  data_type=str,
  value=None,
  maximum_length=10, minimum_length=1,
  possible_values=None,
  regular_expression=None,
  data_class=True
)

# Setting field definition
setting = Setting(
  value=data, # Debera cumplir con el esquema definido por **PrimitiveData**
  system_name="SETTING", # Nombre con el cual sera accedido por el sistema
  symbolic_name="Ajuste", # Nombre simbolico legible para el ajuste (representativo)
  description="Descripcion del ajuste", # Descripcion del ajuste (descriptivo)
  optional=False # Indicacion de ajuste opcional/obligatorio
)
```

4. Definir configuraciones
```python
# Create configurations instance
configurations = Configurations()

# Add settings to the configurations instance
configurations.add_setting(setting)
```

5. Utilizar
```python
# Show configurations requirements
configurations.to_dict()
```

# Casos de uso

La libreria permite la descripcion de configuraciones ricas y estructuradas, ademas de la normalizacion y serializacion para su presentacion y transporte. Permite elaborar configuraciones completas para cualquier uso, como:

1. **Descripcion de APIs**: Utilizable para describir datos en APIs, y tambien para su validacion de envio/recepcion
2. **Descripcion de configuraciones**: Utilizable para describir configuraciones de dispositivos, o sistemas
3. **Definicion de politicas**: Como politicas de seguridad, control de permisos, perfiles de usuario, etcetera

# Dependencias
Depende de la libreria **DataValue**