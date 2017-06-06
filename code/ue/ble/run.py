import ibeacon_handler
import time
import thread
import os
import socket



thread.start_new_thread(ibeacon_handler.ibeacon_stats,('hci0',))

if os.path.exists( "/tmp/ble_stats" ):
  os.remove( "/tmp/ble_stats" )

print "Opening socket..."
server = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
server.bind("/tmp/ble_stats")

while True:
  datagram = server.recv( 1024 )
  if not datagram:
    continue
  else:
    #got BLE data consume it...
    print datagram
server.close()
os.remove( "/tmp/ble_stats" )
print "Done"

