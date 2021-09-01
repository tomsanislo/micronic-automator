# echo_client.py
import socket

host = '169.254.140.234'
port = 10005
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.sendall(str.encode('startdepping\r\n'))
data = s.recv(1024)
datadecode = data.decode('ascii')
s.close()
print('Received', str(datadecode))
