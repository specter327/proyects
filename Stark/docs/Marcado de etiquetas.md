# Marcado por etiquetas

El mecanismo define las siguientes etiquetas de **archivo**:
**__RESOURCE_TYPE__**: Puede tener dos valores:
    **```"STRUCTURAL"```**: Indica que el recurso es estructural, y siempre se incluira durante la construccion del software. Debe ser multiplataforma y agnostico, abstracto o general.
    **```"DYNAMIC"```**: Indica que el recurso es dinamico, y estara sujeto a la aprobacion mediante la evaluacion para su inclusion durante la construccion del software. Puede ser multiplataforma o no, y puede estar especializado.

**__PLATFORM_COMPATIBILTY__**: Puede tener uno, varios, o todos los valores (multiplataforma).
    **```"WINDOWS"```**: Indica compatibilidad con el sistema operativo Windows.
    **```"GNU/LINUX"```**: Indica compatibilidad con el sistema operativo GNU/Linux.
    **```"MACOS"```**: Indica compatibilidad con el sistema operativo MacOS.
    **```ALL```**: Indica compatibilidad con todas las plataformas.

**__ARCHITECTURE_COMPATIBILITY__**: Puede tener uno, varios, o todos los valores (multiplataforma):
    **```"ARM"```**: Indica compatibilidad con procesadores de arquitectura ARM.
    **```"X32"```**: Indica compatibilidad con procesadores de arquitectura de 32 bits.
    **```"X64"```**: Indica compatibilidad con procesadores de arquitectura de 64 bits.
    **```ALL```**: Indica compatibilidad con todas las arquitecturas.

**__SELECTABLE__**: Indica si el recurso es seleccionable por el usuario durante la fase de construccion del software. Puede tener dos valores:
    **```True```**: Es seleccionable durante la fase de construccion.
    **```False```**: No es seleccionable durante la fase de construccion.

**__ELEMENT_NAME__**: Indica el nombre simbolico (representativo) del elemento.

**__CONFIGURABLE__**: Indica si el recurso puede ser configurado de manera estatica durante la fase de construccion; estas configuraciones seran empaquetadas y de arranque. Puede tener dos valores:
    **```True```**
    **```False```**

**__STATIC_CONFIGURATIONS__**: Indica las configuraciones del elemento utilizando un descriptor de configuraciones estandar (**configurations-stc**), y se serializa con un diccionario (```dict```)

**__REQUIRES__**: Indica los elementos requeridos por el elemento actual.