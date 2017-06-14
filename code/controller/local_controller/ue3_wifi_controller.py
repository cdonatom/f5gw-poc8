#!/usr/bin/env python

import SocketServer
import socket
import os
import numpy
import os.path
import datetime
import random
from StringIO import StringIO
import json
import time
import subprocess
from ctrl_config import *

import netifaces as ni
import thread
import signal
import sys

BUFFER_SIZE = 1024
enable_controller=1
msg_stats=""
EST_SLOT=4
class MyTCPHandler(SocketServer.BaseRequestHandler):
	
	def handle(self):
		global enable_controller
		global msg_data
		global EST_SLOT
		# self.request is the TCP socket connected to the client
		jmsg_data = self.request.recv(1024).strip()
		data=json.loads(jmsg_data)
		if 'xfsm' in jmsg_data:
			if data['xfsm']:
				print ">>>>> ENABLE {}".format(data['xfsm'])
				enable_controller=str(data['xfsm'])
				os.system('bytecode-manager -a {}'.format(data['xfsm']))
		if 'EST_SLOT' in jmsg_data:
			if data['EST_SLOT']:
				EST_SLOT=int(data['EST_SLOT'])
def shift(l,n):
        return l[n:] + l[:n]

def shm_reader():

	cmd = 'bytecode-manager -x 2 | grep -e 0x00D -e 0x00E -e 0x00F'
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	output = p.stdout.read()
	output=output.replace(":", " ")
	output=output.replace("\t", "")
	output=output.replace("\n", "")
	output=output.replace("\r", "")
	output=output.split(" ")
	output=[x for x in output if 'x' not in x]
	pos=4
	tx_count=[]
	rx_ack_count=[]
	for i in range(0,10):
		val=output[i+4]
		hex_val="0x{}{}".format(val[2:4],val[0:2]);
		val=int(hex_val,16)
		tx_count.append(val)
		val=output[i+14]
		hex_val="0x{}{}".format(val[2:4],val[0:2]);
		val=int(hex_val,16)
		rx_ack_count.append(val)
	tx_count=[float(i) for i in tx_count]
	rx_ack_count=[float(i) for i in rx_ack_count]
	tx_count=numpy.array(tx_count)
	rx_ack_count=numpy.array(rx_ack_count)

        return [tx_count,rx_ack_count]

def update_pattern(mask_int,L,est_slot):
        mask_sum=0
        n_shift=0
        for x in list(mask_int):
                mask_sum+=x

        target_mask= [1]*mask_sum + [0]*(L-mask_sum)

        while n_shift < L:
                if mask_int != target_mask:
                        mask_int=shift(mask_int,-1)
                        n_shift=n_shift+1;
                else:
                        break;

        if n_shift < L:
                if mask_sum < est_slot and est_slot < L:

                        for i_mask in range(mask_sum,est_slot):
                                mask_int[i_mask]=1

                mask_int=shift(mask_int,n_shift-(mask_sum-est_slot))
        return mask_int

def controllerLTE(x=1):
	global enable_controller
	global msg_stats
	print "test"
	fh = StringIO();
	[tx_count_,rx_ack_count_]=shm_reader();
	count_round=0

	if enable_controller=='1':
		os.system('bytecode-manager -a 1 > /dev/null')
	else:
		os.system('bytecode-manager -a 2 > /dev/null')
		os.system('bytecode-manager --set-tdma-mask 1111111111 > /dev/null')
	while True:
		count_round=count_round+1
		[tx_count,rx_ack_count]=shm_reader();
		dtx=numpy.mod(tx_count-tx_count_,0xFFFF)
		dack=numpy.mod(rx_ack_count-rx_ack_count_,0xFFFF)
		tx_count_=tx_count
		rx_ack_count_=rx_ack_count
		if max(dtx) < 10:
			dack = numpy.zeros(len(dack))	
		psucc=numpy.divide(dack,dtx)
		print dtx
		print dack
		for i in range(0,len(psucc)):
			if numpy.isinf(psucc[i]):
				psucc[i]=0;
				continue
			if numpy.isnan(psucc[i]):
				psucc[i]=0;
				continue

		psucc_tot=numpy.divide(numpy.sum(dack),numpy.sum(dtx))
		numpy.set_printoptions(precision=1)
		
		mask=""
		for x in psucc:
			if x > 0.5:
				maskval=1
			elif numpy.isinf(x):
				maskval=0
			else:
				maskval=0

			mask="{}{}".format(maskval,mask)
			mask_int = [ int(x) for x in list(mask)]
		mask_sum=0
		for x in list(mask_int):
			mask_sum+=x

		if mask=="0000000000":
			mask="1111111111"		
		L=10
		p_insert=numpy.random.rand();
		if mask_sum < EST_SLOT:
			p_insert=1;
			mask_int=update_pattern(mask_int,L,mask_sum+1)
		mask=""
		for x in mask_int:
			mask="{}{}".format(mask,x)

		if enable_controller=='3':
			mask="1111111111"
		
		if enable_controller == '2' or enable_controller =='3':	
			print mask
			os.system('bytecode-manager --set-tdma-mask {} > /dev/null'.format(mask))
		
		json_msg={ 'type':'ue3_stats', 'time':time.time(), 'psucc':psucc_tot, 'mask':mask,'enable_controller':enable_controller,'mask_sum':mask_sum, 'psucc_list':list(psucc)}
		msg_stats=json.dumps(json_msg)
		#send stats to AP
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((IP_WIFI_AP, UE_TO_AP_PORT))
			s.send(msg_stats)
			s.close()
			print EST_SLOT
		except Exception, e:
			print e
		#send stats to Controller

		time.sleep(1)

def send_stats_tcp(x):
	while True:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((IP_WIFI_AP, UE_TO_AP_PORT))
			s.send(msg_stats)
			s.close()
		except Exception, e:
			print e
		time.sleep(1)
	
def send_stats_udp(x):
	while True:
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			sock.sendto(msg_stats, (IP_CONTROLLER, AP_TO_CTRL_PORT))
			sock.close()
			time.sleep(1)
		except Exception, e:
			print e
	
server=None
def handle_ctrl_c(signal, frame):
        print "Got ctrl+c, going down!"
	try:
		server.server_close()
	except Exception, e:
		print e
	sys.exit(0)

if __name__ == "__main__":
	iface='wlan0'
	ni.ifaddresses(iface)
	signal.signal(signal.SIGINT, handle_ctrl_c)
	HOST=ni.ifaddresses(iface)[2][0]['addr']

	thread.start_new_thread(controllerLTE,(1,)) #init with 1=DCF
	thread.start_new_thread(send_stats_udp,(1,))	
	SocketServer.TCPServer.allow_reuse_address = True
	server = SocketServer.TCPServer((HOST, AP_TO_UE_PORT), MyTCPHandler)

	# Activate the server; this will keep running until you
	# interrupt the program with Ctrl-C
	server.serve_forever()

