import time
import os
import sys
import socket
import threading
from shared.communication_architecture import layers

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LINK_DIR = os.path.join(BASE_DIR, "link")
if LINK_DIR not in sys.path:
    sys.path.insert(0, LINK_DIR)

def run_nexus_orchestrator():
    print("=== STARK SYSTEM: NEXUS ORCHESTRATOR (CORE) ===")
    
    # 1. Inicialización del Contenedor de Capas
    layers_container = layers.LayerContainer()
    layers_container.start()
    
    # Obtención de referencias
    transport = layers_container.query_layer("TRANSPORT")
    comm_layer = layers_container.query_layer("COMMUNICATION")
    control_layer = layers_container.query_layer("CONTROL")

    # 2. Configuración de Roles y Filtro de Módulos
    # EVITAMOS cargar SYSTEM_SHELL_PASSIVE en el Maestro para prevenir el secuestro de prompts
    # Suponiendo que tu LayerContainer o ControlLayer permite filtrar:
    # control_layer.set_unallowed_modules(["SYSTEM_SHELL_PASSIVE"])

    #layers_container.start() 
    # Al hacer start(), ControlLayer cargará SYSTEM_SHELL_ACTIVE y lanzará su hilo CLI interno
    
    # 3. Setup del Listener de Red
    listen_port = 24450
    transport.start()
    comm_layer.start()
    control_layer.start()
    tcp_module_class = transport.query_module("TRANSPORT_TCP_IP")
    cfg = tcp_module_class.CONFIGURATIONS.copy()
    cfg.query_setting("LOCAL_ADDRESS").value.value = "127.0.0.1"
    cfg.query_setting("LOCAL_PORT").value.value = listen_port

    print(f"[*] Escuchando en el puerto {listen_port}...")

    # 4. Bucle de Gestión de Conexiones
    try:
        while True:
            # Bloqueo hasta nueva conexión del agente
            connection_id = transport.receive_connection(tcp_module_class, cfg)
            
            if connection_id:
                # Sincronización de transporte
                while not transport.connections_table.get(connection_id).is_connected:
                    time.sleep(0.1)

                print(f"\n[+] Nuevo Link detectado. ID: {connection_id}")

                # 5. Elevación a Sesión
                # El local_role="ACTIVE" es crucial para que ControlLayer sepa qué módulos asignar
                session_uuid = comm_layer.create_session(connection_id, local_role="ACTIVE")
                
                if session_uuid:
                    print(f"[*] Sesión {session_uuid} establecida y delegada a ControlLayer.")
                    # A partir de aquí, SYSTEM_SHELL_ACTIVE detectará la sesión
                    # y su hilo _cli_loop tomará el control del terminal.
                
                # En un orquestador real, no cerramos aquí, 
                # dejamos que el thread del módulo trabaje.
            
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[*] Finalizando Orquestador...")
    finally:
        layers_container.stop()
        print("[*] Stack de comunicaciones cerrado.")

if __name__ == "__main__":
    run_nexus_orchestrator()