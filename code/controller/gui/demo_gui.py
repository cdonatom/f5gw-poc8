__author__ = 'fabrizio'

from Tkinter import *
import ttk
from PIL import Image, ImageTk
import decimal

import random
from socket import *    # import *, but we'll avoid name conflict
from sys import argv, exit
#import demjson
import json
import signal

import subprocess
#import webbrowser
import urllib2
import base64
import StringIO
import io
import urllib
import zmq
from urllib2 import urlopen, Request, URLError
import time
import os
import thread

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import numpy
from ctrl_config import *

import socket

print ">>>>>>>> {}".format(IP_CONTROLLER)

starttime=time.time()

SUNKABLE_BUTTON = 'SunkableButton.TButton'

DELAY = 1000
uhd_error=False

FREQ=2437e6
AP='alix14'
STA='alix16'
WIFI_CHANNEL=6
demo_dir='~/f5gw-poc8/code/controller'
py_cmd='python'

#demo_dir='/Users/fabrizio/ownCloudUNIPA/work/Flex5Gware/integrated_demo'
#py_cmd='/System/Library/Frameworks/Python.framework/Versions/2.7/bin/python2.7'

usrp_fig_location='/tmp/usrp.png'

def check_error_on_log_file(filename, ccommand):
	sleep_time=1
	global uhd_error
	while True:
		try:
			f = subprocess.Popen(['tail','-n 2',filename],stdout=subprocess.PIPE).communicate()[0]

			pp=str.split(str(f),'\n')
			if 'UHD Error' in str(pp):
				uhd_error=True
			else: 
				uhd_error=False

			if uhd_error:
				closeall()
				os.system(ccommand)
		except Exception:
			pass

		sys.stdout.flush()
		time.sleep(5)
def closeall():
	#KILL lte controller
	cmd="kill -9 $(ps aux | grep uhd_rx_cfile | awk '{ print $2}')"
	print "==================================="
	print cmd
	print "==================================="
	os.system(cmd)


def handle_ctrl_c(signal, frame):
	print "Got ctrl+c, going down!"
	closeall()
	stopWifiTraffic()
	sys.exit(0)

def on_closing():
	print "CLOSE..."
        closeall()
	command="sh {}/killall.sh".format(demo_dir)
        local_command=command;
        os.system(local_command)

        root.destroy()





class Adder(ttk.Frame):
    """The adders gui and functions."""
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        self.init_gui()

    def on_quit(self):
        """Exits program."""
        quit()

    def calculate(self):
        """Calculates the sum of the two inputted numbers."""
        num1 = int(self.num1_entry.get())
        num2 = int(self.num2_entry.get())
        num3 = num1 + num2
        self.answer_label['text'] = num3

    def centreWindow(self):
        w = 1400
        h = 1024
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        #x = (sw - w)/2
        #y = (sh - h)/2
        x = 0
        y = 0 #(sh - h)
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))


    def stopWifiTraffic(self):
        command = 'fab -f {}/fab_wmp_lte.py -u root -H {},{} stop_iperf'.format(demo_dir,AP,STA)
	local_command='{} > /tmp/iperf_client.log 1>&2 &'.format(command);
	os.system(local_command)
        self.startWifiTrafficBtn.state(['!pressed', '!disabled'])
        self.stopWifiTrafficBtn.state(['pressed', 'disabled'])

    def startWifiTraffic(self):
        command_server = 'fab -f {}/fab_wmp_lte.py -u root -H {} start_iperf_server'.format(demo_dir,AP)
	command_client='fab -f {}/fab_wmp_lte.py -u root -H {} start_iperf_client:{},60000,10M,1111111111'.format(demo_dir,STA,AP)

	local_command='{} > /tmp/iperf_server.log 1>&2 &'.format(command_server);
	os.system(local_command)
	local_command='{} > /tmp/iperf_client.log 1>&2 &'.format(command_client);
	os.system(local_command)


	print "start Traffic"
	sys.stdout.flush()
        self.startWifiTrafficBtn.state(['pressed', 'disabled'])
        self.stopWifiTrafficBtn.state(['!pressed', '!disabled'])

    def setupWiFi(self):
	#os.system('cd {}; sh run_wifi.sh'.format(demo_dir))
        command_setup = 'fab -f {0}/fab_wmp_lte.py -u root -H {1},{2} setup_testbed:{1}'.format(demo_dir,AP,STA)
	command_network = 'fab -f {0}/fab_wmp_lte.py -u root -H {1},{2} network:{1},{3}'.format(demo_dir,AP,STA,WIFI_CHANNEL)
	print command_network
        command_load = 'fab -f {}/fab_wmp_lte.py -u root -H {} load_active_radio_program'.format(demo_dir,STA)
	#SETUP TESTBED
	local_command='{}'.format(command_setup);
	os.system(local_command)
	#    create network
	local_command='{}'.format(command_network);
	os.system(local_command)
	#    load correct radio program
	local_command='{}'.format(command_load);
	os.system(local_command)

    def startControllerLTE(self,enable_controller,blank_subframes):
	print "blank_subframes={}".format(blank_subframes)
	mjson={'xfsm':enable_controller,'EST_SLOT':blank_subframes}
	MESSAGE = json.dumps(mjson)
	print MESSAGE

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.sendto(MESSAGE, (IP_ETH_AP, CTRL_TO_AP_PORT))
	sock.close()
	"""
	command="sh {}/kill_proc.sh".format(demo_dir)
	local_command=command;
	os.system(local_command)

	#start controllerLTE
	command='fab -f {}/fab_wmp_lte.py -u root -H {} controllerLTE:{}'.format(demo_dir,STA,enable_controller)
	#local_command='{} 1>&2 &'.format(command)
	local_command='{} > /dev/null 2>&1 &'.format(command)
	os.system(local_command)

	#start syncAP
	if enable_controller=='1': #only if TDMA+LTE
		command='fab -f {}/fab_wmp_lte.py -u root -H {} syncAP'.format(demo_dir,AP)
		local_command='{} > /dev/null 2>&1 &'.format(command)
		#local_command='{} 1>&2 &'.format(command)
		os.system(local_command)

	if enable_controller=='1':
		self.startControllerLTEBtn.state(['pressed', 'disabled'])
		self.disableControllerLTEBtn.state(['!pressed', '!disabled'])
		self.dcfControllerLTEBtn.state(['!pressed', '!disabled'])
	if enable_controller=='0':
		self.startControllerLTEBtn.state(['!pressed', '!disabled'])
		self.disableControllerLTEBtn.state(['pressed', 'disabled'])
		self.dcfControllerLTEBtn.state(['!pressed', '!disabled'])
	
	if enable_controller=='2':
		self.disableControllerLTEBtn.state(['!pressed', '!disabled'])
		self.startControllerLTEBtn.state(['!pressed', '!disabled'])
		self.dcfControllerLTEBtn.state(['pressed', 'disabled'])
		self.killControllerLTEBtn.state(['!pressed', '!disabled'])
	"""
	
    def killControllerLTE(self):
	command="sh {}/kill_proc.sh".format(demo_dir)
	local_command='{}'.format(command);
	os.system(local_command)

	# RESET WITH FULL TX in ALL SLOTS
	command='fab -f {}/fab_wmp_lte.py -u root -H {} killControllerLTE'.format(demo_dir,STA)
	local_command='{}'.format(command);
	os.system(local_command)

	#self.disableControllerLTEBtn.state(['!pressed', '!disabled'])
	self.startControllerLTEBtn.state(['!pressed', '!disabled'])
	#self.killControllerLTEBtn.state(['!pressed', '!disabled'])

	sys.stdout.flush()

    def startUSRP(self,usrp_serial,samp_rate=20e6,freq=FREQ,plot_w_size=50):
	print "START USRP"
	closeall()
	print "CLOSE ALL"
	# USRP
	#usrp_serial="30AD308"
	#usrp_serial="30AD345"
	#usrp_serial="860"
	nsamp=round(2*decimal.Decimal(self.plot_w_size.get())*decimal.Decimal('1e-3') * decimal.Decimal(self.samp_rate.get()))
	print "nsamp={}".format(nsamp)

	command="{} {}/pyUsrpTracker/uhd_rx_cfile \
		--args=serial={} --samp-rate {} -f {} -g 28 -s -N {} --plotwindowsize {} /tmp/usrp.raw --plotfigout {}".format(py_cmd,demo_dir,usrp_serial,samp_rate,freq,nsamp,plot_w_size,usrp_fig_location)
	local_command='{} > /tmp/uhd_rx_cfile.log 2>&1 &'.format(command);
	print local_command
	os.system(local_command)

#    	thread.start_new_thread(check_error_on_log_file,('/tmp/demo_controller.err', local_command) )
	print "CHANGE BUTTON STATES"
        self.startUSRPBtn.state(['pressed', 'disabled'])
        self.stopUSRPBtn.state(['!pressed', '!disabled'])
	self.Frequency.configure(state='disabled')
	self.WindowSize.configure(state='disabled')

    def stopUSRP(self):
	print "STOP USRP"
	closeall()

        self.startUSRPBtn.state(['!pressed', '!disabled'])
        self.stopUSRPBtn.state(['pressed', 'disabled'])
	self.Frequency.configure(state='normal')
	self.WindowSize.configure(state='normal')

    def set_xy(self,thr,DT,x,y):
	xx=[]
	yy=[]

	xx = list( numpy.array(x) + DT)
	xx.insert(0,0)
	xx=xx[0:self.Nplot]

	y.append( numpy.nan_to_num( thr ) )
	yy=y[::-1]
	yy=yy[0:self.Nplot]
	yy=yy[::-1]
	return xx,yy

    def ewma(self,y,y_,a):
	return a*y +(1-a)*y_

    def loop_statistics(self,x):
	init_plot_success_rate=True;
	init_plot_iperf=True;
	global line_psucc_wifi;
	alpha=0.7
	psucc=0;
	psucc_=0
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((IP_CONTROLLER,AP_TO_CTRL_PORT))

	t0_ue1_stats=time.time()
	t1_ue1_stats=time.time()

	t0_iperf_ue1=time.time()
	t1_iperf_ue1=time.time()

	t0_ue2_stats=time.time()
	t1_ue2_stats=time.time()

	t0_iperf_ue2=time.time()
	t1_iperf_ue2=time.time()

	t0_ue3_stats=time.time()
	t1_ue3_stats=time.time()

	t0_iperf_ue3=time.time()
	t1_iperf_ue3=time.time()
	
	bler_ue1_=0
	bler_ue1=0
	thr_ue1_=0
	thr_ue1=0

	bler_ue2_=0
	bler_ue2=0

	thr_ue2_=0
	thr_ue2=0

	psucc_=0
	psucc=0

	thr_wmp_=0
	thr_wmp=0

	MAX_LTE_THR=18;

	while True:
		try:
			data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
			stats=json.loads(data)
			if stats['type']=='iperf_wmp':
				t1_iperf_ue3=time.time()
				DT=t1_iperf_ue3-t0_iperf_ue3
				t0_iperf_ue3=time.time()
				try:
					thr_wmp_=thr_wmp
					thr_wmp=float(stats.get('thr'))*100/(3.80*1e6)
					if numpy.isnan(thr_wmp):
						thr_wmp=float(0);
					thr_wmp=self.ewma(thr_wmp,thr_wmp_,0.7)
					self.xval_thr_wmp,self.yval_thr_wmp=self.set_xy(thr_wmp,DT,self.xval_thr_wmp,self.yval_thr_wmp)
						
				except Exception as e:
					print e

			if stats['type']=='iperf_ue1':
				t1_iperf_ue1=time.time()
				DT=t1_iperf_ue1-t0_iperf_ue1
				t0_iperf_ue1=time.time()
				try:
					thr_ue1_=thr_ue1
					thr_ue1=15+float(stats.get('thr'))*100/(MAX_LTE_THR*1e6)
					if numpy.isnan(thr_ue1):
						thr_ue1=float(0);
					thr_ue1=self.ewma(thr_ue1,thr_ue1_,0.7)
					if numpy.isnan(thr_ue1):
						thr_ue1=float(0);
					self.xval_thr_ue1,self.yval_thr_ue1=self.set_xy(thr_ue1,DT,self.xval_thr_ue1,self.yval_thr_ue1)
						
				except Exception as e:
					print e

			if stats['type']=='iperf_ue2':
				print stats
				t1_iperf_ue2=time.time()
				DT=t1_iperf_ue2-t0_iperf_ue2
				t0_iperf_ue2=time.time()
				try:
					thr_ue2_=thr_ue2
					thr_ue2=15+float(stats.get('thr'))*100/(MAX_LTE_THR*1e6)
					if numpy.isnan(thr_ue2):
						thr_ue2=float(0);
					thr_ue2=self.ewma(thr_ue2,thr_ue2_,0.7)
					self.xval_thr_ue2,self.yval_thr_ue2=self.set_xy(thr_ue2,DT,self.xval_thr_ue2,self.yval_thr_ue2)
						
				except Exception as e:
					print e


			if stats['type']=='ue1_stats':
				t1_ue1_stats=time.time()
				DT=t1_ue1_stats-t0_ue1_stats
				t0_ue1_stats=time.time()
				try:
					bler_ue1_=bler_ue1
					bler_ue1=stats.get('PDSCH-BLER')/float(100)
					bler_ue1=self.ewma(bler_ue1,bler_ue1_,0.7)

					self.blsuccLabel.config(text="1 - PDSCH-BLER={}".format(str(1 - bler_ue1)))
					self.xval_blsucc_lte_ue1,self.yval_blsucc_lte_ue1=self.set_xy((1-bler_ue1),DT,self.xval_blsucc_lte_ue1,self.yval_blsucc_lte_ue1)

				except Exception as e:
					print e

			if stats['type']=='ue2_stats':
				t1_ue2_stats=time.time()
				DT=t1_ue2_stats-t0_ue2_stats
				t0_ue2_stats=time.time()
				try:
					bler_ue2_=bler_ue2
					bler_ue2=stats.get('PDSCH-BLER')/float(100)
					bler_ue2=self.ewma(bler_ue2,bler_ue2_,0.7)

					self.blsuccLabel.config(text="1 - PDSCH-BLER={}".format(str(1 - bler_ue2)))
					self.xval_blsucc_lte_ue2,self.yval_blsucc_lte_ue2=self.set_xy((1-bler_ue2),DT,self.xval_blsucc_lte_ue2,self.yval_blsucc_lte_ue2)

				except Exception as e:
					print e

			if stats['type']=='ue3_stats':
				t1_ue3_stats=time.time()
				DT=t1_ue3_stats-t0_ue3_stats
				t0_ue3_stats=time.time()
				try:
					psucc_=psucc
					psucc=float(stats.get('psucc'));
					if numpy.isnan(psucc):
						psucc=float(0);
					psucc=self.ewma(psucc,psucc_,0.7)
					self.psuccLabel.config(text="PSUCC={}".format(str(stats.get('psucc'))))
					self.maskLabel.config(text="MASK={}".format(str(stats.get('mask'))))

					self.xval_psucc_wifi,self.yval_psucc_wifi=self.set_xy(psucc,DT,self.xval_psucc_wifi,self.yval_psucc_wifi)

				except Exception as e:
					print e
			#PRINT IPERF 
			if stats['type']=='iperf_ue1' or stats['type']=='iperf_ue2' or stats['type']=='iperf_wmp':
				try:
					thr_aggr = numpy.array(self.yval_thr_ue1[::-1]) + numpy.array(self.yval_thr_wmp[::-1])
#					print "X={}".format(len(self.xval_thr_ue1[0:self.Nplot]))
#					print "X={}".format(-1*numpy.array(self.xval_thr_ue1[0:self.Nplot]))
#					print "X={}".format(-1*numpy.array(self.xval))
#					print "Y={}".format(len(self.yval_thr_ue1[::-1]))
#					print "Y={}".format(self.yval_thr_ue1[::-1])
					if init_plot_iperf:
						f_iperf = Figure(figsize=(10.5,2.2), dpi=100)
						ax = f_iperf.add_subplot(111)
						ax.grid(True)
						ax.set_xlabel('Time [s]')
						ax.set_ylabel('Throughput')

						self.tick=(self.tick+1) % self.Nplot
						line_thr_wmp, = ax.plot(-1*numpy.array(self.xval_thr_wmp),self.yval_thr_wmp[::-1],label="WMP THR")
						line_thr_ue1,   = ax.plot(-1*numpy.array(self.xval_thr_ue1),self.yval_thr_ue1[::-1],label="UE1 THR")
						line_thr_ue2,   = ax.plot(-1*numpy.array(self.xval_thr_ue2),self.yval_thr_ue2[::-1],label="UE2 THR")
						ax.set_ylim([0, 100])
						ax.set_xlim([-1*600, 0])
						ax.patch.set_facecolor('white')
						f_iperf.set_facecolor('white')

						canvas = FigureCanvasTkAgg(f_iperf, self.ue_traffic_frame)
						canvas.show()
						canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
						canvas.get_tk_widget().grid(column=1, row=3, columnspan=1, sticky='nesw')
						ax.legend(loc="lower left")
					else: 
						line_thr_wmp.set_xdata(-1*numpy.array(self.xval_thr_wmp))
						line_thr_wmp.set_ydata(self.yval_thr_wmp[::-1])

						line_thr_ue1.set_ydata(self.yval_thr_ue1[::-1])
						line_thr_ue1.set_xdata(-1*numpy.array(self.xval_thr_ue1))

						line_thr_ue2.set_ydata(self.yval_thr_ue2[::-1])
						line_thr_ue2.set_xdata(-1*numpy.array(self.xval_thr_ue2))
						f_iperf.canvas.draw()

					init_plot_iperf = False;

				except Exception as e:
					print e
			#PRINT SUCCESS STATS
			if stats['type']=='ue3_stats' or stats['type']=='ue2_stats' or stats['type']=='ue1_stats':
				try:
					if init_plot_success_rate:
						f = Figure(figsize=(10.5,2.2), dpi=100)
						ax = f.add_subplot(111)
						ax.grid(True)
						ax.set_xlabel('Time [s]')
						ax.set_ylabel('SUCCESS RATE')

						self.tick=(self.tick+1) % self.Nplot
						line_psucc_wifi,     = ax.plot(-1*numpy.array(self.xval_psucc_wifi)    ,self.yval_psucc_wifi[::-1]    ,label="WIFI")
						line_bler_lte_ue1,   = ax.plot(-1*numpy.array(self.xval_blsucc_lte_ue1),self.yval_blsucc_lte_ue1[::-1],label="LTE UE1")
						line_bler_lte_ue2,   = ax.plot(-1*numpy.array(self.xval_blsucc_lte_ue2),self.yval_blsucc_lte_ue2[::-1],label="LTE UE2")
						ax.set_ylim([0, 1])
						ax.patch.set_facecolor('white')
						f.set_facecolor('white')

						canvas = FigureCanvasTkAgg(f, self.ue_stats_frame)
						canvas.show()
						canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
						canvas.get_tk_widget().grid(column=1, row=4, columnspan=1, sticky='nesw')
						ax.legend(loc="lower left")
					else: 
						line_psucc_wifi.set_ydata(self.yval_psucc_wifi[::-1])
						line_bler_lte_ue1.set_ydata(self.yval_blsucc_lte_ue1[::-1])
						line_bler_lte_ue2.set_ydata(self.yval_blsucc_lte_ue2[::-1])
						f.canvas.draw()

					init_plot_success_rate = False;

				except Exception as e:
					print e

		except Exception as e:
			print e

	"""
	while True:
		command = 'tail -n1 /tmp/controllerLTE.log'
		proc=subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
		(out_wifi, err) = proc.communicate()
#		command = 'tail -n1 /tmp/lte_ue.json'
#		proc=subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
#		(out_lte, err) = proc.communicate()

		try:
			stats = json.loads(out_wifi)
#			stats_lte = json.loads(out_lte)
#			print "------------------------------"
#			print stats_lte
#			print stats
#			print "------------------------------"
			psucc=float(stats.get('psucc'));
			if numpy.isnan(psucc):
                                psucc=float(0);
			#psucc_=alpha*psucc+(1-alpha)*psucc_
			#psucc=psucc_

			self.yval_psucc_wifi.append( numpy.nan_to_num( psucc ) )
#			self.yval_bler_lte.append( 1 - stats_lte.get('PDSCH-BLER')/float(100) )

			yy=self.yval_psucc_wifi[::-1]
			yy=yy[0:self.Nplot]
			self.yval_psucc_wifi=yy[::-1]

#			yy=self.yval_bler_lte[::-1]
#			yy=yy[0:self.Nplot]
#			self.yval_bler_lte=yy[::-1]
			if init_plot:
				f = Figure(figsize=(5,2.9), dpi=100)
				ax = f.add_subplot(111)
				ax.grid(True)
				ax.set_xlabel('Time [s]')
				ax.set_ylabel('SUCCESS RATE')

				self.tick=(self.tick+1) % self.Nplot
				line_psucc_wifi, = ax.plot(self.xval,self.yval_psucc_wifi[::-1],label="WIFI success rate")
				#line_bler_lte,   = ax.plot(self.xval,self.yval_bler_lte[::-1],label="LTE Block success rate")
				ax.set_ylim([0, 1])
				ax.patch.set_facecolor('white')
				f.set_facecolor('white')

				canvas = FigureCanvasTkAgg(f, self)
				canvas.show()
				canvas.get_tk_widget().configure(background='white',  highlightcolor='white', highlightbackground='white')
				canvas.get_tk_widget().grid(column=1, row=3, columnspan=1, sticky='nesw')
				ax.legend(loc="lower right")
			else: 
				line_psucc_wifi.set_ydata(self.yval_psucc_wifi[::-1])
				#line_bler_lte.set_ydata(self.yval_bler_lte[::-1])
				f.canvas.draw()

			init_plot = False;

		except Exception as e:
			print e

		time.sleep(1)
	"""
		

    def loopUSRPCapture(self,x):
#        location='http://127.0.0.1:8484/5gppp_demo/plots/usrp.png'
	location=usrp_fig_location;
	print location
	while True:
		try:
			fd = urllib.urlopen(location)
			imgFile = io.BytesIO(fd.read())
			im = ImageTk.PhotoImage(Image.open(imgFile))
			label_usrp = Label(self.channel_frame, image=im)
			label_usrp.image = im
			label_usrp.grid(row=0,column=0, sticky=W+E)
		except Exception as e:
		    print e
		    pass
		time.sleep(1)

    def stats_update(self,x):
	while True:
		command = 'tail -n1 /tmp/controllerLTE.log'
		#ssh_command='ssh fabrizio@lab.tti.unipa.it \"ssh fabrizio@hendrix.local \'{}\' \"'.format(command);
		try:
			proc=subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
			(out_wifi, err) = proc.communicate()
			#command = 'tail -n1 /tmp/lte_ue.json'
			#proc=subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
			#(out_lte, err) = proc.communicate()
			#proc=subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
			stats = json.loads(out_wifi)
			#stats_lte = json.loads(out_lte)

			self.psuccLabel.config(text="PSUCC={}".format(str(stats.get('psucc'))))
			#self.blsuccLabel.config(text="PDSCH-BLER={}".format(str(stats_lte.get('PDSCH-BLER'))))
			self.maskLabel.config(text="MASK={}".format(str(stats.get('mask'))))
		except Exception as e:
			print e
			pass
		time.sleep(1)

    def init_yvals(self):
	self.yval_thr_wmp=[0 for x in range(0,self.Nplot)]
	self.xval_thr_wmp=[x for x in range(0,self.Nplot)]
	self.yval_thr_ue1=[0 for x in range(0,self.Nplot)]
	self.xval_thr_ue1=[x for x in range(0,self.Nplot)]
	self.yval_thr_ue2=[0 for x in range(0,self.Nplot)]
	self.xval_thr_ue2=[x for x in range(0,self.Nplot)]
	self.yval_psucc_wifi=[0 for x in range(0,self.Nplot)]
	self.xval_psucc_wifi=[x for x in range(0,self.Nplot)]
	self.yval_blsucc_lte_ue1=[0 for x in range(0,self.Nplot)]
	self.xval_blsucc_lte_ue1=[x for x in range(0,self.Nplot)]
	self.yval_blsucc_lte_ue2=[0 for x in range(0,self.Nplot)]
	self.xval_blsucc_lte_ue2=[x for x in range(0,self.Nplot)]

    def init_gui(self):

        """Builds GUI."""
        print('GUI setup')
	self.psucc=0
	self.mask=1111111111
	self.bler="0"
        self.root.title('5GPPP DEMO Flex5Gware')
        self.root.option_add('*tearOff', 'FALSE')

        self.parent = self.root
        self.root.title("5GPPP DEMO Flex5Gware")
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.centreWindow()
        self.pack(fill=BOTH, expand=1)

        self.grid(column=0, row=0, sticky='nsew')

        self.menubar = Menu(self.root)

        self.menu_file = Menu(self.menubar)
        self.menu_file.add_command(label='Exit', command=self.on_quit)

        self.menu_edit = Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_file, label='File')
        self.menubar.add_cascade(menu=self.menu_edit, label='Edit')

        self.root.config(menu=self.menubar)

        #USRP FRAME
        self.usrp_frame = ttk.LabelFrame(self, text='USRP', height=100, width=100)
        self.usrp_frame.grid(column=0, row=1, columnspan=1, sticky='nesw')

        self.plot_w_size=StringVar(value=40);
        self.LabelWindowSize = Label(self.usrp_frame, text="Window Size [ms]", bg="lightgrey")
	self.LabelWindowSize.grid(row=0, column=0, sticky=W+E)
	self.WindowSize=Entry(self.usrp_frame,textvariable=self.plot_w_size)
        self.WindowSize.grid(row=0, column=1, padx=5, pady=5, ipady=2, sticky=W)

	self.freq=StringVar(value=FREQ)
        self.LabelFrequency = Label(self.usrp_frame, text="Frequency [Hz]",bg="lightgrey")
	self.LabelFrequency.grid(row=1, column=0, sticky=W+E)
	self.Frequency=Entry(self.usrp_frame,textvariable=self.freq)
        self.Frequency.grid(row=1, column=1, padx=5, pady=5, ipady=2, sticky=W)


	self.usrp_serial="30AD308"
#	self.usrp_serial="30AD345"
#	self.usrp_serial="860"
	self.samp_rate=StringVar(value=20e6)
	

        self.startUSRPBtn = ttk.Button(self.usrp_frame, text="START USRP", width=10, command=lambda: self.startUSRP(self.usrp_serial,decimal.Decimal(self.samp_rate.get()),decimal.Decimal(self.freq.get()),decimal.Decimal(self.plot_w_size.get())),style=SUNKABLE_BUTTON)

        self.startUSRPBtn.grid(row=2, column=0, padx=15, pady=15, ipady=2, sticky=W)
        self.stopUSRPBtn = ttk.Button(self.usrp_frame, text="STOP USRP", width=10, command=self.stopUSRP,  style=SUNKABLE_BUTTON)
        self.stopUSRPBtn.grid(row=2, column=1, padx=15, pady=15, ipady=2, sticky=W)

        self.info_frame = ttk.LabelFrame(self.usrp_frame, text='USRP SAMPLING INFO', height=100, width=100)
        self.info_frame.grid(column=0, row=3, columnspan=1, sticky='nesw')

	self.settings_usrp="usrp_serial={}\nsamp_rate={}\n".format(self.usrp_serial,self.samp_rate.get());	
        self.LabelSettingInfos = Label(self.info_frame, text=self.settings_usrp,bg="lightgrey")
	self.LabelSettingInfos.grid(column=0,row=1,sticky=W)

        #CHANNEL FRAME
        self.channel_frame = ttk.LabelFrame(self, text='Channel occupation', height=100, width=100)
        self.channel_frame.grid(column=1, row=1, columnspan=1, sticky='nesw')

	thread.start_new_thread(self.loop_statistics,(1,))

	# Statistics Frame
	
	self.stats_frame = ttk.LabelFrame(self, text='Monitor info', height=100, width=100)
        self.stats_frame.grid(column=0, row=2, columnspan=1, sticky='nesw')
	self.psuccLabel=Label(self.stats_frame, text="PSUCC={}".format(self.psucc))
	self.psuccLabel.grid(column=0,row=1,sticky=W)
	self.maskLabel=Label(self.stats_frame, text="MASK={}".format(self.mask))
	self.maskLabel.grid(column=0,row=2,sticky=W)
	self.blsuccLabel=Label(self.stats_frame, text="PDSCH-BLER={}".format(self.bler))
	self.blsuccLabel.grid(column=0,row=3,sticky=W)

        self.ue_stats_frame = ttk.LabelFrame(self, text='SUCCESS RATE', height=100, width=100)
        self.ue_stats_frame.grid(column=1, row=2, columnspan=1, sticky='nesw')
        self.ue_traffic_frame = ttk.LabelFrame(self, text='PERFORMANCE', height=100, width=100)
        self.ue_traffic_frame.grid(column=1, row=3, columnspan=1, sticky='nesw')

	self.wmp_frame = ttk.LabelFrame(self, text='PLOT CONTROL', height=100, width=100)
        self.wmp_frame.grid(column=1, row=4, columnspan=1, sticky='nesw')
        self.cleanPlotBtn = ttk.Button(self.wmp_frame, text="CLEAN PLOTS", width=15, command=self.init_yvals,  style=SUNKABLE_BUTTON)
        self.cleanPlotBtn.grid(row=1, column=1, padx=15, pady=15, ipady=2, sticky=W)

	#Traffic Frame
	self.wmp_frame=ttk.LabelFrame(self, text='WMP STATE MACHINE ENFORCEMENT', height=100, width=100)
        self.wmp_frame.grid(column=0, row=3, columnspan=1, sticky='nesw')


	list_subframes=[x for x in range(1,11)]
	self.blankframes = StringVar(value=list_subframes[3])
        self.subframes = OptionMenu(self.wmp_frame, self.blankframes, *list_subframes)
	self.subframes.configure(state="active")
        self.subframes.grid(row=1, column=1, padx=15, pady=15, ipady=2, sticky=W)

        self.startControllerLTEBtn = ttk.Button(self.wmp_frame, text="TDMA+LTEcoex", width=15, command=lambda: self.startControllerLTE('2',self.blankframes.get()),  style=SUNKABLE_BUTTON)
        self.startControllerLTEBtn.grid(row=2, column=1, padx=15, pady=15, ipady=2, sticky=W)
        self.dcfControllerLTEBtn = ttk.Button(self.wmp_frame, text="DCF", width=15, command=lambda: self.startControllerLTE('1',0),  style=SUNKABLE_BUTTON)
        self.dcfControllerLTEBtn.grid(row=2, column=3, padx=15, pady=15, ipady=2, sticky=W)
#	self.topo_frame=ttk.LabelFrame(self, text="Network Scenario", height=100, width=90)
#        self.topo_frame.grid(column=0, row=4, columnspan=1, sticky='nesw')
	


#	wpercent=50
#	basewidth = 350
#	img=Image.open('topology.png')
#	wpercent = (basewidth/float(img.size[0]))
#	hsize = int((float(img.size[1])*float(wpercent)))
#	img = img.resize((basewidth,hsize), Image.ANTIALIAS)
	
#	im = ImageTk.PhotoImage(img)
#	label_topo_img = Label(self.topo_frame, image=im)
#	label_topo_img.image = im
#	label_topo_img.grid(row=0,column=0, sticky=W+E)
	
	


	self.stopUSRP()
	#self.stopWifiTraffic()
	self.killControllerLTE()



#        self.loopUSRPCapture()
	self.Nplot=600
        self.init_yvals()
	self.xval=[x for x in range(0,self.Nplot)]
	self.tick=0;
        # ttk.Separator(self, orient='horizontal').grid(column=0,
        #         row=1, columnspan=4, sticky='ew')
        #
#	thread.start_new_thread(self.stats_update,(1,))
	thread.start_new_thread(self.loopUSRPCapture,(1,))


        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

		

if __name__ == '__main__':
    root = Tk()
    root.resizable(0,0)
    signal.signal(signal.SIGINT, handle_ctrl_c)
    Adder(root)
    root.lift()
    root.attributes('-topmost',True)
    root.after_idle(root.attributes,'-topmost',False)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
