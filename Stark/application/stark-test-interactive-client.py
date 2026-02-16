import time
import os
import subprocess
import sys
from shared.communication_architecture import layers

PORT_FILE = ".stark_port"

def get_dynamic_port():
    """Recupera el puerto desde argumentos o archivo de señalización."""
    try:
        if len(sys.argv) > 1:
            return int(sys.argv[1])
    except ValueError:
        pass

    print("[*] Buscando puerto activo en archivo de sistema...")
    while not os.path.exists(PORT_FILE):
        time.sleep(0.5)
    
    with open(PORT_FILE, "r") as f:
        return int(f.read().strip())

def run_interactive_client():
    print("=== STARK SYSTEM: INTERACTIVE PASSIVE CLIENT ===")
    
    server_port = get_dynamic_port()
    print(f"[Link] Estableciendo túnel hacia el puerto: {server_port}")

    # Inicialización del Stack de Capas
    layers_container = layers.LayerContainer()
    layers_container.start()
    
    transport = layers_container.query_layer("TRANSPORT")
    comm_layer = layers_container.query_layer("COMMUNICATION")
    transport.start()
    comm_layer.start()

    # Configuración de Capa 4 (Transporte)
    tcp_module = transport.query_module("TRANSPORT_TCP_IP")
    cfg = tcp_module.CONFIGURATIONS.copy()
    cfg.query_setting("REMOTE_ADDRESS").value.value = "127.0.0.1"
    cfg.query_setting("REMOTE_PORT").value.value = server_port
    
    client_id = transport.connect(tcp_module, cfg)

    if not client_id:
        print("[!] Error crítico: No se pudo establecer la conexión TCP.")
        return

    # Creación de Sesión en Capa de Aplicación (Modo PASIVO para recibir comandos)
    session_uuid = comm_layer.create_session(connection_identifier=client_id, local_role="PASSIVE")
    
    if session_uuid:
        session = comm_layer.sessions_table.get(session_uuid)
        print("[Link] Sesión establecida. Esperando instrucciones del servidor...")

        try:
            while True:
                # El cliente PASIVO espera a que el ACTIVE (servidor) hable primero
                datapackage = session.datapackages_handler.receive_datapackage(timeout=None)
                
                if not datapackage:
                    continue

                command = datapackage.get("COMMAND")
                
                if command:
                    # Comando de ruptura
                    if command.strip().upper() in ["EXIT", "QUIT"]:
                        break

                    # Ejecución silenciosa y captura de flujo
                    proc = subprocess.Popen(
                        command, 
                        shell=True, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        stdin=subprocess.PIPE
                    )
                    stdout, stderr = proc.communicate()
                    output = stdout.decode() + stderr.decode()

                    # Si no hay salida (ej: rm file), enviamos confirmación para no dejar al server colgado
                    if not output:
                        output = "[*] Command executed (No output)"

                    # Responder al servidor
                    session.datapackages_handler.send_datapackage({
                        "RESULT": output
                    })

        except KeyboardInterrupt:
            print("\n[!] Conexión cerrada por el usuario.")
        except Exception as e:
            print(f"\n[!] Error en el bucle de comunicación: {e}")
        
    # Cleanup
    print("[*] Desconectando capas...")
    transport.disconnect(client_id)
    layers_container.stop()
    print("=== CLIENTE STARK FINALIZADO ===")

if __name__ == "__main__":
    run_interactive_client()