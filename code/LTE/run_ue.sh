USRP_DEV="serial=30AD308"
USRP_DEV="serial=30AD345"

if [ $# -lt 3 ]; then
	echo "sh run_ue.sh <SERIAL> <PORT> <FREQ>"
	exit
fi

USRP_DEV="serial=$1"
port=$2
freq=$3
./srsLTE/build/srslte/examples/pdsch_ue -a $USRP_DEV -f $freq -r 1234 -u $port -U 127.0.0.1
