# Sparky - Herramienta de Personalización de Textos

## 📋 Presentación

**Sparky** es una herramienta ligera y potente diseñada para facilitar la personalización de textos mediante estructuras de datos de alto nivel de manera simple e intuitiva. Permite reemplazar tokens en plantillas de texto con valores provenientes de estructuras JSON anidadas, ideal para generar contenido personalizado de forma automatizada.

### 🎯 Objetivo

Sparky está dirigido a desarrolladores y usuarios que necesitan personalizar textos de manera sistemática, utilizando estructuras de datos complejas y anidadas. Es especialmente útil para:

- Generación de mensajes personalizados
- Creación de plantillas de correos electrónicos
- Personalización de documentos
- Automatización de comunicaciones
- Cualquier caso de uso que requiera reemplazo de tokens en texto

### ✨ Características Principales

- **Sintaxis simple**: Utiliza tokens con formato `{{CLAVE}}` para identificar puntos de reemplazo
- **Estructuras anidadas**: Soporta datos JSON complejos y anidados mediante notación de punto (ej: `{{USER.CONTACT.EMAIL}}`)
- **Interfaz dual**: Disponible tanto como herramienta CLI como biblioteca Python
- **Alto rendimiento**: Procesamiento eficiente de textos y estructuras de datos
- **Fácil integración**: API simple y clara para uso programático

## 🔧 Funcionamiento

### Concepto de Tokens

Sparky utiliza **tokens** o claves únicas contenidas por símbolos especiales: `{{CLAVE}}`, que permiten especificar de manera unívoca dónde se deben colocar los datos. Los tokens pueden referenciar valores anidados usando notación de punto.

**Ejemplo de tokens:**
- `{{USER.NAME}}` - Referencia simple
- `{{USER.CONTACT.EMAIL}}` - Referencia anidada
- `{{SERVICE.STATUS}}` - Referencia a otro objeto

### Proceso de Personalización

1. **Definir la plantilla**: Crear un texto con tokens `{{CLAVE}}`
2. **Estructurar los datos**: Organizar los datos en formato JSON con estructura anidada
3. **Normalizar el perfil**: Sparky convierte la estructura anidada en claves planas (ej: `USER.CONTACT.EMAIL`)
4. **Reemplazar tokens**: Se reemplazan todos los tokens encontrados con sus valores correspondientes

### Estructura de Datos

Gracias al uso de tablas de datos anidables en formato JSON, es muy fácil y de alto nivel crear una plantilla, definir la estructura de datos, y generar la personalización.

## 📚 Casos de Uso

Sparky se puede utilizar para textos de cualquier tamaño, con estructuras de datos de cualquier complejidad. Algunos ejemplos incluyen:

- **Mensajes personalizados** con información individual de usuarios
- **Plantillas de correo electrónico** con datos dinámicos
- **Documentos generados automáticamente** con información contextual
- **Notificaciones personalizadas** con datos del sistema
- **Reportes dinámicos** con información estructurada

## 💡 Ejemplo Básico

### Plantilla de Texto

```
¡Hola {{USER.FULL_NAME}}! Bienvenido de nuevo al sistema.

Nombre de usuario: {{USER.USERNAME}}
Contraseña: {{USER.PASSWORD}}
Correo electrónico: {{USER.CONTACT.EMAIL}}
Número telefónico: {{USER.CONTACT.PHONE_NUMBER}}
Servicio disponible: {{SERVICE.STATUS}}
```

### Tabla de Datos (JSON)

```json
{
    "USER": {
        "FULL_NAME": "Sparky",
        "USERNAME": "Sparky_user",
        "PASSWORD": "Sparky_password",
        "CONTACT": {
            "EMAIL": "sparkyemail@domain.com",
            "PHONE_NUMBER": "1234567890"
        }
    },
    "SERVICE": {
        "STATUS": "AVAILABLE"
    }
}
```

### Resultado Personalizado

```
¡Hola Sparky! Bienvenido de nuevo al sistema.

Nombre de usuario: Sparky_user
Contraseña: Sparky_password
Correo electrónico: sparkyemail@domain.com
Número telefónico: 1234567890
Servicio disponible: AVAILABLE
```

## 🚀 Instalación

Sparky es una herramienta Python que no requiere instalación adicional de dependencias externas. Solo necesitas:

1. Python 3.7 o superior
2. Clonar o descargar el proyecto
3. Ejecutar directamente los scripts

## 📖 Uso

### Uso Programático (Código)

#### Importar las clases de trabajo

```python
from src.interfaces.code import personalize_text
```

#### Definir datos

```python
text_content = "Your text with {{USER.NAME}} and other {{KEYS}} with the described syntax"
data_table = {"USER": {"NAME": "Sparky"}}
```

#### Personalizar y usar texto

```python
personalized_text = personalize_text(text_content, data_table)
print(personalized_text)
```

**Resultado:**
```
Your text with Sparky and other {{KEYS}} with the described syntax
```

> **Nota:** Los tokens que no tienen un valor correspondiente en el perfil de datos permanecen sin reemplazar.

### Uso en CLI

#### Con archivo JSON (Recomendado)

```bash
python ./sparky.py --text "Username: {{USER.NAME}} | Password: {{USER.CREDENTIALS.PASSWORD}}" --profile-file ./data_probe.json
```

#### Con JSON directo

```bash
python ./sparky.py --text "Hello {{USER.NAME}}!" --profile '{"USER":{"NAME":"Sparky"}}'
```

## 📁 Estructura del Proyecto

```
Sparky/
├── sparky.py              # Punto de entrada principal (CLI)
├── data_probe.json        # Archivo de ejemplo con datos
├── README.md              # Esta documentación
└── src/
    ├── data/
    │   └── classes.py      # Clases principales: Text y PersonalizeProfile
    ├── interfaces/
    │   └── cli.py          # Interfaz de línea de comandos
    └── functions/          # Funciones auxiliares (reservado)
```

## 🔍 API de Referencia

### Clase `Text`

Representa un texto editable con tokens de personalización.

**Métodos:**
- `query_tokens(tokens: List[str]) -> List[str]`: Identifica qué tokens de una lista están presentes en el texto

### Clase `PersonalizeProfile`

Representa un perfil de datos para personalización de texto.

**Propiedades de clase:**
- `KEY_PREFIX`: `"{{"` - Prefijo de los tokens
- `KEY_SUFFIX`: `"}}"` - Sufijo de los tokens
- `NOTATION_SEPARATOR`: `"."` - Separador para notación anidada

**Métodos:**
- `personalize_text(text: Text) -> str`: Personaliza un texto reemplazando todos los tokens encontrados

## 📝 Notas Importantes

- Los tokens deben usar la sintaxis exacta: `{{CLAVE}}` (con dobles llaves)
- La notación anidada usa punto (`.`) como separador
- Los valores se convierten a string durante el reemplazo
- Los tokens sin valor correspondiente permanecen sin reemplazar
- La estructura JSON puede tener cualquier nivel de anidación

## 📄 Licencia

Ver archivo LICENSE en el directorio raíz del proyecto.
