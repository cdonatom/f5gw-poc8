import serial
import time
import socket
import thread
import json
import os
import sys
import bluetooth._bluetooth as bluez
import subprocess
import os, os.path
from threading import *

port='/dev/ttyUSB0'
rate=115200
info='test'
info=0;
T=5
TYPE='lte'
adv_name='lte,0,0,0'
UNIX_OUT="/tmp/ble_stats"

def run_bluez_discovery(dev):
	discovery_timeout=1
	global adv_name
	ii=0
        while True:
                try:
			#out=run_command_with_timeout('./bluez-test-discovery',discovery_timeout);
			p=subprocess.Popen("timeout {} ./bluez-test-discovery".format(discovery_timeout),stdout=subprocess.PIPE,shell=True)
			out, err = p.communicate()
			if os.path.exists(UNIX_OUT):
				try:
					client = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
					client.connect(UNIX_OUT)
					client.send(str(out))
					client.close()
				except Exception, e:
					print e



			cmd="hciconfig {0} reset; sleep 0.2; ./ibeacon ; sleep 0.2; hciconfig {0} name '{1}'".format(dev,adv_name)
			os.system(cmd)
			cmd="hciconfig {0} reset; sleep 0.2; ./ibeacon ; sleep 0.2; hciconfig {0} name '{1}'".format(dev,adv_name)
			os.system(cmd)

                except KeyboardInterrupt:
                        # quit
			return


def update_tx_lte_stats(x):
	global adv_name
	if os.path.exists( "/tmp/ble_adv_name" ):
		  os.remove( "/tmp/ble_adv_name" )

	print "Opening socket..."
	server = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
	server.bind("/tmp/ble_adv_name")
	
	while True:
		try:
			data, addr = server.recvfrom(1024) # buffer size is 1024 bytes

			data = data.replace('\r', '').replace('\n', '').replace(' ','').replace('\0','')
			lte_json=json.loads(str(data))
			adv_name='{},{},{},{}'.format(TYPE,lte_json['UE_ID'],int(lte_json['SNR']),int(lte_json['PDSCH-BLER']))
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
		except Exception, e:
			print e

def ibeacon_stats(iface="hci0"):
	if not os.geteuid() == 0:
	    sys.exit('Script must be run as root')
	print "---------------------------------------"
	print "UDP output on unix socket".format(UNIX_OUT)
	print "---------------------------------------"
	thread.start_new_thread(run_bluez_discovery,(iface,))
	thread.start_new_thread(update_tx_lte_stats,(-1,))
	while True:
		time.sleep(1)
