import blescan
import sys
import bluetooth._bluetooth as bluez
import os

dev_id = 0
try:
    sock = bluez.hci_open_dev(dev_id)
    print ("ble thread started")

except:
    print ("error accessing bluetooth device...")
    sys.exit(1)


print(sock)
blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

"""
DEVICES = {'df:0a:6f:3c:43:23': {'name': 'AP1-DCF', 'rx_pw': 0}, 'f4:42:57:94:a8:a6': {'name': 'AP2-TDMA', 'rx_pw': 0 }}
best_ap_={'': { 'rx_pw':-100}};
best_ap={'': { 'rx_pw':-100}};
"""
while True:
#	best_ap={'': { 'rx_pw':-100}};
	returnedList = blescan.parse_events(sock, 10)
	for found in returnedList:
		ibcn = found.split(',')
		print ibcn

#		if DEVICES.get(ibcn[0]):
#			DEVICES.get(ibcn[0]).update({'rx_pw':float(ibcn[5])})
#		if best_ap.get('rx_pw') < DEVICES.get(ibcn[0]).get('rx_pw'):
#			best_ap=DEVICES.get(ibcn[0])
#	if best_ap_ != best_ap:
#		print("Cambia AP")
#		if best_ap.get('name') == "AP1-DCF":
#			os.system("~/alix_tools/bytecode-manager -a 1")
#	
#	if best_ap.get('name') == "AP2-TDMA":
#		os.system("~/alix_tools/bytecode-manager -a 2")
    #else:
    #print "Stesso AP"
    #print best_ap
    #os.system("bytecode-manager -v | grep CURRENT")
#	best_ap_=best_ap;
