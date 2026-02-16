import time
import random
import threading
from shared.communication_architecture import layers

def run_stark_protection_negotiation_test():
    print("=== STARK SYSTEM: ROBUST PROTECTION LAYER TEST ===")
    
    # Eventos de sincronización para evitar condiciones de carrera en el test
    server_ready_event = threading.Event()
    negotiation_done_event = threading.Event()
    
    layers_container = layers.LayerContainer()
    layers_container.start()
    
    transport = layers_container.query_layer("TRANSPORT")
    protection = layers_container.query_layer("PROTECTION")
    
    transport.start()
    protection.start()

    server_port = random.randint(30000, 50000)
    tcp_module = transport.query_module("TRANSPORT_TCP_IP")
    http_mod_class = protection.query_module("HTTP_PROTECTION")

    # Almacén de resultados para hilos
    results = {"server_received": b"", "error": None}

    def server_worker():
        try:
            # 1. Setup Conexión
            server_id = transport.receive_connection(tcp_module, _build_cfg(tcp_module, "LOCAL", server_port))
            server_ready_event.set() # Avisamos al cliente que puede conectar
            
            # 2. Negociación
            print("[SERVER] Esperando negociación...")
            protection.negotiate(role=protection.LAYER_ROLE_PASSIVE, connection_identifier=server_id)
            
            # 3. Carga de Módulo (Inmediata tras negociar)
            server_cfg = http_mod_class.CONFIGURATIONS.copy()
            server_cfg.query_setting("DEVICE_IDENTIFIER").value.value = server_id
            protection.load_module(http_mod_class, server_cfg)
            
            # 4. Recepción Robusta (con reintentos)
            print("[SERVER] Módulo cargado. Escuchando datos...")
            max_retries = 5
            for i in range(max_retries):
                # Intentamos leer con un timeout corto pero repetitivo
                data = protection.receive(server_id, limit=1024, timeout=5)
                if data:
                    results["server_received"] = data
                    break
                print(f"[SERVER] Intento {i+1}/{max_retries}: Buffer vacío, reintentando...")
                time.sleep(1)
                
        except Exception as e:
            results["error"] = f"Server Error: {str(e)}"
        finally:
            negotiation_done_event.set()

    def client_worker():
        try:
            server_ready_event.wait(timeout=10)
            client_id = transport.connect(tcp_module, _build_cfg(tcp_module, "REMOTE", server_port))
            
            # 1. Negociación
            print("[CLIENT] Iniciando negociación...")
            protection.negotiate(role=protection.LAYER_ROLE_ACTIVE, connection_identifier=client_id)
            
            # 2. Carga de Módulo
            client_cfg = http_mod_class.CONFIGURATIONS.copy()
            client_cfg.query_setting("DEVICE_IDENTIFIER").value.value = client_id
            protection.load_module(http_mod_class, client_cfg)
            
            # 3. Esperar un breve instante para asegurar que el servidor entró en 'receive'
            time.sleep(1) 
            
            payload = b"SECURE_STARK_DATA_001"
            print(f"[CLIENT] Enviando: {payload}")
            protection.send(client_id, payload)
            
        except Exception as e:
            results["error"] = f"Client Error: {str(e)}"

    # Ejecución concurrente
    t_srv = threading.Thread(target=server_worker)
    t_cli = threading.Thread(target=client_worker)

    t_srv.start()
    t_cli.start()

    t_cli.join()
    t_srv.join()

    # Validación Final
    print("\n" + "="*40)
    if results["error"]:
        print(f"[!!!] FALLO CRÍTICO: {results['error']}")
    else:
        print(f"[RESULTADO] Datos recibidos por Servidor: {results['server_received']}")
        if results["server_received"] == b"SECURE_STARK_DATA_001":
            print("=== [SUCCESS] Integridad de datos confirmada ===")
        else:
            print("=== [FAILURE] Los datos se perdieron o llegaron corruptos ===")
    print("="*40)

def _build_cfg(module, mode, port):
    cfg = module.CONFIGURATIONS.copy()
    prefix = "LOCAL" if mode == "LOCAL" else "REMOTE"
    cfg.query_setting(f"{prefix}_ADDRESS").value.value = "127.0.0.1"
    cfg.query_setting(f"{prefix}_PORT").value.value = port
    return cfg

if __name__ == "__main__":
    run_stark_protection_negotiation_test()