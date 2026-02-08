import time
from shared.communication_architecture import layers
import traceback
layers_container = layers.LayerContainer()
layers_container.start()

for layer_name in layers_container.query_layers():
    layer = layers_container.query_layer(layer_name)

    print("Layer:", layer_name)
    layer.start()
    for module_name in layer.query_modules():
        print("    Module:", module_name)


from shared.communication_architecture.layers.transport.modules.tcpip import TransportModule
import random
def run_stark_test():
    server_port = random.randint(29381, 54390)
    
    # 2. Preparar Configuraciones para el Cliente
    # 1. Preparar Configuraciones para el Servidor
    transport_layer = layers_container.query_layer("TRANSPORT")
    
    # Get TCP/IP module
    tcp_ip_module = transport_layer.query_module("TRANSPORT_TCP_IP")

    # Configure the module
    client_module_configurations = tcp_ip_module.CONFIGURATIONS.copy()
    client_module_configurations.query_setting("REMOTE_ADDRESS").value.value = "127.0.0.1"
    client_module_configurations.query_setting("REMOTE_PORT").value.value = server_port


    # Configure the TCP/IP module for server
    server_module_configurations = tcp_ip_module.CONFIGURATIONS.copy()
    server_module_configurations.query_setting("LOCAL_ADDRESS").value.value = "127.0.0.1"
    server_module_configurations.query_setting("LOCAL_PORT").value.value = server_port

    print("[TEST] Inicializando módulos...")
    server_identifier = transport_layer.receive_connection(tcp_ip_module, server_module_configurations)
    print("Server result:", server_identifier)

    # Connect configurated client
    client_identifier = transport_layer.connect(tcp_ip_module, client_module_configurations)

    print("Connection result:", client_identifier)
    # 4. Conectar el cliente

    print("[CLIENT] Intentando conectar al servidor...")
    if client_identifier:
        print("[CLIENT] Conexión establecida.")
    else:
        print("[CLIENT] Error en la conexión.")
        return

    # Esperar un breve instante para la sincronización de hilos
    time.sleep(1)

    # 5. Prueba de transmisión: Cliente -> Servidor
    payload = b"STARK_PROTOCOL_INIT_01"
    print(f"[CLIENT] Enviando: {payload}")
    transport_layer.send(client_identifier, payload)

    # 6. Prueba de recepción: Servidor lee datos
    time.sleep(0.5)
    received = transport_layer.receive(server_identifier)
    print(f"[SERVER] Recibido: {received}")

    if received == payload:
        print("[SUCCESS] Integridad de datos validada.")
        
        # 7. Respuesta: Servidor -> Cliente
        response = b"STARK_ACK"
        print(f"[SERVER] Enviando respuesta: {response}")
        transport_layer.send(server_identifier, response)
        
        time.sleep(0.5)
        client_received = transport_layer.receive(client_identifier)
        print(f"[CLIENT] Recibido del servidor: {client_received}")
    else:
        print("[FAILURE] Error en la integridad o recepción de datos.")

    # 8. Cierre de sesión
    print("[TEST] Finalizando prueba...")
    transport_layer.disconnect(client_identifier)
    transport_layer.disconnect(server_identifier)

if __name__ == "__main__":
    run_stark_test()