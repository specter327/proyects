import time
import random
import threading
from shared.communication_architecture import layers

def run_stark_protection_negotiation_test():
    print("=== STARK SYSTEM: PROTECTION LAYER NEGOTIATION TEST ===")
    
    # 1. Inicialización de infraestructura
    layers_container = layers.LayerContainer()
    layers_container.start()
    
    transport = layers_container.query_layer("TRANSPORT")
    protection = layers_container.query_layer("PROTECTION")
    
    transport.start()
    protection.start()

    # 2. Setup de Red (TCP)
    server_port = random.randint(30000, 50000)
    tcp_module = transport.query_module("TRANSPORT_TCP_IP")
    
    server_id = transport.receive_connection(tcp_module, _build_cfg(tcp_module, "LOCAL", server_port))
    time.sleep(1) # Latencia mínima para estabilización de socket
    client_id = transport.connect(tcp_module, _build_cfg(tcp_module, "REMOTE", server_port))
    
    print(f"[*] Conexión establecida. Server ID: {server_id} | Client ID: {client_id}")

    # 3. EJECUCIÓN DE NEGOCIACIÓN AUTOMATIZADA
    # La lógica de selección, intercambio de plantillas y carga (load_module) 
    # ocurre internamente dentro de protection.negotiate()
    def server_negotiation():
        print("[SERVER] Iniciando handshake pasivo...")
        protection.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value = server_id
        success = protection.negotiate(role=protection.LAYER_ROLE_PASSIVE, connection_identifier=server_id)
        print(f"[SERVER] Negociación {'COMPLETADA' if success else 'FALLIDA'}.")

    def client_negotiation():
        print("[CLIENT] Iniciando handshake activo...")
        protection.layer_settings.query_setting("DEVICE_IDENTIFIER").value.value = client_id
        success = protection.negotiate(role=protection.LAYER_ROLE_ACTIVE, connection_identifier=client_id)
        print(f"[CLIENT] Negociación {'COMPLETADA' if success else 'FALLIDA'}.")

    t_server = threading.Thread(target=server_negotiation)
    t_client = threading.Thread(target=client_negotiation)

    t_server.start()
    t_client.start()

    t_server.join()
    t_client.join()

    print("\n[TEST] Capa de protección configurada mediante handshake.")

    # 4. PRUEBA DE TRANSMISIÓN PROTEGIDA (Uso de la capa post-negociación)
    # En este punto, la capa ya detecta que tiene un módulo cargado para estos IDs.
    payload = b"SECURE_STARK_DATA_001"
    print(f"\n[CLIENT] Enviando datos: {payload}")
    protection.send(client_id, payload)

    print("[SERVER] Esperando datos en la capa de protección...")
    
    # Implementación de espera para compensar la latencia de procesamiento asíncrono
    received_data = b""
    attempts = 0
    while not received_data and attempts < 5:
        received_data = protection.receive(server_id, limit=1024, timeout=5)
        if not received_data:
            print(f"[*] Intento {attempts + 1}: Buffer vacío, reintentando...")
            time.sleep(1)
        attempts += 1

    # 5. VALIDACIÓN FINAL
    print(f"\n[RESULTADO] Datos recibidos: {received_data}")
    
    if received_data == payload:
        print("=== [SUCCESS] Protocolo de Negociación y Carga Dinámica Validado ===")
    else:
        print("=== [FAILURE] Error en la integridad o flujo de la negociación ===")

    # Cleanup
    transport.disconnect(client_id)
    transport.disconnect(server_id)
    layers_container.stop()

def _build_cfg(module, mode, port):
    cfg = module.CONFIGURATIONS.copy()
    prefix = "LOCAL" if mode == "LOCAL" else "REMOTE"
    cfg.query_setting(f"{prefix}_ADDRESS").value.value = "127.0.0.1"
    cfg.query_setting(f"{prefix}_PORT").value.value = port
    return cfg

if __name__ == "__main__":
    run_stark_protection_negotiation_test()