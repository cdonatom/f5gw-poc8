USRP_DEV="serial=30AD308"
USRP_DEV="serial=30AD345"
USRP_DEV="serial=$1"
port=$2
#while [ 1 ]; do ./srsLTE/build/srslte/examples/pdsch_ue -a $USRP_DEV -f 2437e6 -r 1234 -u 2001 -U 127.0.0.1; sleep 1; done
#while [ 1 ]; do ./srsLTE/build/srslte/examples/pdsch_ue -f 2437e6 -r 1234 -s 2001 -S 127.0.0.1; sleep 1; done

#./srsLTE/build/srslte/examples/pdsch_ue -a $USRP_DEV -f 2437e6 -r 1234 -u 2001 -U 127.0.0.1
./srsLTE/build/srslte/examples/pdsch_ue -a $USRP_DEV -f 2437e6 -r 1234 -u $port -U 127.0.0.1
