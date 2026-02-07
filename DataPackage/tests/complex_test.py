import time
import threading
import random
from datapackage import Datapackage

# --- Transporte Simulado con Fragmentación ---
class ShredderTransport:
    def __init__(self):
        self.wire_buffer = b""
        self.lock = threading.Lock()

    def write(self, data: bytes) -> bool:
        with self.lock:
            # Simulamos que el cable recibe los bytes
            self.wire_buffer += data
        return True

    def read(self) -> bytes:
        with self.lock:
            if not self.wire_buffer:
                return b""
            
            # TRITURADORA: Devolvemos un trozo aleatorio de 1 a 10 bytes
            size = random.randint(1, 10)
            chunk = self.wire_buffer[:size]
            self.wire_buffer = self.wire_buffer[size:]
            return chunk

# --- Lógica del Test ---

def producer(dp: Datapackage, thread_id: int, count: int):
    for i in range(count):
        payload = {
            "origin": f"thread_{thread_id}",
            "seq": i,
            "data": "A" * random.randint(10, 50), # Carga variable
            "ts": time.time()
        }
        dp.send_datapackage(payload)
        time.sleep(0.001) # Ráfaga rápida

def stress_test():
    transport = ShredderTransport()
    # Inyectamos los métodos del objeto transport
    dp = Datapackage(write_function=transport.write, read_function=transport.read)
    
    num_threads = 5
    packets_per_thread = 50
    total_expected = num_threads * packets_per_thread
    
    print(f"[*] Iniciando Test de Estrés: {num_threads} hilos, {total_expected} paquetes totales.")
    print("[*] El transporte fragmentará los paquetes en trozos de 1-10 bytes...")

    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=producer, args=(dp, i, packets_per_thread))
        threads.append(t)
        t.start()

    # Recepción y validación
    received_count = 0
    start_time = time.time()
    
    while received_count < total_expected:
        packet = dp.receive_datapackage(timeout=5)
        if packet:
            received_count += 1
            if received_count % 50 == 0:
                print(f"[+] Recibidos {received_count}/{total_expected}...")
        else:
            print("[!] ERROR: Timeout alcanzado. Paquetes perdidos o buffer corrupto.")
            break

    duration = time.time() - start_time
    print(f"\n[!] RESULTADOS:")
    print(f"    - Tiempo total: {duration:.2f} segundos")
    print(f"    - Paquetes procesados: {received_count}")
    print(f"    - Tasa de éxito: {(received_count/total_expected)*100}%")

    dp.stop()

if __name__ == "__main__":
    stress_test()