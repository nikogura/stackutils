# stackutils

Utilities for working with OpenStack.

## stackinit

Stackinit is a bash script that will install OpenStack Liberty on a RedHat based box.

OpenStack has a bunch of services that all have their own passwords, and the various
  passwords have to be in the right configs in the right way for everything to work.  This can be a pain.  To help, stackinit will generate them for you, and write them into itself.  You can also just write your own passwords into the script if that's your preference.
  
Stackinit works very well on CentOS 7.  There's no reason why it can't work on RHEL or OEL if the repos contain the proper packages.

## boxinit.py
Boxinit.py is a python script that will set up a remote host.  It has the yum repos OpenStack requires in it, and they're munged up to work within Apple Datacenters.

## Usage

    ./boxinit.py -s -n <hostname>
   
You'll be logged into the box

    sudo ./boxinit
    
The box will be updated, will reboot.

Log back into the box

    sudo su -
    ./stackinit
    ./stackinit
    
Openrc files with admin and user creds will be created in /root that can be used for subsequent logins.
    
    

