import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 999
chunkSize=1024
try:s.connect((host, port))
except:
	print("No server detected on "+str((host, port)))
	exit()
while True:
	try:
		msg = s.recv(chunkSize).decode('ascii')
		if msg=='--empty-resp--':msg=""
		if msg=='--close-conn--':break
		if msg and not msg.endswith('\n'):msg+='\n'
		s.send(input(msg+'>').encode('ascii') or b'--empty-resp--')
	except:break
s.close()
