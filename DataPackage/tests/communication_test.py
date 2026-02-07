import time
from datapackage_messages import Datapackage

# --- Simulación de Transporte (Loopback Buffer) ---
virtual_transport_buffer = b""

def virtual_write(data: bytes) -> bool:
    global virtual_transport_buffer
    # Simulamos el envío agregando bytes al buffer
    virtual_transport_buffer += data
    return True

def virtual_read() -> bytes:
    global virtual_transport_buffer
    # Simulamos la recepción extrayendo y limpiando el buffer
    if not virtual_transport_buffer:
        return b""
    
    data = virtual_transport_buffer
    virtual_transport_buffer = b""
    return data

# --- Lógica de Prueba ---

def run_test():
    print("[*] Iniciando Datapackage en modo Loopback...")
    
    # Instanciamos con las funciones inyectadas
    dp = Datapackage(write_function=virtual_write, read_function=virtual_read)

    # 1. Caso de prueba: Diccionario simple
    test_data = {
        "command": "SHELL_EXEC",
        "args": ["whoami"],
        "id": 1024
    }

    print(f"[>] Enviando paquete: {test_data}")
    if dp.send_datapackage(test_data):
        print("[+] Envío exitoso.")

    # 2. Caso de prueba: Recepción con timeout
    print("[*] Esperando recepción...")
    received_data = dp.receive_datapackage(timeout=2)

    if received_data:
        print(f"[<] Paquete recibido correctamente: {received_data}")
        assert received_data == test_data, "Error: Los datos recibidos no coinciden con los enviados."
        print("[!] Validación de integridad: OK")
    else:
        print("[!] Error: No se recibió el paquete (Timeout).")

    # Limpieza
    dp.stop()
    print("[*] Test finalizado.")

if __name__ == "__main__":
    run_test()