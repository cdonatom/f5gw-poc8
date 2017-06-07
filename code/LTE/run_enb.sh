#USRP_DEV="serial=30AD308"
#USRP_DEV="serial=30AD345"
if [ $# -lt 4 ]; then
	echo "usage:sh run_enb.sh <SERIAL-USRP> <TX_PATTERN> <PRB> <FREQ>"
	exit
fi
USRP_DEV="serial=$1"
#tx_pattern="1,1,1,1,1,1,0,0,0,0"
tx_pattern=$2
PRB=$3
gain=90
freq=$4 #5000e6

cmd="./srsLTE/build/srslte/examples/pdsch_enodeb -a $USRP_DEV -f $freq -p $PRB -g $gain -l 0.7 -m 28 -u 2000 -b f -w $tx_pattern"
echo "-----------------"
echo $cmd
echo "-----------------"
$cmd
