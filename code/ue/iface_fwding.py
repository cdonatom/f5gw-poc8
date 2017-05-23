#!/usr/bin/env python

import socket
import thread

TCP_IP = '127.0.0.1'
REM_IP = '11.0.0.1'
TCP_PORT = 2001
IPERF_PORT = 2002
REM_PORT = 2003
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

data = ""
flag_t1 = False
flag_t2 = False

conn, addr = s.accept()

def sendLTE(x):
  s_iperf = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s_iperf.connect((TCP_IP, IPERF_PORT))
  global flag_t1
  print "Thread 1: sendLTE"
  while True:
    if flag_t1:
      s_iperf.send(data)
      flag_t1 = False

def sendD2D(x):
  s_rem = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s_rem.connect((REM_IP, REM_PORT))
  global flag_t2
  print "Thread 2: sendD2D" 
  while True:
    if flag_t2:
      s_rem.send(data)
      flag_t2 = False

thread.start_new_thread(sendLTE, (1,))
thread.start_new_thread(sendD2D, (1,))

print 'Connection address:', addr
while 1:
    data = conn.recv(BUFFER_SIZE)
    flag_t1 = True
    flag_t2 = True
 #   if not data: print "no data"
 #   s_iperf.send(data)
 #   s_rem.send(data)


conn.close()
