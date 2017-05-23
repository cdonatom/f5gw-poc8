#!/usr/bin/env python

import socket
import thread
import sys

REM_IP = '127.0.0.1'
TCP_IP = '11.0.0.1'
REM_PORT = 2001
TCP_PORT = 2003
FWD_PORT = 2002

TRIG_PORT = 3000
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

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


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()

s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.bind((REM_IP, REM_PORT))
s2.listen(1)

conn2, addr = s2.accept()

s_rem = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_rem.connect((REM_IP, FWD_PORT))

conn_to_use = conn

thread.start_new_thread(triggerRoutine, (1,))

print 'Connection address:', addr
while 1:
  try:
    if trigger == "D2D":
      conn_to_use = conn
    else:
      conn_to_use = conn2

    data = conn_to_use.recv(BUFFER_SIZE)
#    print data
 #   if not data: print "no data"
    s_rem.send(data)
  except KeyboardInterrupt:
    sys.exit(0)

conn.close()
