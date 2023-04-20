import socket                

s = socket.socket()          

port = 12345                

s.connect(('192.168.1.136', port)) 
msg = "My name is Anmol"
s.send(msg.encode()) 

s.close() 