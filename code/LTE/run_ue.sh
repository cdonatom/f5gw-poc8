USRP_DEV="serial=30AD308"
USRP_DEV="serial=30AD345"

if [ $# -lt 4 ]; then
	echo "sh run_ue.sh <SERIAL> <PORT> <FREQ> <ue_id>"
	exit
fi

USRP_DEV="serial=$1"
port=$2
freq=$3
ue_id=$4
IP_CONTROLLER=10.8.9.13


cmd="./srsLTE/build/srslte/examples/pdsch_ue -a $USRP_DEV -f $freq -r 1234 -u $port -U 127.0.0.1 -m $ue_id -H $IP_CONTROLLER"
echo "-----------------"
echo $cmd
echo "-----------------"
$cmd
