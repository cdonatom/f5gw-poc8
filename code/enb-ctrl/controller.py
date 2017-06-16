#!/usr/bin/env python

import socket
import mysql.connector
import thread
import time
import math

THRESHOLD_DIST = 5
COUNTER_NEAR = 3
COUNTER_FAR = 10

PORT_TRIGGER = 3000

class PositionGathering:

    def __init__(self):
        self.cnx = mysql.connector.connect( user='cdonato', password='cdonato123', host='172.16.14.10', database='tofwlan')
        self.cursor = self.cnx.cursor()
        self.distance = 0

    def gatherDistance(self):
        query = "SELECT x_coor, y_coor FROM users WHERE Model = %s"
        self.cursor.execute(query,('atheros',))
        for (x_coor, y_coor) in self.cursor:
            lastX = x_coor
            lastY = y_coor

        query = "SELECT x_coor, y_coor FROM users WHERE Username = %s"
        self.cursor.execute(query,('Alix Carlos',))
        for (x_coor, y_coor) in self.cursor:
            refX = x_coor
            refY = y_coor

        self.distance = math.sqrt( math.pow((lastX - refX), 2 ) + math.pow((lastY - refY), 2 ))

    def threadRoutine(self):
        while True:
            self.gatherDistance()
            print "Thread: "+str(self.distance)
            time.sleep(0.2)
        
if __name__ == '__main__':

    posGat = PositionGathering()
    thread.start_new_thread(posGat.threadRoutine, ())
    counter_near = 0
    counter_far = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    trigger_sent = False

    while True:
        time.sleep(0.2)
        print "Main Thread: "+str(posGat.distance)

        if self.distance <= THRESHOLD_DIST:
            counter += 1

            if counter >= COUNTER_NEAR and trigger_sent is False:
                for i in range(3):
                    s.sendto('TRIGGER', ('127.0.0.1', PORT_TRIGGER))
                    time.sleep(0.1)
                trigger_sent = True

        else:
            if trigger_sent is True:
                counter_far += 1

                if counter_far >= COUNTER_FAR:
                    trigger_sent = False
                    for i in range(3):
                        s.sendto('DISABLE', ('127.0.0.1', PORT_TRIGGER))
                    time.sleep(0.1)
