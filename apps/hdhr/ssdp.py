import socket
import threading
import time

# SSDP Multicast Address and Port
SSDP_MULTICAST = "239.255.255.250"
SSDP_PORT = 1900

# Server Information
DEVICE_TYPE = "urn:schemas-upnp-org:device:MediaServer:1"
SERVER_IP = "10.0.0.107"  # Replace with your server's IP address
SERVER_PORT = 8000

def ssdp_response(addr):
    """Send an SSDP response to a specific address."""
    response = (
        f"HTTP/1.1 200 OK\r\n"
        f"CACHE-CONTROL: max-age=1800\r\n"
        f"EXT:\r\n"
        f"LOCATION: http://{SERVER_IP}:{SERVER_PORT}/hdhr/device.xml\r\n"
        f"SERVER: Dispatcharr/1.0 UPnP/1.0 HDHomeRun/1.0\r\n"
        f"ST: {DEVICE_TYPE}\r\n"
        f"USN: uuid:device1-1::{DEVICE_TYPE}\r\n"
        f"\r\n"
    )
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.sendto(response.encode("utf-8"), addr)
    sock.close()

def ssdp_listener():
    """Listen for SSDP M-SEARCH requests and respond."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((SSDP_MULTICAST, SSDP_PORT))

    while True:
        data, addr = sock.recvfrom(1024)
        if b"M-SEARCH" in data and DEVICE_TYPE.encode("utf-8") in data:
            print(f"Received M-SEARCH from {addr}")
            ssdp_response(addr)

def ssdp_broadcaster():
    """Broadcast SSDP NOTIFY messages periodically."""
    notify = (
        f"NOTIFY * HTTP/1.1\r\n"
        f"HOST: {SSDP_MULTICAST}:{SSDP_PORT}\r\n"
        f"CACHE-CONTROL: max-age=1800\r\n"
        f"LOCATION: http://{SERVER_IP}:{SERVER_PORT}/hdhr/device.xml\r\n"
        f"SERVER: Dispatcharr/1.0 UPnP/1.0 HDHomeRun/1.0\r\n"
        f"NT: {DEVICE_TYPE}\r\n"
        f"NTS: ssdp:alive\r\n"
        f"USN: uuid:device1-1::{DEVICE_TYPE}\r\n"
        f"\r\n"
    )
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    while True:
        sock.sendto(notify.encode("utf-8"), (SSDP_MULTICAST, SSDP_PORT))
        time.sleep(30)

from django.conf import settings

def start_ssdp():
    """Start SSDP services."""
    global SERVER_IP
    # Dynamically get the IP address of the server
    SERVER_IP = settings.SERVER_IP or "127.0.0.1"  # Default to localhost if not set
    threading.Thread(target=ssdp_listener, daemon=True).start()
    threading.Thread(target=ssdp_broadcaster, daemon=True).start()
    print(f"SSDP services started on {SERVER_IP}.")

