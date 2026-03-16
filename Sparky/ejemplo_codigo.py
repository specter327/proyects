#!/usr/bin/env python3
# ============================================================================
# DEMOSTRACIÓN DE USO DE SPARKY - INTERFAZ DE CÓDIGO
# ============================================================================
# Este script demuestra cómo usar Sparky programáticamente desde Python
# con diferentes escenarios y casos de uso.

from src.data.classes import Text, PersonalizeProfile
import json

def print_separator(title: str):
    """Imprime un separador visual para organizar los ejemplos."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def ejemplo_1_basico():
    """Ejemplo 1: Personalización básica de texto."""
    print_separator("Ejemplo 1: Personalización Básica")
    
    # Definir el texto con tokens
    texto_plantilla = "¡Hola {{USER.NAME}}! Tu contraseña es: {{USER.CREDENTIALS.PASSWORD}}"
    
    # Definir los datos de personalización
    datos = {
        "USER": {
            "NAME": "Sparky",
            "CREDENTIALS": {
                "PASSWORD": "Sparky1234"
            }
        }
    }
    
    # Crear instancias
    texto = Text(texto_plantilla)
    perfil = PersonalizeProfile(datos)
    
    # Personalizar
    resultado = perfil.personalize_text(texto)
    
    print("Texto original:")
    print(texto_plantilla)
    print("\nDatos de personalización:")
    print(json.dumps(datos, indent=2, ensure_ascii=False))
    print("\nResultado personalizado:")
    print(resultado)


def ejemplo_2_multiple_secciones():
    """Ejemplo 2: Personalización con múltiples secciones de datos."""
    print_separator("Ejemplo 2: Múltiples Secciones")
    
    texto_plantilla = """Usuario: {{USER.NAME}}
Contraseña: {{USER.CREDENTIALS.PASSWORD}}
Estado del servicio: {{SERVICE.STATUS}}
Fecha de registro: {{ACCOUNT.SIGNED_UP}}"""
    
    datos = {
        "USER": {
            "NAME": "Sparky",
            "CREDENTIALS": {
                "PASSWORD": "Sparky1234"
            }
        },
        "SERVICE": {
            "STATUS": "Available"
        },
        "ACCOUNT": {
            "SIGNED_UP": "27/06/2026"
        }
    }
    
    texto = Text(texto_plantilla)
    perfil = PersonalizeProfile(datos)
    resultado = perfil.personalize_text(texto)
    
    print("Texto original:")
    print(texto_plantilla)
    print("\nDatos de personalización:")
    print(json.dumps(datos, indent=2, ensure_ascii=False))
    print("\nResultado personalizado:")
    print(resultado)


def ejemplo_3_correo_electronico():
    """Ejemplo 3: Plantilla de correo electrónico personalizado."""
    print_separator("Ejemplo 3: Plantilla de Correo Electrónico")
    
    texto_plantilla = """Estimado {{CLIENTE.NOMBRE}},

Le informamos que su pedido #{{PEDIDO.NUMERO}} ha sido procesado exitosamente.

Detalles del pedido:
- Producto: {{PEDIDO.PRODUCTO}}
- Cantidad: {{PEDIDO.CANTIDAD}}
- Precio total: {{PEDIDO.PRECIO}} {{PEDIDO.MONEDA}}

Su pedido será enviado a:
{{CLIENTE.DIRECCION.CALLE}}, {{CLIENTE.DIRECCION.CIUDAD}}

Gracias por su compra.
Equipo de Ventas"""
    
    datos = {
        "CLIENTE": {
            "NOMBRE": "María González",
            "DIRECCION": {
                "CALLE": "Av. Principal 123",
                "CIUDAD": "Madrid"
            }
        },
        "PEDIDO": {
            "NUMERO": "ORD-2024-001",
            "PRODUCTO": "Laptop Pro",
            "CANTIDAD": 1,
            "PRECIO": 1299.99,
            "MONEDA": "EUR"
        }
    }
    
    texto = Text(texto_plantilla)
    perfil = PersonalizeProfile(datos)
    resultado = perfil.personalize_text(texto)
    
    print("Texto original (plantilla de correo):")
    print(texto_plantilla)
    print("\nDatos de personalización:")
    print(json.dumps(datos, indent=2, ensure_ascii=False))
    print("\nResultado personalizado:")
    print(resultado)


def ejemplo_4_estructura_compleja():
    """Ejemplo 4: Estructura de datos compleja con múltiples niveles."""
    print_separator("Ejemplo 4: Estructura Compleja")
    
    texto_plantilla = """=== Sistema de Gestión ===

Usuario: {{USUARIO.NOMBRE_COMPLETO}}
ID: {{USUARIO.ID}}
Email: {{USUARIO.CONTACTO.EMAIL}}
Teléfono: {{USUARIO.CONTACTO.TELEFONO}}

Configuración:
- Idioma: {{CONFIG.IDIOMA}}
- Zona horaria: {{CONFIG.TIEMPO.ZONA}}
- Formato de fecha: {{CONFIG.TIEMPO.FORMATO_FECHA}}

Último acceso: {{SESION.ULTIMO_ACCESO}}
Estado: {{SESION.ESTADO}}"""
    
    datos = {
        "USUARIO": {
            "NOMBRE_COMPLETO": "Carlos Rodríguez",
            "ID": "USR-001",
            "CONTACTO": {
                "EMAIL": "carlos.rodriguez@example.com",
                "TELEFONO": "+34 600 123 456"
            }
        },
        "CONFIG": {
            "IDIOMA": "español",
            "TIEMPO": {
                "ZONA": "Europe/Madrid",
                "FORMATO_FECHA": "DD/MM/YYYY"
            }
        },
        "SESION": {
            "ULTIMO_ACCESO": "2024-01-15 14:30:00",
            "ESTADO": "Activa"
        }
    }
    
    texto = Text(texto_plantilla)
    perfil = PersonalizeProfile(datos)
    resultado = perfil.personalize_text(texto)
    
    print("Texto original:")
    print(texto_plantilla)
    print("\nDatos de personalización:")
    print(json.dumps(datos, indent=2, ensure_ascii=False))
    print("\nResultado personalizado:")
    print(resultado)


def ejemplo_5_desde_archivo():
    """Ejemplo 5: Cargar datos desde un archivo JSON."""
    print_separator("Ejemplo 5: Carga desde Archivo JSON")
    
    try:
        # Cargar datos desde el archivo de ejemplo
        with open("data_probe.json", "r", encoding="utf-8") as f:
            datos = json.load(f)
        
        texto_plantilla = """Bienvenido al sistema, {{USER.NAME}}!

Tus credenciales de acceso:
- Usuario: {{USER.NAME}}
- Contraseña: {{USER.CREDENTIALS.PASSWORD}}

Estado del servicio: {{SERVICE.STATUS}}
Fecha de registro: {{ACCOUNT.SIGNED_UP}}"""
        
        texto = Text(texto_plantilla)
        perfil = PersonalizeProfile(datos)
        resultado = perfil.personalize_text(texto)
        
        print("Texto original:")
        print(texto_plantilla)
        print("\nDatos cargados desde data_probe.json:")
        print(json.dumps(datos, indent=2, ensure_ascii=False))
        print("\nResultado personalizado:")
        print(resultado)
        
    except FileNotFoundError:
        print("⚠️  Archivo data_probe.json no encontrado.")
        print("Este ejemplo requiere el archivo de datos de ejemplo.")


def ejemplo_6_query_tokens():
    """Ejemplo 6: Consultar qué tokens están presentes en el texto."""
    print_separator("Ejemplo 6: Consulta de Tokens")
    
    texto_plantilla = "Hola {{USER.NAME}}, tu email es {{USER.EMAIL}} y tu teléfono es {{USER.PHONE}}"
    
    # Lista de tokens posibles
    tokens_posibles = [
        "{{USER.NAME}}",
        "{{USER.EMAIL}}",
        "{{USER.PHONE}}",
        "{{USER.ADDRESS}}",
        "{{ADMIN.NAME}}"
    ]
    
    texto = Text(texto_plantilla)
    tokens_presentes = texto.query_tokens(tokens_posibles)
    
    print("Texto original:")
    print(texto_plantilla)
    print("\nTokens posibles:")
    for token in tokens_posibles:
        print(f"  - {token}")
    print("\nTokens presentes en el texto:")
    for token in tokens_presentes:
        print(f"  ✓ {token}")


def ejemplo_7_tokens_sin_reemplazo():
    """Ejemplo 7: Comportamiento con tokens sin valor correspondiente."""
    print_separator("Ejemplo 7: Tokens sin Reemplazo")
    
    texto_plantilla = "Hola {{USER.NAME}}, tu código es {{USER.CODE}} y tu nivel es {{USER.LEVEL}}"
    
    # Datos incompletos (falta USER.LEVEL)
    datos = {
        "USER": {
            "NAME": "Ana",
            "CODE": "ABC123"
            # USER.LEVEL no está definido
        }
    }
    
    texto = Text(texto_plantilla)
    perfil = PersonalizeProfile(datos)
    resultado = perfil.personalize_text(texto)
    
    print("Texto original:")
    print(texto_plantilla)
    print("\nDatos de personalización (incompletos):")
    print(json.dumps(datos, indent=2, ensure_ascii=False))
    print("\nResultado personalizado:")
    print(resultado)
    print("\n⚠️  Nota: El token {{USER.LEVEL}} permanece sin reemplazar")
    print("    porque no tiene un valor correspondiente en los datos.")


def main():
    """Función principal que ejecuta todos los ejemplos."""
    print("\n" + "=" * 60)
    print("  SPARKY - Demostración de Interfaz de Código")
    print("=" * 60)
    
    # Ejecutar todos los ejemplos
    ejemplo_1_basico()
    ejemplo_2_multiple_secciones()
    ejemplo_3_correo_electronico()
    ejemplo_4_estructura_compleja()
    ejemplo_5_desde_archivo()
    ejemplo_6_query_tokens()
    ejemplo_7_tokens_sin_reemplazo()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("  ✅ Demostración Completada")
    print("=" * 60)
    print("\nEstos ejemplos muestran las capacidades de Sparky:")
    print("  • Personalización básica de textos")
    print("  • Múltiples secciones de datos")
    print("  • Estructuras de datos anidadas")
    print("  • Carga desde archivos JSON")
    print("  • Consulta de tokens presentes")
    print("  • Manejo de tokens sin reemplazo")
    print("\nPara más información, consulta el README.md\n")


if __name__ == "__main__":
    main()
