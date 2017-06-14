#!/usr/bin/env python

import socket
import thread
import sys

LOCAL_IP = '127.0.0.1'
FWD_PORT = 2000
LISTEN_PORT = 2001
TRIGGER_PORT = 3000
BUFF_SIZE = 4096

trigger = None

def triggerRoutine():
    # Trigger events
    print "Thread listening"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((LOCAL_IP, TRIGGER_PORT))
    global trigger
    while True:
        data, addr = s.recvfrom(1024)
        if data:
            trigger = data

# Receives data
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((LOCAL_IP, LISTEN_PORT))
print "Waiting for incoming connections"
s.listen(1)
conn, addr = s.accept()

# Sends data
s_rem = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "Connecting to "+LOCAL_IP
s_rem.connect((LOCAL_IP, FWD_PORT))

thread.start_new_thread(triggerRoutine, ())

while True:
    try:
        if trigger is not None:
            print trigger
            s_rem.send(str(trigger))
            trigger = None
        
        data = conn.recv(BUFF_SIZE)
        s_rem.send(data)


    except KeyboardInterrupt:
        sys.exit(0)
        conn.close()
        s_rem.close()