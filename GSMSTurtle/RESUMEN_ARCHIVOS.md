# Resumen de Archivos - GSMSTurtle v2

Este documento describe cada archivo del proyecto GSMSTurtle versión 2, su función y cómo se relacionan entre sí para construir la aplicación.

## Estructura General del Proyecto

GSMSTurtle v2 es un framework Python diseñado para gestionar y controlar dispositivos GSM (módems, módulos celulares) de manera estandarizada. La arquitectura está basada en contratos (interfaces) que permiten abstraer las operaciones con dispositivos GSM.

---

## Archivos de Documentación

### `ARQUITECTURA.md`
**Ubicación**: Raíz del proyecto  
**Función**: Documentación técnica completa de la arquitectura del proyecto. Describe:
- Resumen general del framework
- Estructura del proyecto
- Arquitectura por capas
- Patrones de diseño utilizados
- Flujo de trabajo típico
- Estado actual del proyecto
- Dependencias externas

**Relación**: Proporciona contexto arquitectónico para entender cómo funcionan todos los demás archivos.

### `README.md`
**Ubicación**: Raíz del proyecto  
**Función**: Archivo de documentación principal del proyecto (actualmente vacío, reservado para información general del proyecto).

---

## Punto de Entrada Principal

### `gsmsturtle.py`
**Ubicación**: Raíz del proyecto  
**Función**: Punto de entrada principal de la aplicación (actualmente vacío).  
**Estado**: Pendiente de implementación. Debería contener la inicialización y configuración principal del framework.

**Relación**: Sería el archivo que los usuarios importarían para usar el framework completo.

---

## Módulo Principal (`src/`)

### `src/__init__.py`
**Ubicación**: `src/`  
**Función**: Archivo de inicialización del paquete principal (actualmente vacío).  
**Relación**: Permite que `src` sea reconocido como un paquete Python y puede exportar las clases principales del framework.

---

## Capa de Contratos (`src/contracts/`)

La capa de contratos define los estándares e interfaces que deben seguir todas las implementaciones concretas.

### Clases de Datos (`src/contracts/data_classes/`)

#### `src/contracts/data_classes/__init__.py`
**Función**: Inicialización del módulo de clases de datos (vacío).  
**Relación**: Permite importar las clases de datos desde este módulo.

#### `src/contracts/data_classes/primitive_data.py`
**Función**: Clase base para validación de datos primitivos.  
**Características principales**:
- Validación de tipo de dato (str, int, float, bool, None)
- Validación de longitud mínima/máxima
- Validación de valores posibles (enum-like)
- Sistema de metadatos extensible
- Métodos: `validate()`, `update()`, `append_metadata()`, `delete_metadata()`, `get_metadata()`, `query_metadata()`, `to_string()`

**Relaciones**:
- **Usado por**: `Message`, `PhoneNumber`, `Setting`, `SendSMSOperationResults`
- **Base para**: Todas las validaciones de datos en el sistema

#### `src/contracts/data_classes/message.py`
**Función**: Representa un mensaje SMS con validación.  
**Propiedades**:
- `content`: Contenido del mensaje (1-200 caracteres, validado por `PrimitiveData`)
- `timestamp`: Timestamp opcional del mensaje
- `type`: Tipo de mensaje (`TYPE_SENT` o `TYPE_RECEIVED`)

**Relaciones**:
- **Usa**: `PrimitiveData` para validar todas sus propiedades
- **Usado por**: `SendSMSOperationParameters` para encapsular el mensaje a enviar

#### `src/contracts/data_classes/phone_number.py`
**Función**: Representa un número de teléfono en formato estándar internacional (E164).  
**Características**:
- Utiliza la librería `phonenumbers` para validación
- Convierte a formato E164 estándar
- Lanza excepciones si el formato es inválido
- Longitud máxima de 50 caracteres

**Relaciones**:
- **Usa**: `PrimitiveData` para almacenar el número validado
- **Dependencia externa**: Librería `phonenumbers`
- **Usado por**: `SendSMSOperationParameters` para validar el número de destino

#### `src/contracts/data_classes/complex_data.py`
**Función**: Placeholder para futuras implementaciones de datos complejos.  
**Estado**: Vacío, reservado para futuras expansiones.  
**Relación**: Referenciado por `Setting` como posible tipo de valor.

---

### Controlador de Dispositivos (`src/contracts/device_controller/`)

#### `src/contracts/device_controller/__init__.py`
**Función**: Inicialización del módulo de controlador de dispositivos (vacío).  
**Relación**: Permite importar las clases del controlador desde este módulo.

#### `src/contracts/device_controller/device_controller.py`
**Función**: Define la interfaz abstracta (`DeviceControllerInterface`) que deben implementar todos los controladores de dispositivos GSM.  
**Características principales**:
- Clase abstracta (ABC) que define el contrato
- Propiedades: `configurations`, `properties`, `operations`, `capabilities`, `connection_status`, `device_status`, `connection_controller`
- Métodos abstractos requeridos:
  - `_identify()`: Identifica dispositivos potencialmente compatibles
  - `_detect(device)`: Verifica compatibilidad de un dispositivo
  - `recognize()`: Detecta dispositivos compatibles
  - `connect()`: Conecta con el dispositivo
  - `configure(configurations)`: Configura el dispositivo
  - `disconnect()`: Desconecta del dispositivo
  - `request_property(property)`: Solicita una propiedad del dispositivo
  - `request_operation(operation, parameters)`: Ejecuta una operación

**Relaciones**:
- **Usa**: `Configurations`, `constants`, `OperationParametersInterface`, `OperationResultsInterface`
- **Base para**: Todas las implementaciones concretas de controladores (aún no implementadas)

#### `src/contracts/device_controller/configurations.py`
**Función**: Gestiona un conjunto de configuraciones (settings) para un dispositivo.  
**Métodos**:
- `add_setting(setting)`: Agrega una configuración
- `query_settings()`: Lista nombres de configuraciones
- `query_setting(system_name)`: Obtiene una configuración específica
- `delete_setting(system_name)`: Elimina una configuración

**Relaciones**:
- **Usa**: `Setting` para almacenar configuraciones individuales
- **Usado por**: `DeviceControllerInterface` para gestionar la configuración del dispositivo

#### `src/contracts/device_controller/setting.py`
**Función**: Representa una configuración individual con valor y características.  
**Propiedades**:
- `system_name`: Nombre del sistema (en mayúsculas)
- `symbolic_name`: Nombre simbólico legible
- `description`: Descripción de la configuración
- `value`: Valor (puede ser `PrimitiveData` o `ComplexData`)
- `optional`: Indica si la configuración es opcional

**Métodos**:
- `to_dict()`: Serializa la configuración a diccionario

**Relaciones**:
- **Usa**: `PrimitiveData` o `ComplexData` para el valor
- **Usado por**: `Configurations` para almacenar configuraciones

#### `src/contracts/device_controller/constants.py`
**Función**: Define constantes de estado utilizadas en todo el sistema.  
**Constantes definidas**:
- `CONNECTED` / `DISCONNECTED`: Estados de conexión
- `AVAILABLE` / `UNAVAILABLE`: Estados del dispositivo
- `ERROR` / `SUCCESS`: Estados de operación

**Relaciones**:
- **Usado por**: `DeviceControllerInterface` para gestionar estados

---

### Operaciones (`src/contracts/operations/`)

#### `src/contracts/operations/__init__.py`
**Función**: Define las interfaces base para operaciones.  
**Contenido**:
- `OperationInterface`: Contrato que deben implementar todas las operaciones
  - Propiedades: `name`, `version`, `description`, `identification`
- `OperationParametersInterface`: Contrato para parámetros de operaciones
  - Método: `validate()`
- `OperationResultsInterface`: Contrato para resultados de operaciones

**Relaciones**:
- **Base para**: Todas las operaciones concretas (como `SendSMS`)
- **Usado por**: `DeviceControllerInterface` para definir el contrato de operaciones

#### `src/contracts/operations/send_sms.py`
**Función**: Implementa la operación estándar de envío de SMS.  
**Clases definidas**:
1. **`SendSMS`** (implementa `OperationInterface`):
   - Identificación: `"SEND_SMS"`
   - Versión: `"1"`
   - Descripción: "This operation allows to send a SMS message to a specified phone number destinatary"

2. **`SendSMSOperationParameters`** (implementa `OperationParametersInterface`):
   - `destinatary_phone_number`: Instancia de `PhoneNumber` (validada)
   - `message`: Instancia de `Message` (validada)
   - Método `validate()`: Valida los parámetros

3. **`SendSMSOperationResults`** (implementa `OperationResultsInterface`):
   - `send_result`: Resultado booleano del envío
   - `status_code`: Código de estado (0: SUCCESS, 1: UNKNOWN_ERROR)

**Relaciones**:
- **Usa**: `OperationInterface`, `OperationParametersInterface`, `OperationResultsInterface`
- **Usa**: `PhoneNumber` y `Message` para los parámetros
- **Usa**: `PrimitiveData` para validar los resultados
- **Usado por**: `DeviceControllerInterface.request_operation()` para ejecutar el envío de SMS

---

## Directorios Vacíos (Reservados para Futuras Implementaciones)

### `src/contracts/properties/`
**Función**: Reservado para el sistema de propiedades estándar de dispositivos GSM.  
**Estado**: Vacío, pendiente de implementación.

### `src/controllers/`
**Función**: Reservado para implementaciones concretas de `DeviceControllerInterface`.  
**Estado**: Vacío. Aquí irían controladores específicos como `SerialDeviceController`, `USBDeviceController`, etc.

### `src/data/`
**Función**: Reservado para estructuras de datos adicionales o persistencia.  
**Estado**: Vacío.

### `src/functions/`
**Función**: Reservado para funciones auxiliares y utilidades.  
**Estado**: Vacío.

### `src/interfaces/`
**Función**: Reservado para interfaces adicionales no relacionadas con contratos principales.  
**Estado**: Vacío.

### `src/system/`
**Función**: Reservado para componentes del sistema (logging, configuración global, etc.).  
**Estado**: Vacío.

### `docs/`
**Función**: Reservado para documentación adicional del proyecto.  
**Estado**: Vacío.

### `resources/`
**Función**: Reservado para recursos estáticos (imágenes, archivos de configuración, etc.).  
**Estado**: Vacío.

---

## Flujo de Relaciones y Construcción de la Aplicación

### 1. **Capa de Validación de Datos**
```
PrimitiveData (base)
    ↓
Message, PhoneNumber (datos del dominio)
    ↓
SendSMSOperationParameters, SendSMSOperationResults
```

### 2. **Capa de Configuración**
```
Setting (configuración individual)
    ↓
Configurations (conjunto de configuraciones)
    ↓
DeviceControllerInterface (usa configuraciones)
```

### 3. **Capa de Operaciones**
```
OperationInterface, OperationParametersInterface, OperationResultsInterface (contratos)
    ↓
SendSMS, SendSMSOperationParameters, SendSMSOperationResults (implementación concreta)
    ↓
DeviceControllerInterface.request_operation() (ejecuta operaciones)
```

### 4. **Flujo Completo de Uso**

```
1. Usuario crea Configurations
   └─> Agrega Settings (usando PrimitiveData o ComplexData)

2. Usuario instancia un DeviceControllerInterface concreto
   └─> Configura con Configurations
   └─> Conecta con connect()

3. Usuario crea parámetros de operación
   └─> SendSMSOperationParameters (usa PhoneNumber y Message)
   └─> PhoneNumber y Message validan usando PrimitiveData

4. Usuario ejecuta operación
   └─> DeviceControllerInterface.request_operation(SendSMS(), parámetros)
   └─> Retorna SendSMSOperationResults

5. Usuario desconecta
   └─> DeviceControllerInterface.disconnect()
```

---

## Dependencias Externas

- **`phonenumbers`**: Librería Python para validación y formato de números telefónicos internacionales
  - Usada por: `src/contracts/data_classes/phone_number.py`

---

## Patrones de Diseño Utilizados

1. **Patrón de Interfaz/Contrato**: Uso extensivo de ABC para definir contratos
2. **Patrón de Validación**: `PrimitiveData` actúa como wrapper validado
3. **Patrón de Factory/Builder**: `Configurations` permite construir configuraciones complejas
4. **Patrón de Estrategia**: `DeviceControllerInterface` permite diferentes estrategias de control

---

## Estado del Proyecto

### ✅ Implementado
- Sistema de validación de datos (`PrimitiveData`)
- Clases de datos del dominio (`Message`, `PhoneNumber`)
- Interfaces de operaciones (`OperationInterface`, `SendSMS`)
- Sistema de configuración (`Configurations`, `Setting`)
- Interfaz de controlador de dispositivos (`DeviceControllerInterface`)
- Constantes de estado

### 🚧 Pendiente
- Implementaciones concretas de `DeviceControllerInterface`
- Sistema de propiedades (`properties/`)
- `ComplexData` (actualmente placeholder)
- Punto de entrada principal (`gsmsturtle.py`)
- Implementaciones de resultados de operaciones adicionales
- Funciones auxiliares y utilidades

---

## Conclusión

El proyecto GSMSTurtle v2 está estructurado como un framework extensible basado en contratos. La separación clara entre:
- **Contratos** (interfaces y estándares)
- **Datos** (clases de dominio con validación)
- **Operaciones** (operaciones estándar)
- **Controladores** (interfaces para dispositivos)

Permite crear un sistema modular donde las implementaciones concretas pueden desarrollarse independientemente mientras mantienen compatibilidad con los contratos definidos. El sistema está preparado para crecer con nuevas operaciones, propiedades y controladores sin romper la compatibilidad existente.
