import serial
import time
import socket
import thread
import random
import json
import os
import sys
import bluetooth._bluetooth as bluez
import subprocess

UDP_IP = "127.0.0.1"
UDP_INPUT_PORT = 9999
UDP_OUTPUT_PORT = 5055
port='/dev/ttyUSB0'
rate=115200
info='test'
info=0;
T=5
tsleep=0.2
TYPE='lte'
DEBUG=True
UE_ID=2
#input: LTE stats json
#output: enforce new TST sensor name
adv_name='lte,0,0,0'


def run_bluez_discovety(dev,ue_id):
	discovery_timeout=4
	global adv_name
	ii=0
        while True:
                try:
                        cmd='timeout {} ./bluez-test-discovery'.format(discovery_timeout)
                        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
                        out = p.stderr.read()
			if out:
				print out
                        ii=ii+1
			cmd="hciconfig {0} reset; sleep 0.2; ./ibeacon ; sleep 0.2; hciconfig {0} name '{1}'".format(dev,adv_name)
			os.system(cmd)
			cmd="hciconfig {0} reset; sleep 0.2; ./ibeacon ; sleep 0.2; hciconfig {0} name '{1}'".format(dev,adv_name)
			os.system(cmd)

                except KeyboardInterrupt:
                        # quit
			return

def update_tx_lte_stats(ue_id):
	global adv_name

	sock_in = socket.socket(socket.AF_INET, # Internet
		     socket.SOCK_DGRAM) # UDP
	sock_in.bind((UDP_IP, UDP_INPUT_PORT))
	
	while True:
		data, addr = sock_in.recvfrom(1024) # buffer size is 1024 bytes
		lte_json=json.loads(data)

		tx_lte_stats={'type':TYPE,'ue_id':ue_id, 'snr':int(lte_json['SNR']) , 'bler':int(lte_json['PDSCH-BLER'])}
		
		adv_name='{},{},{},{}'.format(tx_lte_stats['type'],tx_lte_stats['ue_id'],tx_lte_stats['snr'],tx_lte_stats['bler'])
		"""
		if (t_stop-t_start) >= T:
			print adv_name
			os.system("hciconfig hci0 reset; ./ibeacon ; hciconfig hci0 name '{}'".format(adv_name))
			
			#ser = serial.Serial(port, rate, timeout=1)
			#ser.write('0');
			#time.sleep(tsleep)
			#ser.write('{},{},{},{}'.format(tx_lte_stats['type'],tx_lte_stats['ue_id'],tx_lte_stats['snr'],tx_lte_stats['bler']));
			#time.sleep(tsleep)
			##print ser.read(1024);
			##time.sleep(tsleep)
			
			t_start=time.time()
			t_stop=t_start;

		"""


def rx_ibeacon_info(x):
	dev='hci0'
	global adv_name_, adv_name
	while True:
		t_start=time.time()
		t_stop=t_start
		if (t_stop-t_start) >= T and adv_name_ != adv_name:
			print adv_name
			print adv_name_
			#print "new lte stats, update"
			#os.system("hciconfig hci0 reset; ./ibeacon ; hciconfig hci0 name '{}'".format(adv_name))
			#time.sleep(0.5)
			#os.system("hciconfig hci0 reset; ./ibeacon ; hciconfig hci0 name '{}'".format(adv_name))
			adv_name_=adv_name
			t_stop=time.time()
			print t_stop-t_start

		#GET STA INFO and NAME
		os.system('hciconfig {0} reset'.format(dev))
		sta_info=get_sta_info(dev);
		print "-------------"
		print sta_info
		print "-------------"
		
		os.system('hciconfig {0} reset'.format(dev))
		#time.sleep(0.2)
		#GET POWER INFO
		rssi_info=get_rssi_info()
		print "==========="
		print rssi_info
		print "==========="

		#parse data in single data struct
		rx_lte_stats = parse_ble_info(sta_info,rssi_info) 
		print "************"
		print rx_lte_stats
		print "************"
		
		#Report lte stats via UDP socket
		#print json.dumps(rx_lte_stats)
		if rx_lte_stats:
			sock_out = socket.socket(socket.AF_INET, # Internet
				     socket.SOCK_DGRAM) # UDP
			sock_out.sendto(json.dumps(rx_lte_stats), (UDP_IP, UDP_OUTPUT_PORT))

def ibeacon_stats(ue_id):
	if not os.geteuid() == 0:
	    sys.exit('Script must be run as root')
	print "---------------------------------------"
	print "UDP output on port {}".format(UDP_OUTPUT_PORT)
	print "---------------------------------------"
	thread.start_new_thread(run_bluez_discovety,('hci0',ue_id,))
	thread.start_new_thread(update_tx_lte_stats,(1,))
	while True:
		time.sleep(1)
