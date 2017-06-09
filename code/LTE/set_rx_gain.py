import socket
import os

#!/usr/bin/python

import sys, getopt

UNIX_OUT='/tmp/rx_gain'
def main(argv):
	rxgain = 0
	try:
		opts, args = getopt.getopt(argv,"hg:",["rxgain="])
	except getopt.GetoptError:
		print 'test.py -g <rx_gain= [0=AGC] > '
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'test.py -g <rxgain> '
			sys.exit()
		elif opt in ("-g", "--rxgain"):
			rxgain = arg

	if os.path.exists(UNIX_OUT):
		try:
			client = socket.socket( socket.AF_UNIX, socket.SOCK_DGRAM )
			client.connect(UNIX_OUT)
			out="0"
			client.send(str(rxgain))
			client.close()
		except Exception, e:
			print e
if __name__ == "__main__":
	main(sys.argv[1:])
