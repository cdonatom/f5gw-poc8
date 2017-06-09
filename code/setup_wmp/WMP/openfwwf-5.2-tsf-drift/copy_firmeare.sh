#!/bin/sh

set -x
make clean 
make 

#scp *.fw domenico@lab.tti.unipa.it:/tmp
#ssh domenico@lab.tti.unipa.it "scp /tmp/*.fw root@alix2:/lib/firmware/b43"

scp *.fw root@alix03:/lib/firmware/b43/
#scp *.fw root@alix04:/lib/firmware/b43/
#scp *.fw root@alix05:/lib/firmware/b43/
#scp *.fw root@alix10:/lib/firmware/b43/
#scp *.fw root@alix11:/lib/firmware/b43/
#scp *.fw root@alix12:/lib/firmware/b43/
#scp *.fw root@alix17:/lib/firmware/b43/
#scp *.fw root@alix18:/lib/firmware/b43/
#scp *.fw root@alix19:/lib/firmware/b43/
set +x

