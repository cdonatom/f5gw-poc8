#!/usr/bin/env python

import socket
import mysql.connector
import thread
import time
import math

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
            time.sleep(0.5)
        
if __name__ == '__main__':
    posGat = PositionGathering()
    thread.start_new_thread(posGat.threadRoutine, ())
    while True:
        time.sleep(1)
        print "Main Thread: "+str(posGat.distance)
