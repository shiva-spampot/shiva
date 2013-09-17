#!/bin/bash -e

# Installs SHIVA
# Tested on Ubuntu 12.04 & 13.04 and Mint 15

printf "\nWelcome to the SHIVA's Installer!\n\n"
printf "
 ######  ##     ## #### ##     ##    ###    
##    ## ##     ##  ##  ##     ##   ## ##   
##       ##     ##  ##  ##     ##  ##   ##  
 ######  #########  ##  ##     ## ##     ## 
      ## ##     ##  ##   ##   ##  ######### 
##    ## ##     ##  ##    ## ##   ##     ## 
 ######  ##     ## ####    ###    ##     ## 
 
"
read -p "Press enter to continue installation...";                                                


WORK_PATH=$(pwd)
mkdir -p shiva
INSTALL_PATH=$WORK_PATH/shiva

function prerequisites() {
    printf "\n\n[*] Checking for the prerequisites in system.\n"
    pkgs=("python" "exim4-daemon-light" "g++" "python-virtualenv" "python-dev" "libmysqlclient-dev")
    
    PKG_STATUS=0
    for pkg in "${pkgs[@]}"
    do
        dpkg -s $pkg &> /dev/null
        RETVAL=$?
        if (($RETVAL != 0))
        then
            printf " $pkg not found.\n"
            PKG_STATUS=1
        else
            printf "$pkg found\n"
        fi  
    done
    
    if (($PKG_STATUS == 0))
    then
        printf "\n[*] Checking for dependencies, done!\n"
    else
        die "Some packages are missing. Install them and re-run this script."
    fi

}

function dbcreate() {
    printf "\nDo you wish to setup local databases for storing spam? "
    read -p "[Y]es/[N]o... " choice
    case $choice in
        [Yy]*) sed -i 's/localdb : False/localdb : True/g' $INSTALL_PATH/shiva.conf
               printf "\n[*] Steps to setup local databases."
               printf "\n\t[+] Make sure you've 'mysql-client' and 'mysql-server' installed."
               printf "\n\t[+] Install MySQL-python package by \"sudo pip install MySQL-python\""
               printf "\n\t[+] Edit the shiva/shiva.conf file and"
               printf "\n\t    provide neccesary connection parameters in 'database' section."
               printf "\n\t[+] Execute dbcreate.py in shiva folder as \"python dbcreate.py\"\n"
               read -p "Press enter to continue installation...";;
               
        [Nn]*) printf "\n[*]Set \"localdb : False\" in shiva.conf.\n";
               read -p "Press enter to continue installation...";;
        
        *) die "Wrong choice!"
    esac
}

function helpers() {
    printf "\n\n[*] Copying helper files.\n"
    cp -v $WORK_PATH/helpers/dbcreate.py $INSTALL_PATH/
    cp -v $WORK_PATH/helpers/maindb.sql $INSTALL_PATH/
    cp -v $WORK_PATH/helpers/shiva.conf $INSTALL_PATH/
    cp -v $WORK_PATH/helpers/tempdb.sql $INSTALL_PATH/
    cp -v $WORK_PATH/helpers/setup_exim4.sh $INSTALL_PATH/ 
}

function receiver() {
    printf "\n\n[*] Setting up SMTP Receiver!\n"
    
    cd $INSTALL_PATH
    printf "\n[+] Creating Virtual Environment."
    virtualenv ShivaReceiver
    cd ShivaReceiver
    source bin/activate
    
    printf "\n[+] Installing Lamson and creating project.\n"
    easy_install -U distribute
    pip install lamson
    lamson gen -project Receiver
    
    printf "\n[+] Copying neccesary files.\n"
    cp -v $WORK_PATH/receiver/core/encoding.py $INSTALL_PATH/ShivaReceiver/lib/python2.7/site-packages/lamson/
    cp -v $WORK_PATH/receiver/core/queue.py $INSTALL_PATH/ShivaReceiver/lib/python2.7/site-packages/lamson/
    cp -v $WORK_PATH/receiver/core/server.py $INSTALL_PATH/ShivaReceiver/lib/python2.7/site-packages/lamson/
    cp -v $WORK_PATH/receiver/core/smtpd.py $INSTALL_PATH/ShivaReceiver/lib/python2.7/site-packages/lamson/
    
    cp -v $WORK_PATH/receiver/config/boot.py $INSTALL_PATH/ShivaReceiver/Receiver/config/
    cp -v $WORK_PATH/receiver/config/settings.py $INSTALL_PATH/ShivaReceiver/Receiver/config/

    cp -v $WORK_PATH/receiver/handlers/forward.py $INSTALL_PATH/ShivaReceiver/Receiver/app/handlers
    cp -v $WORK_PATH/receiver/handlers/log.py $INSTALL_PATH/ShivaReceiver/Receiver/app/handlers/
    cp -v $WORK_PATH/receiver/handlers/queue.py $INSTALL_PATH/ShivaReceiver/Receiver/app/handlers/
    cp -v $WORK_PATH/receiver/handlers/spampot.py $INSTALL_PATH/ShivaReceiver/Receiver/app/handlers/
    
    cp -v $WORK_PATH/helpers/clearlogs.sh $INSTALL_PATH/ShivaReceiver/Receiver/logs/
    
    printf "[*] Setting up Shiva Receiver done!\n"
    deactivate
}

function analyzer() {
    printf "\n\n[*] Setting up SMTP Analyzer!"
    
    cd $INSTALL_PATH
    printf "\n[+] Creating Virtual Environment."
    virtualenv ShivaAnalyzer
    cd ShivaAnalyzer
    source bin/activate
    
    printf "\n[+] Installing Lamson and creating project."
    pip install lamson
    lamson gen -project Analyzer
    
    printf "\n[+] Installing required python modules.\n"
    easy_install -U distribute
    pip install cython
    pip install apscheduler
    pip install MySQL-python
    pip install ssdeep
    
    printf "\n[+] Copying neccesary files."
    cp -v $WORK_PATH/analyzer/core/server.py $INSTALL_PATH/ShivaAnalyzer/lib/python2.7/site-packages/lamson/
    cp -v $WORK_PATH/analyzer/core/shiva*.py $INSTALL_PATH/ShivaAnalyzer/lib/python2.7/site-packages/lamson/
    
    mkdir -p $INSTALL_PATH/ShivaAnalyzer/lib/python2.7/site-packages/lamson/hpfeeds/
    cp -v $WORK_PATH/hpfeeds/* $INSTALL_PATH/ShivaAnalyzer/lib/python2.7/site-packages/lamson/hpfeeds/
    
    cp -v $WORK_PATH/analyzer/config/boot.py $INSTALL_PATH/ShivaAnalyzer/Analyzer/config/
    cp -v $WORK_PATH/analyzer/config/settings.py $INSTALL_PATH/ShivaAnalyzer/Analyzer/config/
    
    cp -v $WORK_PATH/helpers/clearlogs.sh $INSTALL_PATH/ShivaAnalyzer/Analyzer/logs/
    
    printf "\n[*] Setting up Shiva Analyzer done!\n"
    deactivate
}

function create_dirs() {
    printf "\n\n[*] Created necessary folders and updated configuration file.!\n"

    mkdir $INSTALL_PATH/queue 
    mkdir $INSTALL_PATH/queue/new
    mkdir $INSTALL_PATH/queue/cur
    mkdir $INSTALL_PATH/queue/tmp
    mkdir $INSTALL_PATH/distorted
    mkdir $INSTALL_PATH/attachments
    mkdir $INSTALL_PATH/attachments/inlines
    mkdir $INSTALL_PATH/rawspams
    
    ESCAPED_PATH=$(echo $INSTALL_PATH | sed -s 's/\//\\\//g')
    
    # Now changing the paths in shiva.conf
    sed -i "s/queuepath : somepath/queuepath : $ESCAPED_PATH\/queue\//g" $INSTALL_PATH/shiva.conf
    sed -i "s/undeliverable_path : somepath/undeliverable_path : $ESCAPED_PATH\/distorted\//g" $INSTALL_PATH/shiva.conf
    sed -i "s/rawspampath : somepath/rawspampath : $ESCAPED_PATH\/rawspams\//g" $INSTALL_PATH/shiva.conf
    sed -i "s/attachpath : somepath/attachpath : $ESCAPED_PATH\/attachments\//g" $INSTALL_PATH/shiva.conf
    sed -i "s/inlinepath : somepath/inlinepath : $ESCAPED_PATH\/attachments\/inlines\//g" $INSTALL_PATH/shiva.conf
}

function die() {
    printf "\n\e[1;31m[!] Error!\e[0m $1\n"
    exit 1
}

prerequisites
sleep 2
helpers
sleep 2
dbcreate
sleep 2
receiver
sleep 2
analyzer
sleep 2 
create_dirs