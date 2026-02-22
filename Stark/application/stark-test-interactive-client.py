import time
import os
import sys
from shared.communication_architecture import layers

# Si el script está en Stark/application/
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LINK_DIR = os.path.join(BASE_DIR, "link")

if LINK_DIR not in sys.path:
    sys.path.insert(0, LINK_DIR)

PORT_FILE = ".stark_port"

def get_dynamic_port():
    if len(sys.argv) > 1:
        return int(sys.argv[1])
        
    print("[*] Buscando puerto activo en archivo de señalización...")
    while not os.path.exists(PORT_FILE):
        time.sleep(0.5)
    
    with open(PORT_FILE, "r") as f:
        return int(f.read().strip())

def run_interactive_console():
    print("=== STARK SYSTEM: OPERATOR CONSOLE ===")
    
    server_port = get_dynamic_port()
    print(f"[Link] Objetivo: 127.0.0.1:{server_port}")

    # Inicialización del Stack
    layers_container = layers.LayerContainer()
    layers_container.start()
    
    transport = layers_container.query_layer("TRANSPORT")
    comm_layer = layers_container.query_layer("COMMUNICATION")
    transport.start()
    comm_layer.start()

    # Configuración TCP
    tcp_module = transport.query_module("TRANSPORT_TCP_IP")
    cfg = tcp_module.CONFIGURATIONS.copy()
    cfg.query_setting("REMOTE_ADDRESS").value.value = "127.0.0.1"
    cfg.query_setting("REMOTE_PORT").value.value = server_port
    
    client_id = transport.connect(tcp_module, cfg)

    if client_id:
        # MANTENEMOS "PASSIVE" PORQUE ES LO QUE TU HANDSHAKE ACEPTA ACTUALMENTE
        session_uuid = comm_layer.create_session(connection_identifier=client_id, local_role="PASSIVE")
        
        if session_uuid:
            session = comm_layer.sessions_table.get(session_uuid)
            print("[Link] Túnel seguro establecido. Consola lista.")
            print("------------------------------------------------")

            try:
                while True:
                    # 1. INPUT: El operador toma la iniciativa
                    command = input("Stark-Shell> ").strip()
                    
                    if not command:
                        continue

                    # 2. SEND: Enviamos la orden al Agente (Servidor)
                    session.datapackages_handler.send_datapackage({"COMMAND": command})

                    if command.upper() in ["EXIT", "QUIT"]:
                        break

                    # 3. RECEIVE: Esperamos la salida del comando
                    # Usamos timeout=None para esperar comandos largos
                    datapackage = session.datapackages_handler.receive_datapackage(timeout=None)
                    
                    if datapackage and "RESULT" in datapackage:
                        print(datapackage["RESULT"])
                    else:
                        print("[!] Trama vacía o sin resultado.")

            except KeyboardInterrupt:
                print("\n[*] Interrupción de usuario.")
            except Exception as e:
                print(f"[!] Error crítico en sesión: {e}")
        
    transport.disconnect(client_id)
    layers_container.stop()

if __name__ == "__main__":
    run_interactive_console()