from ble.ibeacon_handler import *
import time
import thread
import os
import socket
import json

thread.start_new_thread(ibeacon_stats,('hci0','mixed'))

if os.path.exists( "/tmp/ble_stats" ):
  os.remove( "/tmp/ble_stats" )

print "Opening socket..."
server = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
server.bind("/tmp/ble_stats")

rssi_av=0
alpha=0.7
first_round=True
while True:
  datagram = server.recv( 1024 )
  if not datagram:
    continue
  else:
    #got BLE data consume it...
    try:
      data=json.loads(datagram)
      if "lte" in str(data):
	      print "LTE={}".format(data)
	      if data['RSSI']:
		  if first_round:
			rssi_av=data['RSSI']
			first_round=False
		  else:
			rssi_av=alpha*float(data['RSSI'])+(1-alpha)*float(rssi_av)
		  print "rssi_av={} rssi_now={}".format(rssi_av,data['RSSI'])
      else:
       	      print "ibeacon not contains LTE stats"
    except Exception, e:
      print e
      continue
server.close()
os.remove( "/tmp/ble_stats" )
print "Done"
