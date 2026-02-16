import os
import socket
from shared.communication_architecture import layers
import random
import time

PORT_FILE = ".stark_port"

def run_passive_server():
    print("=== STARK SYSTEM: PASSIVE SERVER (DYNAMIC PORT) ===")
    
    layers_container = layers.LayerContainer()
    layers_container.start()
    
    transport = layers_container.query_layer("TRANSPORT")
    comm_layer = layers_container.query_layer("COMMUNICATION")
    transport.start()
    comm_layer.start()

    tcp_module = transport.query_module("TRANSPORT_TCP_IP")
    cfg = tcp_module.CONFIGURATIONS.copy()
    cfg.query_setting("LOCAL_ADDRESS").value.value = "127.0.0.1"
    
    # El puerto 0 solicita al SO un puerto aleatorio disponible
    cfg.query_setting("LOCAL_PORT").value.value = random.randint(24391, 55490)
    
    print("[*] Solicitando puerto dinámico...")
    server_id = transport.receive_connection(tcp_module, cfg)
    
    # Recuperamos el puerto real asignado (asumiendo que su módulo TCP actualiza el objeto cfg o socket)
    # Si su infraestructura no lo devuelve directamente, aquí un helper estándar:
    actual_port = cfg.query_setting("LOCAL_PORT").value.value 
    
    with open(PORT_FILE, "w") as f:
        f.write(str(actual_port))
    
    print(f"[*] Escuchando en el puerto: {actual_port} (Registrado en {PORT_FILE})")
    
    session_uuid = comm_layer.create_session(connection_identifier=server_id, local_role="ACTIVE")
    
    if session_uuid:
        session = comm_layer.sessions_table.get(session_uuid)
        #received_pkg = session.datapackages_handler.receive_datapackage(timeout=120)
        #if received_pkg:
        #    print(f"[DATA RECEIVED]: {received_pkg}")
        #session.datapackages_handler.send_datapackage("Protocolo de enlace exitoso.")
        
        print("[Nexus] Enviando comando...")
        session.datapackages_handler.send_datapackage({"COMMAND":"whoami"})

        print("[Nexus] Result:")
        datapackage = session.datapackages_handler.receive_datapackage(timeout=120)
        result = datapackage.get("RESULT")
        print(result)

        #while True: pass
        time.sleep(10)

    # Cleanup
    os.remove(PORT_FILE)
    transport.disconnect(server_id)
    layers_container.stop()

if __name__ == "__main__":
    run_passive_server()