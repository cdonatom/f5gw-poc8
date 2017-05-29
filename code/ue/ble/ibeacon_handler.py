import serial
import time
import socket
import thread
import random
import json
import os
import blescan
import sys
import bluetooth._bluetooth as bluez
from ble import scan_ble_devices

UDP_IP = "127.0.0.1"
UDP_INPUT_PORT = 5005
UDP_OUTPUT_PORT = 5055
port='/dev/ttyUSB0'
rate=115200
info='test'
info=0;
T=2
tsleep=0.5
TYPE='lte'
DEBUG=True

#input: LTE stats json
#output: enforce new TST sensor name
def update_tx_lte_stats(x):
	sock_in = socket.socket(socket.AF_INET, # Internet
		     socket.SOCK_DGRAM) # UDP
	sock_in.bind((UDP_IP, UDP_INPUT_PORT))
	while True:
		if DEBUG: 
			print "listen..."
		data, addr = sock_in.recvfrom(1024) # buffer size is 1024 bytes
		if DEBUG: 
			print "received message:", data
		tx_lte_stats=json.loads(data)
		if DEBUG: 
			print "received message:", tx_lte_stats
		tx_lte_stats={'type':TYPE,'ue_id':tx_lte_stats['ue_id'], 'snr':tx_lte_stats['snr'] , 'bler':tx_lte_stats['bler']}
		ser = serial.Serial(port, rate, timeout=1)
		ser.write('0');
		time.sleep(tsleep)
		ser.write('{},{},{},{}'.format(tx_lte_stats['type'],tx_lte_stats['ue_id'],tx_lte_stats['snr'],tx_lte_stats['bler']));
		time.sleep(tsleep)
		if DEBUG:
			print ser.read(1024);
			time.sleep(tsleep)

# use bluetooth dongle to receive ibeacon values
# output: list of json, each dict contains:
#		'adddr':sta_i['addr'], 
#		'id':int(lte_info_curr[1]), 
#		'snr':int(lte_info_curr[2]), 
#		'bler':int(lte_info_curr[3]), 
#		'rssi_bcn':int(rssi_i['rssi_bcn'])}

dev='hci0'
def get_sta_info():
	sta_info={}
	try:
		v=scan_ble_devices(dev,'lte*')
		#v=scan_ble_devices('hci0')
		if v:
			#sta_info=v[0]
			sta_info=v
		
	except Exception,e :
		print e
	return sta_info

def get_rssi_info():
	dev_id = 0
	rssi_info=[]
	try:
		sock = bluez.hci_open_dev(dev_id)
		blescan.hci_le_set_scan_parameters(sock)
		blescan.hci_enable_le_scan(sock)
		returnedList = blescan.parse_events(sock, 10)
		for found in returnedList:
			ibcn = found.split(',')
			rssi_dict={'addr':ibcn[0],'rssi_bcn':ibcn[5]}
			rssi_info.append(rssi_dict)
		sock.close()
	except Exception,e :
		print e
	
	return rssi_info

def parse_ble_info(sta_info,rssi_info):
	ret=[]
	match=False
	for rssi_i in rssi_info:
		for sta_i in sta_info:
			if TYPE in sta_i['name'] and str(rssi_i['addr']).upper()== str(sta_i['addr']).upper():
				lte_info_curr=str(sta_i['name']).split(",")
				rx_lte_stat_curr={
					'adddr':sta_i['addr'], 
					'id':int(lte_info_curr[1]), 
					'snr':int(lte_info_curr[2]), 
					'bler':int(lte_info_curr[3]), 
					'rssi_bcn':int(rssi_i['rssi_bcn'])}
				ret.append(rx_lte_stat_curr)
				match=True
		if match:
			break
	return ret
def rx_ibeacon_info(x):

	while True:
		#GET STA INFO and NAME
		sta_info=get_sta_info();
		#if DEBUG:
			#print "-------------"
			#print sta_info
			#print "-------------"
		
		os.system('hciconfig {0} reset'.format(dev))
		time.sleep(0.1)
		#GET POWER INFO
		rssi_info=get_rssi_info()
		#if DEBUG:
			#print "==========="
			#print rssi_info
			#print "==========="
		#parse data in single data struct
		rx_lte_stats = parse_ble_info(sta_info,rssi_info) 
		#if DEBUG:
			#print "************"
			#print rx_lte_stats
			#print "************"
		
		#Report lte stats via UDP socket
		#print json.dumps(rx_lte_stats)
		if rx_lte_stats:
			sock_out = socket.socket(socket.AF_INET, # Internet
				     socket.SOCK_DGRAM) # UDP
			sock_out.sendto(json.dumps(rx_lte_stats), (UDP_IP, UDP_OUTPUT_PORT))

def ibeacon_stats():

	if not os.geteuid() == 0:
	    sys.exit('Script must be run as root')
	print "---------------------------------------"
	print "UDP output on port {}".format(UDP_OUTPUT_PORT)
	print "---------------------------------------"
	thread.start_new_thread(rx_ibeacon_info,(1,))
	thread.start_new_thread(update_tx_lte_stats,(1,))
	while True:
		time.sleep(1)
