#!/bin/bash

#step 1
sed -i -e '32a\daemon_smtp_ports=2500' /etc/exim4/exim4.conf.template

#step 2
sed -i s/dc_eximconfig_configtype=\'local\'/dc_eximconfig_configtype=\'internet\'/ /etc/exim4/update-exim4.conf.conf

#step 3
service exim4 restart
