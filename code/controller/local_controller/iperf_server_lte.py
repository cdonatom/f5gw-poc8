import socket
import json
import subprocess
def execute_cmd(cmd):
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
		print iperf_res
                msg['type']='iperf_ue1'
                msg['thr']=iperf_res[8]
                jmsg=json.dumps(msg)

                # forward to UDP socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                #sock.sendto(jmsg, ('10.8.19.1',10001))
                sock.sendto(jmsg, ('10.8.9.13',10001))



iperf_server(1)
