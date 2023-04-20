import socket                

s = socket.socket()          
print("Socket successfully created")

port = 12345                

s.bind(('192.168.1.136', port))         
print("socket binded to %s" %(port)) 

s.listen(10)      
print("socket is listening")            

while True: 

   c, addr = s.accept()      
   print('Got connection from', addr)
   print(c)
   msg2 = c.recv(4096)
   print(msg2.decode())
  # msg = 'Thanks from Pratyusha'
  # c.send(msg.encode()) 

  # c.close() 
