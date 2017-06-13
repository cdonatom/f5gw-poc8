import socket
import json
import subprocess
import os
def execute_cmd(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
	try:
		raise subprocess.CalledProcessError(return_code, cmd)
	except Exception, e:
		print "ops"
		

def iperf_server(x):
        iperf_port=2001
    #    cmd = ['iperf', '-s', '-p',str(iperf_port),'-i','1','-y', 'C']
	cmd=['iperf', '-c', '127.0.0.1', '-p', '2000', '-i', '1', '-t', '10000', '-y', 'C']
        msg={}
	while True:
		for path in execute_cmd(cmd):
			iperf_res=path.split(',')
			print iperf_res
			if float(iperf_res[7]) < 0:
				print "KILLL"
				os.system("killall -9 iperf")

os.system("killall -9 iperf")
iperf_server(1)
