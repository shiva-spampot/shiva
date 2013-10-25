#!/bin/bash -e

# Installs SHIVA
# Tested on Ubuntu 12.04 & 13.04 and Mint 15

clear

banner ()
{
cat << EOF

########################################################################
	      		
			SHIVA Installer Script				
			       Ver 0.2	
                                                             
                        _/        _/                        
               _/_/_/  _/_/_/        _/      _/    _/_/_/   
            _/_/      _/    _/  _/  _/      _/  _/    _/    
               _/_/  _/    _/  _/    _/  _/    _/    _/     
          _/_/_/    _/    _/  _/      _/        _/_/_/      
                                                            

			      Cheers to:
			   Honeynet Project
				  &
			    garage4hackers
			    
Report bugs to author
########################################################################

EOF
}


WORK_PATH=$(pwd)
mkdir -p shiva
INSTALL_PATH=$WORK_PATH/shiva

prerequisites () {
    printf "\n\n[*] Checking for the prerequisites in system.\n"
    pkgs=("python" "exim4-daemon-light" "g++" "python-virtualenv" "python-dev" "libmysqlclient-dev")
    
    missing_counter=0
    for needed_pkg in "${pkgs[@]}"
    do
        if ! dpkg-query -W $needed_pkg > /dev/null 2>&1; then
	  printf "\t[-] Missing package: %s\n" "$needed_pkg"
	  missing_counter=$[$missing_counter + 1]	  
	else
	  printf "\t[+] Required package found: (%s)\n" "$needed_pkg"
	fi
    done
       
    if ((missing_counter > 0)); then
      printf "\n[\n\e[1;31m[!] Error!\e[0m Minimum %d package(s) missing. Install required package(s) (refer to User Manual) and re-run this script.....aborting installation\n\n" "$missing_counter"
      exit 1
    fi
}

helpers () {
    printf "\n\n[*] Copying helper files.\n"
    cp -v $WORK_PATH/helpers/dbcreate.py $INSTALL_PATH/
    cp -v $WORK_PATH/helpers/maindb.sql $INSTALL_PATH/
    cp -v $WORK_PATH/helpers/shiva.conf $INSTALL_PATH/
    cp -v $WORK_PATH/helpers/tempdb.sql $INSTALL_PATH/
    cp -v $WORK_PATH/helpers/setup_exim4.sh $INSTALL_PATH/ 
}

dbcreate () {
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
               
        [Nn]*) printf "\n[*] Setting \"localdb : False\" in shiva.conf.\n";;
        
        *) die "Wrong choice!"
    esac
}

receiver () {
    printf "\n\n[*] Setting up SHIVA Receiver!\n"
    
    cd $INSTALL_PATH
    
    printf "\n[*] Creating Virtual Environment: \n"
    virtualenv shivaReceiver
    cd shivaReceiver
    source bin/activate
    
    printf "\n[*] Installing Lamson and creating project: \n"
    easy_install -U distribute
    pip install lamson
    lamson gen -project receiver
    
    printf "\n[*] Copying neccesary files: \n"
    cp -v $WORK_PATH/receiver/core/encoding.py $INSTALL_PATH/shivaReceiver/lib/python2.7/site-packages/lamson/
    cp -v $WORK_PATH/receiver/core/queue.py $INSTALL_PATH/shivaReceiver/lib/python2.7/site-packages/lamson/
    cp -v $WORK_PATH/receiver/core/server.py $INSTALL_PATH/shivaReceiver/lib/python2.7/site-packages/lamson/
    cp -v $WORK_PATH/receiver/core/smtpd.py $INSTALL_PATH/shivaReceiver/lib/python2.7/site-packages/lamson/
    
    cp -v $WORK_PATH/receiver/config/boot.py $INSTALL_PATH/shivaReceiver/receiver/config/
    cp -v $WORK_PATH/receiver/config/settings.py $INSTALL_PATH/shivaReceiver/receiver/config/

    cp -v $WORK_PATH/receiver/handlers/forward.py $INSTALL_PATH/shivaReceiver/receiver/app/handlers
    cp -v $WORK_PATH/receiver/handlers/log.py $INSTALL_PATH/shivaReceiver/receiver/app/handlers/
    cp -v $WORK_PATH/receiver/handlers/queue.py $INSTALL_PATH/shivaReceiver/receiver/app/handlers/
    cp -v $WORK_PATH/receiver/handlers/spampot.py $INSTALL_PATH/shivaReceiver/receiver/app/handlers/
    
    cp -v $WORK_PATH/helpers/clearlogs.sh $INSTALL_PATH/shivaReceiver/receiver/logs/
    
    printf "[+] Setting up Shiva Receiver done!\n"
    deactivate
}

analyzer () {
    printf "\n\n[*] Setting up SHIVA Analyzer!"
    
    cd $INSTALL_PATH
    printf "\n[*] Creating Virtual Environment:\n"
    virtualenv shivaAnalyzer
    cd shivaAnalyzer
    source bin/activate
    
    printf "\n[*] Installing Lamson and creating project:\n"
    pip install lamson
    lamson gen -project analyzer
    
    printf "\n[*] Installing required python modules:\n"
    easy_install -U distribute
    pip install cython
    pip install apscheduler
    pip install MySQL-python
    pip install ssdeep
    
    printf "\n[*] Copying neccesary files:\n"
    cp -v $WORK_PATH/analyzer/core/server.py $INSTALL_PATH/shivaAnalyzer/lib/python2.7/site-packages/lamson/
    cp -v $WORK_PATH/analyzer/core/shiva*.py $INSTALL_PATH/shivaAnalyzer/lib/python2.7/site-packages/lamson/
    
    mkdir -p $INSTALL_PATH/shivaAnalyzer/lib/python2.7/site-packages/lamson/hpfeeds/
    cp -rv $WORK_PATH/hpfeeds/sendfiles.py $INSTALL_PATH/shivaAnalyzer/lib/python2.7/site-packages/lamson/hpfeeds/
    cp -rv $WORK_PATH/hpfeeds/hpfeeds.py $INSTALL_PATH/shivaAnalyzer/lib/python2.7/site-packages/lamson/hpfeeds/
    
    cp -v $WORK_PATH/analyzer/config/boot.py $INSTALL_PATH/shivaAnalyzer/analyzer/config/
    cp -v $WORK_PATH/analyzer/config/settings.py $INSTALL_PATH/shivaAnalyzer/analyzer/config/
    
    cp -v $WORK_PATH/helpers/clearlogs.sh $INSTALL_PATH/shivaAnalyzer/analyzer/logs/
    
    printf "\n[+] Setting up Shiva Analyzer done!\n"
    deactivate
}

create_dirs () {
    printf "\n\n[*] Creating necessary folders and updating configuration files!\n"

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
    printf "\n[+] All done. Refer to User Manual to further customize shiva.conf configuration file\n"

}

die () {
    printf "\n\e[1;31m[!] Error!\e[0m $1\n"
    exit 1
}

installation () {
    prerequisites
    helpers
    dbcreate
    receiver
    analyzer  
    create_dirs
}

banner
read -p "Press enter to continue installation...";
if [ "$UID" == "0" ] || [ "$EUID" == "0" ]
then
    printf "\n[!] Drop your privileges and run as non-root user.....aborting installation\n\n"
    exit 1
fi

installation