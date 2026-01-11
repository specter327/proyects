# Presentacion
## Objetivo
Sparky es una herramienta que esta dirigida a facilitar la personalizacion de textos con estructuras de datos de alto nivel, y de manera simple.

## Funcionamiento
Esta herramienta utiliza "tokens", o claves unicas contenidas por simbolos especiales: {{CLAVE}}, que permiten especificar de manera univoca donde se deben colocar los datos. Por ejemplo: {{USER.PASSWORD}}

Gracias al uso de tablas de datos anidables en formato JSON, es muy facil y de alto nivel crear una plantilla, definir la estructura de datos, y generar la personalizacion

## Casos de uso
Se puede utilizar para textos de cualquier tamaño, con estructuras de datos de cualquier tamaño. Por ejemplo, para mensajes personalizados con informacion individual:

## Ejemplo
Texto (plantilla):

¡Hola {{USER.FULL_NAME}}! Bienvenido de nuevo al sistema.

Nombre de usuario: {{USER.USERNAME}}
Contraseña: {{USER.PASSWORD}}
Correo electronico: {{USER.CONTACT.EMAIL}}
Numero telefonico: {{USER.CONTACT.PHONE_NUMBER}}
Servicio disponible: {{SERVICE.STATUS}}

Tabla de datos:
{
    "USER":{
        "FULL_NAME":"Sparky",
        "USERNAME":"Sparky_user",
        "PASSWORD":"Sparky_password",
        "CONTACT":{
            "EMAIL":"sparkyemail@domain.com",
            "PHONE_NUMBER":"1234567890"
        }
    },
    
    "SERVICE":{
        "STATUS":"AVAILABLE"
    }
}

Resultado de personalizacion:

¡Hola Sparky! Bienvenido de nuevo al sistema.

Nombre de usuario: Sparky_user
Contraseña: Sparky_password
Correo electronico: sparkyemail@domain.com
Numero telefonico: 1234567890
Servicio disponible: AVAILABLE

# Uso
## Codigo

### Importar las clases de trabajo
>>> from src.data.classes import Text, PersonalizeProfile

### Definir datos
>>> text_content = "Your text with {{USER.NAME}} and other {{KEYS}} with the described syntax"
>>> data_table = {"USER":{"NAME":"Sparky"}}

### Crear las instancias de trabajo
>>> text = Text(text_content)
>>> personalizer = PersonalizeProfile(data_table)

### Personalizar y usar texto
>>> personalized_text = personalizer.personalize_text(text)
>>> print(personalized_text)
Your text with Sparky and other {{KEYS}} with the described syntax

## Uso en CLI
### Con archivo (recomendado)
>>> python ./sparky.py --text "Username: {{USER.NAME}} | Password: {{USER.CREDENTIALS.PASSWORD}} \nService status: {{SERVICE.STATUS}}\nAccount signed up: {{ACCOUNT.SIGNED_UP}}" --profile-file ./data_probe.json
Username: Sparky | Password: Sparky1234 \nService status: Available\nAccount signed up: 27/06/2026

### Sin archivo: directo
