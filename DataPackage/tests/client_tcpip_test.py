import socket
import time
from datapackage import Datapackage

def emisor_generico():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 9999))
    
    # Inyectamos el socket
    dp = Datapackage(
        write_function=sock.sendall,
        read_function=lambda: sock.recv(4096)
    )

    # Lista de paquetes de prueba con diferentes estructuras
    cargas = [
        {"id": 1, "msg": "Hola mundo"},
        {"id": 2, "sensor_data": [22.5, 23.1, 21.8], "active": True},
        {"id": 3, "config": {"mode": "verbose", "retries": 5}}
    ]

    for carga in cargas:
        print(f"[EMISOR] Enviando: {carga}")
        dp.send_datapackage(carga)
        
        # Esperamos la respuesta del receptor
        ack = dp.receive_datapackage(timeout=2)
        print(f"[EMISOR] Respuesta recibida: {ack}")
        time.sleep(1)

    dp.stop()
    sock.close()

if __name__ == "__main__":
    emisor_generico()