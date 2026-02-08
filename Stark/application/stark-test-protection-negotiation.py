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
    
    # Levantamos los endpoints TCP
    server_id = transport.receive_connection(tcp_module, _build_cfg(tcp_module, "LOCAL", server_port))

    time.sleep(2)

    client_id = transport.connect(tcp_module, _build_cfg(tcp_module, "REMOTE", server_port))
    
    print(f"[*] Conexión establecida. Server ID: {server_id} | Client ID: {client_id}")

    # 3. EJECUCIÓN DE NEGOCIACIÓN (Simetría de Roles)
    # Definimos las funciones para los hilos
    def server_negotiation():
        print("[SERVER] Iniciando negociación en modo PASIVO...")
        # El servidor envía la lista de módulos cargados en su ModuleContainer
        protection.negotiate(role=protection.LAYER_ROLE_PASSIVE, connection_identifier=server_id)
        print("[SERVER] Negociación finalizada.")

    def client_negotiation():
        print("[CLIENT] Iniciando negociación en modo ACTIVO...")
        # El cliente espera recibir la lista de módulos del servidor
        protection.negotiate(role=protection.LAYER_ROLE_ACTIVE, connection_identifier=client_id)
        print("[CLIENT] Negociación finalizada.")

    time.sleep(5)
    # Lanzamos ambos lados para evitar el bloqueo del hilo principal
    t_server = threading.Thread(target=server_negotiation)
    t_client = threading.Thread(target=client_negotiation)

    t_server.start()
    t_client.start()

    t_server.join()
    t_client.join()

    print("\n[TEST] Intercambio de metadatos mediante Datapackage completado.")

    # 4. CARGA DINÁMICA DE MÓDULO (Post-Negociación)
    # Simulamos que tras la negociación, el cliente elige un módulo (ej. HTTP_PROTECTION)
    http_mod_class = protection.query_module("HTTP_PROTECTION")
    
    print("\n[TEST] Cargando módulo seleccionado en ambos extremos...")
    
    # Configuración Cliente
    client_cfg = http_mod_class.CONFIGURATIONS.copy()
    client_cfg.query_setting("DEVICE_IDENTIFIER").value.value = client_id
    protection.load_module(http_mod_class, client_cfg)

    # 5. PRUEBA DE TRANSMISIÓN PROTEGIDA
    payload = b"SECURE_STARK_DATA_001"
    print(f"\n[CLIENT] Enviando datos protegidos: {payload}")
    protection.send(client_id, payload)

    # Reconfiguramos contexto para recibir como servidor (en este script compartido)
    server_cfg = http_mod_class.CONFIGURATIONS.copy()
    server_cfg.query_setting("DEVICE_IDENTIFIER").value.value = server_id
    protection.load_module(http_mod_class, server_cfg)

    print("[SERVER] Leyendo de la capa de protección...")
    # El módulo debe haber hecho el unprotect internamente
    received_data = protection.receive(server_id, limit=1024, timeout=None)

    # 6. VALIDACIÓN
    print(f"\n[RESULTADO] Datos recibidos: {received_data}")
    if received_data == payload:
        print("=== [SUCCESS] Negociación y Transmisión Validadas ===")
    else:
        print("=== [FAILURE] Discrepancia en los datos recibidos ===")

    # Cleanup
    transport.disconnect(client_id)
    transport.disconnect(server_id)

def _build_cfg(module, mode, port):
    cfg = module.CONFIGURATIONS.copy()
    prefix = "LOCAL" if mode == "LOCAL" else "REMOTE"
    cfg.query_setting(f"{prefix}_ADDRESS").value.value = "127.0.0.1"
    cfg.query_setting(f"{prefix}_PORT").value.value = port
    return cfg

if __name__ == "__main__":
    run_stark_protection_negotiation_test()