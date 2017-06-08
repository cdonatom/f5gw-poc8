AP="alix14"
STA="alix16"
#fw_dir="~/ownCloudTTI/work/Flex5Gware/integrated_demo/WMP/"
fw_dir="/home/fabrizio/f5gw-poc8/code/setup_wmp/WMP/"
#fw_dir="~/ownCloudUNIPA/work/Flex5Gware/integrated_demo/WMP/"
fab -f fab_wmp_lte.py -u root -H $AP,$STA setup_testbed:$AP,$fw_dir
#    create network
fab -f fab_wmp_lte.py -u root -H $AP,$STA network:$AP,6
#    load correct radio program
fab -f fab_wmp_lte.py -u root -H $STA load_active_radio_program
#    run traffic
#fab -f fab_wmp_lte.py -u root -H $AP start_iperf_server
#fab -f fab_wmp_lte.py -u root -H $STA start_iperf_client:$AP,60000,10M,1111111111
#fab -f fab_wmp_lte.py -u root -H $STA,$AP stop_iperf
