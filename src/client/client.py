import socket

from ..server import msgs
from typing import Any, TypedDict, TypeGuard, Literal



def send_to(msg):
    server_addr = ("192.168.1.10", 80007)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(server_addr)

    data = msgs.encode(msg)
    s.sendto(data)
    s.close()

    

        

