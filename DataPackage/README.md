# Presentacion

Esta libreria proporciona una abstraccion generica para el uso de paquetes de datos sobre comunicaciones. 

Los paquetes de datos son presentados como un diccionario (```dict```), y serializados en ```bytes``` en formato ```JSON``` para su envio, o deserializados de ```bytes``` en formato ```JSON``` a un diccionario (```dict```) en su recepcion, de manera que el intercambio de mensajes estructurados es simple y potente

# Control

La libreria requiere que se le proporcione acceso a dos funciones:
- ```write(data: bytes)``: funcion de escritura. Debe retornar un valor booleano
- ```read(**args, **kwargs)```: funcion de lectura. Debe retornar bytes

Internamente permite el envio ordenado de paquetes de datos completos, y la recepcion de paquetes de datos ordenados por orden de recepcion, con funciones de alto nivel:

- ```send_datapackage(data_package: dict, **args, **kwargs) -> bool```
- ```receive_datapackage(timeout: int = None) -> dict```
> Operacion bloqueante: si hay un paquete de datos disponible en la cola, retorna el primero recibido (mas antiguo), si no lo hay, espera hasta que haya uno, o expire el tiempo limite (si aplica)

# Implementacion

La libreria convierte los datos (diccionarios) en secuencias de bytes serializadas en formato JSON, aplicando un delimitador para definir la limitacion entre un paquete de datos y otro. De esta manera, cada paquete de datos enviado se envia de manera atomica, asegurandose del orden, y fiabilidad de entrega. Por parte de la recepcion, los paquetes de datos son reconstruidos a partir de bytes serializados, y almacenados de manera ordenada en una cola interna de paquetes: cada llamada a: ```receive_datapackage``` retorna el ultimo paquete de datos recibido no extraido; posteriormente se descarta de la cola y se retorna el siguiente