# Proceso de discriminacion por compatibilidad

Este proceso analiza a todos los recursos (archivos) de codigo fuente, en busqueda de detectar la compatibilidad del mismo con una plataforma (sistema operativo) o arquitectura (procesador) objetivos.

## Analisis

Se utiliza la etiqueta (@Marcado de etiquetas) **__PLATFORM_COMPATIBILITY__**, y **__ARCHITECTURE_COMPATIBILITY__** para esta validacion; si el archivo aprueba la validacion, se incluye dentro del codigo fuente final, en caso contrario es descartado

## Carpetas

Si una carpeta contiene un archivo **__init__**, se maneja la carpeta y todo su contenido como un **modulo**: en este caso, si el archivo **__init__** no aprueba la validacion, TODOS sus archivos y carpetas son omitidos y no incluidos en el codigo fuente final; en caso de aprobar la validacion, se procede a validar cada sub-archivo y sub-carpeta de manera individual

# Proceso de discriminacion por seleccion

Este proceso permite al usuario escoger de manera selectiva los elementos del software. Si es escogido, se incluye en la construccion del software; en caso contrario es descartado.

## Archivos

Para un archivo, la seleccion involucra que sea integrado directamente en la construccion del software

## Carpetas

Para una carpeta, la seleccion involucra que la carpeta misma sea integrada: si sus archivos indican explicitamente que pueden ser seleccionables, entonces se permite la especificacion individual para decidir si se incluyen o no.

# Proceso de prevision de configuraciones

Este proceso permite que, el usuario pueda proporcionar dinamicamente (de forma interactiva) configuraciones solicitadas y descritas detalladamente por un elemento del software. 

El recurso debe utilizar la etiqueta: **__CONFIGURABLE__** (@Marcado de etiquetas) para indicar que soporta esto, y debe describir en una estructura JSON (```dict```) un descriptor serializado de tipo ```Configurations``` (libreria: ```configurations-stc```) sus configuraciones. Asimismo debera incluir su nombre de elemento en la etiqueta: **__ELEMENT_NAME__**, ya que con ella seran indexadas sus configuraciones, y podra localizarlas en el deposito de configuraciones.

> Esto nos permite instanciar un objeto ```Configurations``` - ```configurations-stc``` - a partir de las configuraciones serializadas, rico en datos y metodos de alto nivel para su manipulacion, y asimismo serializar en formato compatible (```JSON```/```dict```) las configuraciones resultantes para su almacenamiento.

Las configuraciones provistas durante la fase de preparacion del software seran estaticas. Se podrian entender como configuraciones basicas, iniciales, o de arranque.

El descriptor estatico de configuraciones del elemento sera recuperado desde la variable constante: **__STATIC_CONFIGURATIONS__**, y las configuraciones resultantes seran almacenadas en el deposito de configuraciones definido.

## Archivos

Para un archivo, las configuraciones provistas se interpretan como individuales para el mismo.

## Carpetas

Si una carpeta contiene un archivo **__init__**, se entiende que se trata de un modulo, y que las configuraciones provistas son generales para este modulo.

## Almacenamiento

Las configuraciones estaticas generadas, seran almacenadas en un archivo de codigo fuente: ```configurations.py``` (ruta: ```link/shared/configurations.py```), mismo que sera incluido durante el empaquetamiento y compilacion del archivo binario de programa ejecutable.

Desde este recurso, todos los elementos del software que hayan registrado sus configuraciones estaticas (que en caso de ser indicadas, seran obligatorias), podran recuperarlas utilizando su nombre: descrito en su propia etiqueta **__ELEMENT_NAME__** como forma de indexacion.

# Dependencias

## Especificacion de dependencia

El mecanismo permite la especificacion de dependencias mediante la etiqueta **__REQUIRES__**, que utiliza una notacion anidable y de punto (como: ```system.install.modules.persistence_windows```), que permite una identificacion y trazabilidad exacta. 

Gracias a este mecanismo, se puede saber que elementos son necesarios, y detectar situaciones de corrupcion de dependencias para evitar generar copias de software no funcionales.

# Filtramiento de residuos

El constructor de software filtrara automaticamente recursos residuales como:
- **__pycache__**
- **.pyc**

Para evitar incluir elementos inutiles en la copia de software final.