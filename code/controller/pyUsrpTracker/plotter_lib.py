#!/usr/bin/python

import sys, getopt
import numpy as np
import os
import math
from scipy.signal  import butter, lfilter, tf2ss
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt, os, fnmatch
import csv
import time
plt.close('all')
def plotter(inputfile,outputfile,milliseconds,fs=25e6):
	T=int(milliseconds)*1e-3
	#print "fs={}".format(fs)
	Ts = 1./fs
	N = round(T*fs)
	decim=1;
	fix_to_float = 1./(2**4)
	tf=open(inputfile,'r')
	tf.seek(2*N*2, os.SEEK_SET)  # seek
        try:
		with tf as fid:
			print "fs={}".format(fs)
			print "T={}".format(T)
			r = np.fromfile(fid, np.int16).reshape((-1, 2)).T
		#for i in range(0,len(r[0])):
		for i in range(0,10):
			print("I:%d,Q:%d" % (r[0,i],r[1,i]))

		#filtering 
		r2=(fix_to_float*r[0])**2+(fix_to_float*r[1])**2;
		step=0
		print "len(r2)={}".format(len(r2))
		print "N={}".format(N)
		print "r2={}".format(r2)
#		r2=r2[int(step):int(step+N)]
		r2=r2[step:step+int(N)]

		alpha = math.exp(-Ts/0.5e-6);
		#print alpha
		b = [1-alpha];
		a = [1,-alpha];
		r2_red=[];
		r2_filt = lfilter(b, a, r2[0::decim]);
		print len(r2[0::decim]);
		t=np.arange(N)
		#t=np.arange(len(r2[0::decim]))
		t=Ts*t*1e3
		noise=-100

		#plot
		my_dpi=100
		
		width=900
		height=300
		
		
		
		fig = plt.figure()
		ax = fig.add_subplot(111)
		ax.plot(t,10*np.log10(r2_filt)+noise);
		#ax.plot(10*np.log10(r2_filt)+noise);
		ax.grid(True)
		ax.set_xlabel('Time [ms]')
		ax.set_ylabel('RSSI [dBm]')
		ax.set_ylim([-100, -30])
		ax.set_xlim([0, T*1e3])
		fig.set_size_inches(width/my_dpi,height/my_dpi)
		plt.tight_layout()
		#plt.show()
		fig.savefig(outputfile)
		plt.close(fig)
		plt.close('all')
        except Exception ,err:
		print err
		pass

