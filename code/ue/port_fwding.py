#!/usr/bin/env python

import socket
import thread
import sys

REM_IP = '127.0.0.1'
TCP_IP = '11.0.0.2'
REM_PORT = 2001
TCP_PORT = 2003
FWD_PORT = 2002

TRIG_PORT = 3000
NOT_PORT = 3001
BUFFER_SIZE = 4096 

trigger = "D2D"

def triggerRoutine(x):
  s_trigger = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s_trigger.bind((REM_IP, TRIG_PORT))
  global trigger
  print "Server thread ready"
  while 1:
    trigger, addr = s_trigger.recvfrom(1024)
    if trigger:
      print "Server Thread: flag received"
      print trigger

conn = None
addr = None
conn_to_use = conn

def incomingRoutine():
      global conn
      global trigger
      global addr

      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.bind((TCP_IP, TCP_PORT))
      s.listen(1)
      conn, addr = s.accept()
      trigger ="D2D"


#s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s2.bind((REM_IP, REM_PORT))
#s2.listen(1)

#conn2, addr = s2.accept()

s_rem = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_rem.connect((REM_IP, FWD_PORT))


thread.start_new_thread(triggerRoutine, (1,))
thread.start_new_thread(incomingRoutine, ())

print 'Connection address:', addr
while True:
  try:
    if trigger == "D2D":
      conn_to_use = conn
    else:
      conn_to_use = conn2

    if conn_to_use is None:
      continue

    data = conn_to_use.recv(BUFFER_SIZE)
#    print data
    if not data:
      #conn_to_use = conn2
      print "D2D out!"
      s2.listen(1)
      conn2, addr = s2.accept()
    s_rem.send(data)

    if "TRIGGER" in str(data):
      print "Trigger found!"
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.sendto('TRIGGER', ('127.0.0.1', NOT_PORT))
      s.close()

    if "DISABLE" in str(data):
      print "Disable found!"
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.sendto('DISABLE', ('127.0.0.1', NOT_PORT))
      s.close()

  except KeyboardInterrupt:
    conn.close()
    conn2.close()
    sys.exit(0)

