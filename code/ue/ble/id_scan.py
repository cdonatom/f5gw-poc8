from ble import scan_ble_devices

while True:
	try:
		v=scan_ble_devices('hci0','lte*')
		if v:
			print v[0]
	except Exception, e:
		#print e
		continue
