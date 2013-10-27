#!/bin/bash
source ../bin/activate

# There is a bug at the receiver end, which is yet to be fixed. Probably lamson doesn't breaks the network connections after they are done.
# Hence, gradually the total number of connections in "established" state reaches ~1020 and system stops accepting connections at TCP port 25.
# Following is a dirty fix to restart "receiver" every xx minutes to clear connections
restart_receiver () {

    lamson stop -ALL run
    sleep 30

    #cd logs
    #bash clearlogs.sh
    #cd ..

    echo -e "\n\t[+] scheduler script stopped SHIVA-receiver"
    echo -en "\t[+] number of established connection before stopping receiver: "
    netstat -natp | grep -i estab | wc -l
    echo -e "\t[+] attempting to restart receiver....."
    
    lamson start -FORCE
    
    if [ $? != 0 ]; then
	echo -e "\t[-] Error: Most probably TCP port 25 is engaged...sleeping for 30 seconds before reattempting\n"
	sleep 30
	restart_receiver
    fi
}

restart_receiver