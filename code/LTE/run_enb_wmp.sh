USRP_DEV="serial=30AD345"
tx_pattern="1,1,1,1,1,1,0,0,0,0"
./srsLTE/build/srslte/examples/pdsch_enodeb -a $USRP_DEV -f 2437e6 -g 90 -l 0.8 -m 28 -u 2000 -b f -w $tx_pattern
