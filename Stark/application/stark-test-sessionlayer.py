import time
import threading
from shared.communication_architecture import layers

def run_stark_node(role: str, port: int, remote_ip: str = None):
    print(f"=== STARK NODE: {role} ===")
    
    # 1. Inicialización de Infraestructura
    layers_container = layers.LayerContainer()
    layers_container.start()
    
    transport = layers_container.query_layer("TRANSPORT")
    comm_layer = layers_container.query_layer("COMMUNICATION")
    transport.start()
    comm_layer.start()

    tcp_module = transport.query_module("TRANSPORT_TCP_IP")
    cfg = tcp_module.CONFIGURATIONS.copy()

    # 2. Establecimiento de Conexión Física (L4)
    if role == "PASSIVE_SERVER":
        cfg.query_setting("LOCAL_ADDRESS").value.value = "0.0.0.0"
        cfg.query_setting("LOCAL_PORT").value.value = port
        print(f"[*] [{role}] Escuchando en puerto {port}...")
        conn_id = transport.receive_connection(tcp_module, cfg)
    else:
        cfg.query_setting("REMOTE_ADDRESS").value.value = remote_ip
        cfg.query_setting("REMOTE_PORT").value.value = port
        print(f"[*] [{role}] Conectando a {remote_ip}:{port}...")
        conn_id = transport.request_connection(tcp_module, cfg)

    # 3. Creación de Sesión Orquestada (L5/L6)
    # Esto activará SessionLayer.start(), que negocia Protección y Seguridad
    print(f"[*] [{role}] Iniciando SessionLayer (Handshake RSA + HTTP)...")
    session_uuid = comm_layer.create_session(connection_identifier=conn_id, local_role=role)
    
    if session_uuid:
        session = comm_layer.sessions_table.get(session_uuid)
        
        # 4. Intercambio de Datos Protegidos
        if role == "ACTIVE_CLIENT":
            payload = {"cmd": "system_info", "status": "request"}
            print(f"[>] [{role}] Enviando Datapackage cifrado...")
            session.datapackages_handler.send_datapackage(payload)
            
            # Esperar respuesta
            response = session.datapackages_handler.receive_datapackage(timeout=10)
            print(f"[<] [{role}] Respuesta del servidor: {response}")
        
        else: # SERVER
            print(f"[*] [{role}] Esperando datos del cliente...")
            incoming = session.datapackages_handler.receive_datapackage(timeout=15)
            if incoming:
                print(f"[<] [{role}] Datapackage recibido y descifrado: {incoming}")
                session.datapackages_handler.send_datapackage({"status": "SUCCESS", "code": 200})

    # Cleanup
    time.sleep(2)
    transport.disconnect(conn_id)
    layers_container.stop()

if __name__ == "__main__":
    # Ejecución local con hilos para verificar compatibilidad
    port = 45000
    
    # Lanzar Servidor
    srv = threading.Thread(target=run_stark_node, args=("PASSIVE_SERVER", port))
    srv.start()
    
    time.sleep(2) # Pausa técnica para asegurar que el socket está en LISTEN
    
    # Lanzar Cliente
    cli = threading.Thread(target=run_stark_node, args=("ACTIVE_CLIENT", port, "127.0.0.1"))
    cli.start()