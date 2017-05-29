from ble import scan_ble_devices
dev='hci1'
while True:
	try:
		v=scan_ble_devices(dev,'lte*')
		if v:
			print v[0]
	except Exception, e:
		#print e
		continue
