import socket
import json
import subprocess
from ctrl_config import *
import thread



perl_cmd="\
#!/usr/bin/perl \n\
use strict; \n\
use warnings; \n\
use Time::HiRes; \n\
my $reporting_interval = 1.0; # seconds \n\
my $bytes_this_interval = 0; \n\
my $start_time = [Time::HiRes::gettimeofday()]; \n\
STDOUT->autoflush(1); \n\
while (<>) { \n\
  if (/ length (\d+):/) { \n\
    $bytes_this_interval += $1; \n\
    my $elapsed_seconds = Time::HiRes::tv_interval($start_time); \n\
    if ($elapsed_seconds > $reporting_interval) { \n\
       my $bps = $bytes_this_interval / $elapsed_seconds; \n\
       $bps*=8; \n\
       printf \"%10.2f\n\",$bps; \n\
       $start_time = [Time::HiRes::gettimeofday()]; \n\
       $bytes_this_interval = 0; \n\
    }\n\
  }\n\
}"
perl_script = open("/tmp/netbps","w")
perl_script.write(perl_cmd)
perl_script.close()


type_id='iperf_ue1'

def execute_cmd(cmd,sh=False):
    if sh:
	popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True,shell=True)
    else:
	popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

def iperf_server(x):
        iperf_port=2001
        cmd = ['iperf', '-s', '-p',str(iperf_port),'-i','1','-y', 'C']
        msg={}
        for path in execute_cmd(cmd):
                iperf_res=path.split(',')
#		print iperf_res
#               msg['type']=type_id
#                msg['thr']=iperf_res[8]
#                jmsg=json.dumps(msg)

                # forward to UDP socket
                #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                #sock.sendto(jmsg, ('10.8.19.1',10001))
                #sock.sendto(jmsg, ('10.8.9.13',10001))

def sniffer_server(x):
	cmd = "tcpdump -i lo tcp port 2001 -tt -l -n -e | perl /tmp/netbps"
	msg={}
	for path in execute_cmd(cmd,True):
		iperf_res=path.split(',')
		print iperf_res
                msg['type']=type_id
		msg['thr']=iperf_res[0]
		jmsg=json.dumps(msg)

		# forward to UDP socket
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(jmsg, (IP_CONTROLLER,AP_TO_CTRL_PORT))





#MAIN

thread.start_new_thread(sniffer_server,(1,))
thread.start_new_thread(iperf_server,(1,))
while True:
	pass
