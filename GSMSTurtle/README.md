# Presentacion

**GSMSTurtle** es una aplicacion de comunicacion textual (simple) tipo mensajeria por medio de SMS dirigido a computadores portatiles/escritorio con sistemas operativos:

- Windows (plataforma NT)
- GNU/Linux (plataforma POSIX)
- MacOS (plataforma POSIX)

Que tiene la finalidad de proporcionar un medio de comunicacion por computadora, utilizable por agentes humanos, o sistemas automaticos.

# Capacidades

Gracias a su arquitectura, es una aplicacion robusta, flexible, adaptativa y escalable. Puede disponer de varias interfaces:

- API
- Codigo (libreria importable)
- CLI
- GUI
- Web

Ademas de tratarse de un sistema de comunicacion general, es altamente extensible en dispositivos de comunicacion gracias al diseño y uso de una plataforma estandar. De esta forma, se pueden utilizar desde dispositivos fisicos como modulos GSM, o servicios digitales como Twilio, Vonage, o SMSGate de la misma forma.

# Casos de uso
## Estación de trabajo (uso personal)

GSMSTurtle transforma una estación de trabajo (portatil/escritorio) convencional en una terminal de telecomunicaciones SMS robusta. Gracias a su HAL (Capa de Abstracción de Hardware), el usuario puede integrar hardware físico estándar de manera agnostica.

- Integración de hardware: Soporte plug-and-play para módems GSM/GPRS (serie SIM800, SIM7600, etc.) mediante USB/UART.
- Gestión de identidad: Operación transparente utilizando la tarjeta SIM local, permitiendo el envío/recepción de SMS directamente desde el entorno de escritorio.
- Potencial de voz: En dispositivos con soporte de audio digital (PCM/I2S), el sistema sienta las bases para actuar como softphone mediante interfaces virtuales.
- Integración con servicios en la nube: Para entornos sin hardware dedicado, el sistema abstrae proveedores de telefonía en la nube (como Twilio, o Vonage) o pasarelas Android-HTTP (como SMSGate), tratándolos como "dispositivos virtuales" bajo la misma API unificada.

## Automatización e IoT
Diseñado para la ejecución en entornos sin interfaz grafica, y sistemas embebidos de bajos recursos (por ejemplo: Raspberry Pi, u Orange Pi):

- Sistemas de alerta: Disparo de notificaciones SMS críticas ante eventos de sensores físicos o virtuales.
- Domótica avanzada: Control y monitoreo remoto de infraestructuras residenciales sin depender de conexión a internet, utilizando la red GSM como canal de respaldo seguro.
- Orquestación: Integración sencilla mediante CLI o API con scripts de automatización (por ejemplo: Python, Bash, u otros).

## Infraestructura Empresarial
La arquitectura modular y persistente de la aplicacion la habilita como backend para procesos de negocio críticos:

- Notificaciones transaccionales: Envío masivo de OTPs, confirmaciones de pedidos o alertas de servicio al cliente.
- Integración CRM/ERP: Conexión directa entre sistemas de gestión empresarial y redes móviles para campañas de marketing o seguimiento.
- Alta disponibilidad: Capacidad de gestionar múltiples módems en paralelo para balanceo de carga en el envío de mensajes.

# Caracteristicas

## Controladores - Capa de abstraccion de hardware
Presenta un diseño de arquitectura modular. Utiliza un esquema de abstraccion de hardware (HAL) mediante controladores estandar, permitiendo asi transformar la variabilidad en uniformidad; asi mismo, opera con:

- Operaciones
- Propiedades
- Eventos

Estandar, de manera que el comportamiento es exactamente el mismo a traves de distintos dispositivos, totalmente agnostico al hardware/software subyacente.

## Nucleo - Centralizacion y orquestacion
El nucleo proporciona un elemento de control central que permite gestionar y orquestar todos los dispositivos conectados mediante sus controladores de software.

Ofrece funciones de un nivel medio, como:

- Sistema de notificacion de eventos
- Identificacion de dispositivos
- Deteccion de dispositivos
- Carga dinamica de controladores

Sirviendo como una interfaz media hacia el hardware.

## Sistema de Aplicacion
Encargado de proporcionar todas las funcionalidades de una aplicacion de comunicacion. Proporciona:

- Funciones de alto nivel
- Almacenamiento en bases de datos
- Identificacion de hardware
- Estructuracion y organizacion de conversaciones por dispositivo
- Historiales
- Registros
- Configuraciones
- Sistemas de soporte: actualizacion de datos, recepcion de mensajes, etc.
- Sistema de notificaciones

Tambien se asegura persistencia, e integridad de datos.

## Interfaz
De manera que, la interfaz es tan simple como:

- Visualizar, configurar, y conectar dispositivos (fisicos o virtuales)
- Configurar nuestro sistema: preferencias, archivados, bloqueos, etc.
- Establecer conversaciones: enviar y recibir mensajes
