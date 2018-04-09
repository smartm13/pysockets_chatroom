import socket
import threading
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 999
max_users=1
chunkSize=1024
serversocket.bind((host, port))
serversocket.listen(max_users)
roomsg=dict()
def welcome():
	global roomsg
	return """Welcome to ChatRoom app.\nPlz type exit at any point to exit\nAvailable rooms:\n{}\nEnter room name to enter OR enter New room to create:""".format("\n".join(roomsg.keys()) or "None[create one!]")
def enterroom(who,room):
	global roomsg
	if room in roomsg:
		roomsg[room]['mem'][who]=0
		roomsg[room]['msgs'].append("New member added to room "+str(who)+".")
	else:
		roomsg[room]=dict()
		roomsg[room]['msgs']=["Welcome to room {} by-{}".format(room,who)]
		roomsg[room]['mem']={who:0}
def welcomeroom(room,who):
	global roomsg
	roomsg[room]['mem'][who]=len(roomsg[room]['msgs'])
	return "\n".join(roomsg[room]['msgs'])
def talkroom(toroom,msgby,msg):
	global roomsg
	if msg!='--empty-resp--':roomsg[toroom]['msgs'].append("@{}: {}".format(msgby,msg))
	resp="\n".join(roomsg[toroom]['msgs'][roomsg[toroom]['mem'][msgby]:])
	roomsg[toroom]['mem'][msgby]=len(roomsg[toroom]['msgs'])
	return resp

class SubListener(object):
	def __init__(self,cs, port):
		self.port = port
		self.cs=cs
		thread = threading.Thread(target=self.run, args=())
		thread.daemon = True
		thread.start()
	def run(self):
		print(id(self),"thread started for",self.port)
		name=self.cs.recv(chunkSize).decode('ascii')
		if name=='exit':
			print(id(self),"closing port and dead",self.port)
			self.cs.send(b'--close-conn--')
			self.cs.close()
			return
		self.port="{}({})".format(name,self.port)
		self.cs.send(welcome().encode('ascii'))
		room=self.cs.recv(chunkSize).decode('ascii')
		if room=='exit':
			print(id(self),"closing port and dead",self.port)
			self.cs.send(b'--close-conn--')
			self.cs.close()
			return
		enterroom(self.port,room)
		self.cs.send(welcomeroom(room,self.port).encode('ascii'))
		try:resp=self.cs.recv(chunkSize).decode('ascii')
		except:resp='exit'
		while resp.lower().strip()!='exit':
			ans=talkroom(room,self.port,resp) or '--empty-resp--'
			print(id(self),"from=",self.port,"got=",resp,"send=",ans)
			self.cs.send(ans.encode('ascii'))
			try:resp=self.cs.recv(chunkSize).decode('ascii')
			except:break
		talkroom(room,self.port,"\b\b just left the room.")
		self.cs.send(b'--close-conn--')
		print(id(self),"closing port",self.port)
		self.cs.close()
		print(id(self),"thread dies",self.port)

listeners=[]
while True:
   # establish a connection
   print("main->listening")
   clientsocket,addr = serversocket.accept()
   print("main->Got a connection from "+str(addr))
   print('main->creating new thread for this connection')
   listeners.append(SubListener(clientsocket,addr[1]))
