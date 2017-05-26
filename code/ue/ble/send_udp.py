import socket
import random
import json
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
ue_id='1'

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

snr=random.randint(-100,0)
bler=random.randint(0,100)
mjson={'ue_id':ue_id,'snr':snr,'bler':bler}
MESSAGE = json.dumps(mjson)
print MESSAGE

sock = socket.socket(socket.AF_INET, # Internet
		     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
sock.close()
