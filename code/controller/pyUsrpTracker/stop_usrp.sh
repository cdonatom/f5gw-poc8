#! /bin/bash
kill -9 $(ps aux | grep uhd_rx_cfile | awk '{ print $2}')
