import time
import threading
from typing import Dict
from datapackage import Datapackage 

# --- MOCK DE CAPA DE TRANSPORTE ---
class MockTransport:
    def __init__(self):
        # Simula buffers de red para diferentes IDs de conexión
        self.buffers: Dict[int, list] = {1: [], 2: []}

    def send(self, data: bytes, connection_id: int) -> bool:
        print(f"[Transport] Enviando a ID {connection_id}: {data}")
        # En una prueba real, aquí enviarías por un socket
        return True

    def receive(self, connection_id: int, limit: int = 4096, timeout: int = 1) -> bytes:
        # Simula espera de datos
        if connection_id in self.buffers and self.buffers[connection_id]:
            return self.buffers[connection_id].pop(0)
        time.sleep(0.1) # Simula latencia
        return b""

# --- SCRIPT DE PRUEBA ---
def test_datapackage_context():
    transport = MockTransport()
    
    print("--- Iniciando Prueba de Datapackage con Inyección de Contexto ---")

    # 1. Instanciamos Datapackage
    # Observa que pasamos las funciones del transporte directamente
    dp = Datapackage(
        write_function=transport.send,
        read_function=transport.receive
    )

    # 2. Configuramos los parámetros de recepción para la "Conexión 1"
    # El hilo interno empezará a llamar a transport.receive(connection_id=1, limit=1024)
    print("[*] Configurando Datapackage para Conexión ID: 1")
    dp.set_reception_parameters(connection_id=1, limit=1024)

    # 3. Simulamos la llegada de un paquete al buffer del transporte para el ID 1
    test_data = {"MSG": "Hola Stark", "SEQ": 1}
    raw_packet = b'{"MSG": "Hola Stark", "SEQ": 1}' + Datapackage.PACKAGE_DELIMITER
    transport.buffers[1].append(raw_packet)

    # 4. Intentamos recibir el paquete procesado
    print("[*] Esperando paquete procesado...")
    received = dp.receive_datapackage(timeout=2)
    
    if received:
        print(f"[+] Éxito! Recibido en Capa Superior: {received}")
    else:
        print("[!] Error: No se recibió el paquete.")

    # 5. Probamos el Envío (Pasando el ID dinámicamente)
    print("\n[*] Probando envío con parámetros dinámicos...")
    send_status = dp.send_datapackage({"CMD": "PING"}, connection_id=1)
    if send_status:
        print("[+] Envío ejecutado correctamente.")

    # 6. Prueba de Cambio de Contexto "En Caliente"
    print("\n[*] Cambiando contexto a Conexión ID: 2 (Prueba de Lock)")
    dp.set_reception_parameters(connection_id=2)
    
    # Metemos datos en el buffer del ID 2
    transport.buffers[2].append(b'{"STATUS": "CONNECTED"}' + Datapackage.PACKAGE_DELIMITER)
    
    received_new = dp.receive_datapackage(timeout=2)
    print(f"[+] Recibido tras cambio de ID: {received_new}")

    # Finalizar
    dp.stop()
    print("\n--- Prueba Finalizada ---")

if __name__ == "__main__":
    test_datapackage_context()
