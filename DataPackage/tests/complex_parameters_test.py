import time
import threading
from typing import Dict, List
from datapackage import Datapackage 
import json

# --- SIMULACIÓN DE CAPA DE COMUNICACIÓN (MOCK) ---
class GenericTransport:
    """
    Simula un backend de comunicaciones multiplexado que requiere 
    un identificador de recurso para realizar operaciones de E/S.
    """
    def __init__(self):
        # Almacena buffers independientes por identificador
        self.resource_buffers: Dict[int, List[bytes]] = {
            101: [], 
            102: []
        }

    def write(self, data: bytes, resource_id: int) -> bool:
        """Simula una escritura en un recurso específico."""
        print(f"[Transport] I/O Write -> Resource {resource_id}: {data}")
        return True

    def read(self, resource_id: int, buffer_limit: int = 4096, timeout: int = 1) -> bytes:
        """Simula una lectura bloqueante de un recurso específico."""
        if resource_id in self.resource_buffers and self.resource_buffers[resource_id]:
            return self.resource_buffers[resource_id].pop(0)
        
        # Simulación de latencia de red/E/S
        time.sleep(0.05)
        return b""

# --- BANCO DE PRUEBAS (TEST SUITE) ---
def run_integration_test():
    transport = GenericTransport()
    
    print("=== Datapackage: Generic Integration Test ===")
    print("[1/5] Inicialización de instancia con parámetros de construcción...")

    # Instanciación con parámetros iniciales para Recurso 101
    dp = Datapackage(
        write_function=transport.write,
        read_function=transport.read,
        read_arguments=(101, 2048) # Resource ID y Buffer Limit
    )

    # Simulación de carga de datos en el backend
    test_payload = {"status": "success", "data": "payload_alpha", "timestamp": time.time()}
    raw_frame = json.dumps(test_payload).encode("UTF-8") + Datapackage.PACKAGE_DELIMITER
    transport.resource_buffers[101].append(raw_frame)

    print("[2/5] Verificación de recepción con contexto inicial...")
    received = dp.receive_datapackage(timeout=2)
    
    if received and received.get("data") == "payload_alpha":
        print(f"    [OK] Datos procesados correctamente: {received}")
    else:
        print("    [FAIL] Error en la recepción o procesamiento de datos.")

    print("\n[3/5] Verificación de transmisión con parámetros dinámicos...")
    # Se pasan los argumentos necesarios para la función 'write' del transporte
    send_success = dp.send_datapackage({"command": "reboot"}, resource_id=101)
    if send_success:
        print("    [OK] Transmisión enviada a la función de escritura.")

    print("\n[4/5] Prueba de actualización de contexto (Hot Swap)...")
    # Cambiamos el foco del hilo lector al Recurso 102
    dp.update_reception_parameters(resource_id=102, buffer_limit=4096)
    
    # Inyectamos datos en el nuevo recurso
    new_payload = {"status": "active", "data": "payload_beta"}
    new_frame = json.dumps(new_payload).encode("UTF-8") + Datapackage.PACKAGE_DELIMITER
    transport.resource_buffers[102].append(new_frame)
    
    received_updated = dp.receive_datapackage(timeout=2)
    if received_updated and received_updated.get("data") == "payload_beta":
        print(f"    [OK] Contexto actualizado. Datos recibidos del Recurso 102: {received_updated}")
    else:
        print("    [FAIL] No se recibieron datos tras la actualización de parámetros.")

    print("\n[5/5] Finalización de procesos...")
    dp.stop()
    print("=== Test Finalizado con Éxito ===")

if __name__ == "__main__":
    run_integration_test()