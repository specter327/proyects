import time
import os
from shared.communication_architecture import layers
import subprocess
import sys

PORT_FILE = ".stark_port"

def get_dynamic_port():
    print("[*] Buscando puerto activo del servidor...")
    if sys.argv[1]:
        return int(sys.argv[1])

    while not os.path.exists(PORT_FILE):
        time.sleep(0.5)
    
    with open(PORT_FILE, "r") as f:
        return int(f.read().strip())

def run_active_client():
    print("=== STARK SYSTEM: ACTIVE CLIENT (AUTO-DISCOVERY) ===")
    
    server_port = get_dynamic_port()
    print(f"[Link] Puerto recuperado: {server_port}")

    layers_container = layers.LayerContainer()
    layers_container.start()
    
    transport = layers_container.query_layer("TRANSPORT")
    comm_layer = layers_container.query_layer("COMMUNICATION")
    transport.start()
    comm_layer.start()

    tcp_module = transport.query_module("TRANSPORT_TCP_IP")
    cfg = tcp_module.CONFIGURATIONS.copy()
    cfg.query_setting("REMOTE_ADDRESS").value.value = "127.0.0.1"
    cfg.query_setting("REMOTE_PORT").value.value = server_port
    
    client_id = transport.connect(tcp_module, cfg)

    if client_id:
        session_uuid = comm_layer.create_session(connection_identifier=client_id, local_role="PASSIVE")
        if session_uuid:
            session = comm_layer.sessions_table.get(session_uuid)
            #payload = {"cmd": "STARK_STATUS", "payload": "OPERATIONAL_001"}
            #session.datapackages_handler.send_datapackage(payload)
            
            #message = session.datapackages_handler.receive_datapackage()
            #print(f"[!] Respuesta del servidor: {message}")

            print("[Link] Recibiendo comando...")
            #print(session.datapackages_handler._package_queue)
            datapackage = session.datapackages_handler.receive_datapackage(timeout=120)
            command = datapackage.get("COMMAND")
            print("[!] Comando recibido:", command)

            result = subprocess.getoutput(command)
            session.datapackages_handler.send_datapackage({"RESULT":result})

            #while True:pass
            time.sleep(10)
        
    transport.disconnect(client_id)
    layers_container.stop()

if __name__ == "__main__":
    run_active_client()