# Arquitectura

La aplicacion esta compuesta por una arquitectura por capas, presentando las siguientes capas:
```
     Interfaz
        |
Sistema de aplicacion
        |
      Nucleo
        |
   Controladores
        |
     Hardware
```

Cada capa es abstracta; se encarga de sus propios cargos y responsabilidades, interactuando con la capa subyacente, y proporcionando una interfaz controlada para las capas superiores.

## Capa de Hardware

Esta capa es donde se implementan los dispositivos de comunicacion finales. Se pueden implementar dispositivos categorizados de forma general como:

- Fisicos: tales como un celular, modem GSM/GPRS, etcetera
- Virtuales: tales como servicios digitales como Twilio, Vonage, SMSGate, o enrutadores GSM

Cada dispositivo presenta sus propios datos, y funciones, capacidades y limitaciones. Ademas, el control de estos varia de uno a otro (p. Ej: algunos mediante el estandar AT, otros mediante APIs web)

Aqui los datos se transmiten mediante una comunicacion serial, Bluetooth, virtual (emulado), o por Internet (TCP/UDP)

## Capa de Controladores

En esta capa se implementan controladores de software que controlan la conexion a bajo nivel con el dispositivo en hardware (esta puede ser serial, o en red), se encargan de la comunicacion e instruccion con el dispositivo, y convierten operaciones estandar a operaciones particulares para cada hardware diferente. Estan diseñados a medida para el modelo de dispositivo en particular

Esta capa ofrece una interfaz estandar y uniforme a la capa superior. Todas las propiedades para un dispositivo estan bien definidas, y las operaciones junto con sus parametros y resultados tambien; asi, cada dispositivo intenta proporcionar todo lo que puede, y lo que puede proporcionar lo entrega siguiendo la normativa del estandar, de manera que la variabilidad se transforma en uniformidad

Aqui se implementan funciones como:
- connect
- disconnect
- configure
- request_property
- request_operation
- recognize

Tambien se implementa una sub-capa, denominada: "TransportLayer", la capa de transporte se encarga de normalizar la escritura y lectura de informacion sobre un medio de transporte, sea. Internet (TCP/UDP), serial, o Bluetooh (por ejemplo)

*Para dispositivos AT, se implementa un motor AT, que se encarga de gestionar la interaccion sincronica de: comando -> respuesta, pero tambien la interaccion asincronica de eventos URC, manejando eficientemente un canal de comunicacion reservado

## Capa de Nucleo

Esta capa se encarga principalmente de la organizacion, centralizacion y soporte para los dispositivos conectados mediante sus controladores. Ofrece una capa de acceso intermedio para la capa superior, y proporciona datos y funciones de alto nivel

Esta capa proporciona funciones como:
- connect_device
- disconnect_device
- request_operation
- request_property
- subscribe_event

## Capa de Sistema de Aplicacion

Esta capa se encarga de implementar todos los sistemas, logica, datos y funciones de una aplicacion de comunicacion textual por mensajeria mediante SMS. Aqui se integran bases de datos, configuraciones, preferencias, estructuras de conversacion, etcetera

Interactua internamente con el nucleo, y ofrece una interfaz de muy alto nivel para gestionar una aplicacion de comunicaciones

Esta capa proporciona funciones como:
- send_message
- query_conversations
- query_conversation

## Capa de Interfaz

Esta capa se encarga unicamente de interactuar con la capa subyacente de Sistema de Aplicacion, utilizando las funciones de alto nivel para egreso de datos (salida), e ingreso de datos (entrada), ademas del conjunto de funciones de alto nivel para efectuar acciones

La capa de interfaz solo esta encargada de adaptar la entrada y salida a su medio particular (p. Ej: GUI/WEB/CLI/API, etcetera)
