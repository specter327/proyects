import socket
from datapackage import Datapackage

def receptor_generico():
    # Configuración de Socket estándar
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', 9999))
    sock.listen(1)
    
    print("[*] Receptor listo. Esperando flujo de bytes en el puerto 9999...")
    conn, addr = sock.accept()
    
    # Inyectamos el socket en nuestra librería
    dp = Datapackage(
        write_function=conn.sendall, 
        read_function=lambda: conn.recv(4096)
    )

    try:
        while True:
            # Recibimos el paquete (bloqueante hasta que llegue uno)
            paquete = dp.receive_datapackage(timeout=20)
            if not paquete: break
            
            print(f"[RECEPTOR] Objeto recibido de {addr}: {paquete}")
            
            # Confirmación genérica
            dp.send_datapackage({"status": "ACK", "received_at": paquete.get("id")})
            
    except KeyboardInterrupt:
        pass
    finally:
        dp.stop()
        conn.close()
        sock.close()

if __name__ == "__main__":
    receptor_generico()