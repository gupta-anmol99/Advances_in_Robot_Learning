import socket

from ..server import msgs
from typing import Any, TypedDict, TypeGuard, Literal



def send_to(msg):

    if msgs.is_status_req(msg):
        server_addr = ("192.168.1.10", 80007)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(server_addr)

        data = msgs.encode(msg)
        s.sendto(data)
        s.close()

        
        new_addr = ("0.0.0.0", 12345)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(new_addr)

        while True:
            msg_bytes, addr = s.recvfrom(4096)
            status_dict = msgs.decode(msg_bytes)
            return status_dict

    else:
        server_addr = ("192.168.1.10", 80007)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(server_addr)

        data = msgs.encode(msg)
        s.sendto(data)
        s.close()


    

        

