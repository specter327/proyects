import time
import random
from shared.communication_architecture import layers

def run_stark_protection_test():
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
    
    # Configuramos los endpoints
    server_id = transport.receive_connection(tcp_module, _build_cfg(tcp_module, "LOCAL", server_port))
    client_id = transport.connect(tcp_module, _build_cfg(tcp_module, "REMOTE", server_port))
    
    # 3. CARGA DE PROTECCIÓN (Uso estricto de la Capa)
    http_mod_class = protection.query_module("HTTP_PROTECTION")

    # Configuración del lado Cliente
    print("[TEST] Cargando protección para el CLIENTE...")
    client_prot_cfg = http_mod_class.CONFIGURATIONS.copy()
    client_prot_cfg.query_setting("DEVICE_IDENTIFIER").value.value = client_id
    protection.load_module(http_mod_class, client_prot_cfg)
    
    time.sleep(1) 

    # 4. ENVÍO DESDE EL NEXUS (Lado Cliente)
    stark_payload = b"STARK_ENCRYPTED_SIGNAL_v1"
    print(f"\n[NEXUS-CLIENT] Enviando datos: {stark_payload}")
    
    # Usamos la interfaz de la capa pasando el device_identifier por contrato
    # Aunque el módulo ya lo sepa, la capa lo recibe para mantener la firma
    protection.send(client_id, stark_payload)

    # 5. RECEPCIÓN EN EL NEXUS (Lado Servidor)
    # Reconfiguramos la capa para que actúe como el extremo receptor (Servidor)
    print("\n[TEST] Reconfigurando Capa para contexto SERVIDOR...")
    server_prot_cfg = http_mod_class.CONFIGURATIONS.copy()
    server_prot_cfg.query_setting("DEVICE_IDENTIFIER").value.value = server_id
    protection.load_module(http_mod_class, server_prot_cfg)

    print("[SERVER-APP] Esperando datos procesados por la Capa de Protección...")
    time.sleep(2) 

    # Solicitamos la lectura a la capa indicando de qué identificador queremos recibir
    final_data = protection.receive(server_id, limit=1024, timeout=5)

    print(f"[SERVER-APP] Datos finales recuperados: {final_data}")

    # 6. Validación de Integridad
    if final_data == stark_payload:
        print("\n[SUCCESS] Flujo simétrico completado. La abstracción de capa es total.")
    else:
        print(f"\n[FAILURE] Error en la recuperación. Recibido: {final_data}")

    # Limpieza
    protection.loaded_module.stop()
    transport.disconnect(client_id)
    transport.disconnect(server_id)

def _build_cfg(module, mode, port):
    cfg = module.CONFIGURATIONS.copy()
    prefix = "LOCAL" if mode == "LOCAL" else "REMOTE"
    cfg.query_setting(f"{prefix}_ADDRESS").value.value = "127.0.0.1"
    cfg.query_setting(f"{prefix}_PORT").value.value = port
    return cfg

if __name__ == "__main__":
    run_stark_protection_test()