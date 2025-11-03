import socket
import can
import threading
import logging

# Logging-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s',
    datefmt='%H:%M:%S'
)

# Konfigurationen für Schnittstellen
CONFIGS = [
    {
        "udp_ip": "0.0.0.0",
        "udp_port": 5000,
        "can_interface": "vcan0",
        "udp_dest": ("192.168.1.10", 6000)
    },
    {
        "udp_ip": "0.0.0.0",
        "udp_port": 5001,
        "can_interface": "vcan1",
        "udp_dest": ("192.168.1.11", 6001)
    }
]

def udp_to_can(udp_ip, udp_port, can_interface):
    logging.info(f"[{can_interface}] Starte UDP -> CAN auf {udp_ip}:{udp_port}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))
    bus = can.interface.Bus(channel=can_interface, interface='socketcan')

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            logging.info(f"[{can_interface}] UDP empfangen von {addr}: {data.hex()}")

            if len(data) < 6:
                logging.warning(f"[{can_interface}] Ungültiges Paket (<6 Byte): {data.hex()}")
                continue

            can_id = int.from_bytes(data[0:4], 'big')  # 4 Bytes für Extended ID
            dlc = data[4]
            payload = data[5:]

            if dlc > 8 or len(payload) != dlc:
                logging.warning(f"[{can_interface}] Ungültiger DLC oder Datenlänge stimmt nicht überein")
                continue

            msg = can.Message(
                arbitration_id=can_id,
                is_extended_id=True,
                data=payload
            )
            bus.send(msg)
            logging.info(f"[{can_interface}] CAN gesendet: ID=0x{can_id:X}, DLC={len(payload)}, Daten={payload.hex()}")

        except can.CanError as e:
            logging.error(f"[{can_interface}] CAN-Sende-Fehler: {e}")
        except Exception as e:
            logging.exception(f"[{can_interface}] Allgemeiner Fehler: {e}")

def can_to_udp(can_interface, dest):
    logging.info(f"[{can_interface}] Starte CAN -> UDP an {dest}")
    bus = can.interface.Bus(channel=can_interface, interface='socketcan')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        try:
            msg = bus.recv()
            if msg is None:
                continue

            # UDP-Paketaufbau: 4 Byte ID (little endian), 1 Byte DLC, Payload
            can_id_bytes = msg.arbitration_id.to_bytes(4, 'big')
            dlc_byte = bytes([msg.dlc])
            payload = msg.data
            udp_packet = can_id_bytes + dlc_byte + payload

            sock.sendto(udp_packet, dest)
            logging.info(f"[{can_interface}] UDP gesendet an {dest}: {udp_packet.hex()}")

        except Exception as e:
            logging.exception(f"[{can_interface}] Fehler bei CAN -> UDP: {e}")

def start_threads():
    for config in CONFIGS:
        threading.Thread(
            target=udp_to_can,
            args=(config["udp_ip"], config["udp_port"], config["can_interface"]),
            name=f"UDP2CAN-{config['can_interface']}",
            daemon=True
        ).start()

        threading.Thread(
            target=can_to_udp,
            args=(config["can_interface"], config["udp_dest"]),
            name=f"CAN2UDP-{config['can_interface']}",
            daemon=True
        ).start()

if __name__ == "__main__":
    start_threads()
    logging.info("Alle Threads gestartet. Warte auf Daten ...")
    threading.Event().wait()



