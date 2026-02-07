# Presentacion

Esta libreria proporciona una abstraccion generica para el uso de paquetes de datos sobre comunicaciones. Permitiendo una logica de comunicacion por mensajes estructurados.

Los paquetes de datos son presentados como un diccionario (```dict```), y serializados en ```bytes``` en formato ```JSON``` (```UTF-8```) para su envio, o deserializados de ```bytes``` en formato ```JSON``` (```UTF-8```) a un diccionario (```dict```) en su recepcion, de manera que el intercambio de mensajes estructurados es simple y potente

# Control

La libreria requiere que se le proporcione acceso a dos funciones:
- ```write(data: bytes)```: funcion de escritura. Debe retornar un valor booleano
- ```read()```: funcion de lectura. Debe retornar bytes

Internamente permite el envio ordenado de paquetes de datos completos, y la recepcion de paquetes de datos ordenados por orden de recepcion, con funciones de alto nivel:

- ```send_datapackage(data_package: dict) -> bool```
- ```receive_datapackage(timeout: int = None) -> dict```

> Operacion bloqueante: si hay un paquete de datos disponible en la cola, retorna el primero recibido (mas antiguo), si no lo hay, espera hasta que haya uno, o expire el tiempo limite (si aplica)

# Implementacion

La libreria convierte los datos (diccionarios) en secuencias de bytes serializadas en formato JSON, aplicando un delimitador para definir la limitacion entre un paquete de datos y otro. De esta manera, cada paquete de datos enviado se envia como una unidad logica atomica, asegurandose del orden y estructura, delegando la fiabilidad de entrega al transporte subyacente. Por parte de la recepcion, los paquetes de datos son reconstruidos a partir de bytes serializados, y almacenados de manera ordenada en una cola interna de paquetes: cada llamada a: ```receive_datapackage``` retorna el primer paquete de datos recibido pendiente en la cola (FIFO); posteriormente se descarta de la cola y se retorna el siguiente

# Uso
## Importacion

```python
from datapackage import Datapackage
```

## Instanciacion
```python
datapackage = Datapackage(
    read_function=read_func,
    write_function=write_func
)

# Se utilizaron funciones de ejemplo. Puede trabajar sobre cualquier funcion que opere conceptualmente sobre un flujo de datos secuenciales
```

## Envio de paquete de datos
```python
data = {
    "TIMESTAMP":1234,
    "DATA":"¡Hola, mundo!"
}

datapackage.send_datapackage(data)
```

## Recepcion de paquete de datos
```python
received_response = datapackage.receive_datapackage()
```

# Indicaciones

- La libreria no implementa cifrado, compresion, ni procesamiento de datos.
- No se impone un tamaño limite para los paquetes de datos; pero es recomendable no transmitir paquetes de datos demasiado grandes.
- La fiabilidad de entrega depende totalmente del transporte subyacente; la libreria solo proporciona fiabilidad en el orden de recepcion.
- El delimitador de paquetes de datos utilizado y transmitido podria colisionar con el contenido.
- La libreria no expone mecanismos para pasar parametros dinamicos a las funciones subyacentes de escritura y lectura; dichas funciones deben encapsular internamente su propia logica.