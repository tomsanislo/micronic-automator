# echo_client.py
import socket

host = '169.254.88.108'
port = 10005                   # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.sendall(str.encode('startcapping\r\n'))
data = s.recv(1024)
datadecode = data.decode('ascii')
s.close()
print('Received', str(datadecode))

