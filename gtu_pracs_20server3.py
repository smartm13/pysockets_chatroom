import socket
import threading
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 999
max_users=1
chunkSize=1024
serversocket.bind((host, port))
serversocket.listen(max_users)
#roomsg contains all data {room:{mem:{who:readMsgsIndex},msgs:[allmsgs]}}
roomsg=dict()
def welcome():
	global roomsg
	ret="Welcome to ChatRoom app."
	ret+="\nPlz type exit at any point to exit"
	ret+="\nAvailable rooms:"
	ret+="\n{}".format("\n".join(roomsg.keys()) or "None[create one!]")
	ret+="\nEnter room name to enter OR enter New room to create:"
	return ret
def enterroom(who,room):
	global roomsg
	if room in roomsg:
		roomsg[room]['mem'][who]=0
		roomsg[room]['msgs'].append("New member added {}.".format(who))
	else:
		roomsg[room]=dict()
		roomsg[room]['msgs']=["Welcome to {} created by {}".format(room,who)]
		roomsg[room]['mem']={who:0}
def talkroom(toroom,msgby,msg):
	global roomsg
	if msg.strip():
		roomsg[toroom]['msgs'].append("@{}: {}".format(msgby,msg))
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
	def recv(self):
		try:msg=self.cs.recv(chunkSize).decode('ascii')
		except:msg='exit'
		if msg.lower().strip()=='exit':
			try:self.send('--close-conn--')
			except:pass
		if msg=='--empty-resp--':msg=''
		return msg
	def send(self,data):
		if not data:data='--empty-resp--'
		try:ret=self.cs.send(data.encode('ascii')) or 1
		except:ret=0
		if data=='--close-conn--':
			ret=0
			try:self.cs.close()
			except:pass
		return ret
	def run(self):
		name=''
		while not name:name=self.send("Your Name:") and self.recv()
		if name=='exit':return
		self.port="{}({})".format(name,self.port)
		room=self.send(welcome()) and self.recv()
		while not room:room=self.send('') and self.recv()
		if room=='exit':return
		enterroom(self.port,room)
		self.send(talkroom(room,self.port,''))
		resp=self.recv()
		while resp.lower().strip()!='exit':
			if not self.send(talkroom(room,self.port,resp)):break
			resp=self.recv()
		talkroom(room,self.port,"\b\b left the room.")
		self.send('--close-conn--')

threads=[]
while True:
   clientsocket,addr = serversocket.accept()
   print([len(threads)+1],"Starting new thread for",addr)
   threads.append(SubListener(clientsocket,addr[1]))