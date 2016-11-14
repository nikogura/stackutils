#!/usr/bin/env python

import sys
import subprocess
import re
import os
import getopt

'''
    Installs Yum Repos, ssh keys, a .bashrc and your .vimrc to a remote box.

    Detects Distribution (CentOS or OEL) and Version, and installs the appropriate repos

'''

class BoxInit:
    def __init__(self, mysql=None, epel=True, create_eth1=False, docker=False, openstack=False, stackinit=False, snapshot=None, keys_path=None, alt_host_names=[], sandbox=False, chefinit=False):
        #self.snapshot = snapshot or '2016.11.6'
        self.keys_path = keys_path or '~/.ssh/automationKeys/id*'
        self.openstack = openstack
        self.stackinit = stackinit
        self.mysql = mysql
        self.epel = epel
        self.create_eth1 = create_eth1
        self.docker = docker
        self.alt_host_names = alt_host_names
        self.sandbox = sandbox
        self.chefinit = chefinit

    def epel_repo(self, os_ver):
        return '''[epel]
name=Extra Packages for Enterprise Linux \$releasever - \$basearch
baseurl=http://download.fedoraproject.org/pub/epel/{}/\$basearch
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7
enabled=1'''.format(os_ver)

    def epel_key(self):
        return '''-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.11 (GNU/Linux)

mQINBFKuaIQBEAC1UphXwMqCAarPUH/ZsOFslabeTVO2pDk5YnO96f+rgZB7xArB
OSeQk7B90iqSJ85/c72OAn4OXYvT63gfCeXpJs5M7emXkPsNQWWSju99lW+AqSNm
jYWhmRlLRGl0OO7gIwj776dIXvcMNFlzSPj00N2xAqjMbjlnV2n2abAE5gq6VpqP
vFXVyfrVa/ualogDVmf6h2t4Rdpifq8qTHsHFU3xpCz+T6/dGWKGQ42ZQfTaLnDM
jToAsmY0AyevkIbX6iZVtzGvanYpPcWW4X0RDPcpqfFNZk643xI4lsZ+Y2Er9Yu5
S/8x0ly+tmmIokaE0wwbdUu740YTZjCesroYWiRg5zuQ2xfKxJoV5E+Eh+tYwGDJ
n6HfWhRgnudRRwvuJ45ztYVtKulKw8QQpd2STWrcQQDJaRWmnMooX/PATTjCBExB
9dkz38Druvk7IkHMtsIqlkAOQMdsX1d3Tov6BE2XDjIG0zFxLduJGbVwc/6rIc95
T055j36Ez0HrjxdpTGOOHxRqMK5m9flFbaxxtDnS7w77WqzW7HjFrD0VeTx2vnjj
GqchHEQpfDpFOzb8LTFhgYidyRNUflQY35WLOzLNV+pV3eQ3Jg11UFwelSNLqfQf
uFRGc+zcwkNjHh5yPvm9odR1BIfqJ6sKGPGbtPNXo7ERMRypWyRz0zi0twARAQAB
tChGZWRvcmEgRVBFTCAoNykgPGVwZWxAZmVkb3JhcHJvamVjdC5vcmc+iQI4BBMB
AgAiBQJSrmiEAhsPBgsJCAcDAgYVCAIJCgsEFgIDAQIeAQIXgAAKCRBqL66iNSxk
5cfGD/4spqpsTjtDM7qpytKLHKruZtvuWiqt5RfvT9ww9GUUFMZ4ZZGX4nUXg49q
ixDLayWR8ddG/s5kyOi3C0uX/6inzaYyRg+Bh70brqKUK14F1BrrPi29eaKfG+Gu
MFtXdBG2a7OtPmw3yuKmq9Epv6B0mP6E5KSdvSRSqJWtGcA6wRS/wDzXJENHp5re
9Ism3CYydpy0GLRA5wo4fPB5uLdUhLEUDvh2KK//fMjja3o0L+SNz8N0aDZyn5Ax
CU9RB3EHcTecFgoy5umRj99BZrebR1NO+4gBrivIfdvD4fJNfNBHXwhSH9ACGCNv
HnXVjHQF9iHWApKkRIeh8Fr2n5dtfJEF7SEX8GbX7FbsWo29kXMrVgNqHNyDnfAB
VoPubgQdtJZJkVZAkaHrMu8AytwT62Q4eNqmJI1aWbZQNI5jWYqc6RKuCK6/F99q
thFT9gJO17+yRuL6Uv2/vgzVR1RGdwVLKwlUjGPAjYflpCQwWMAASxiv9uPyYPHc
ErSrbRG0wjIfAR3vus1OSOx3xZHZpXFfmQTsDP7zVROLzV98R3JwFAxJ4/xqeON4
vCPFU6OsT3lWQ8w7il5ohY95wmujfr6lk89kEzJdOTzcn7DBbUru33CQMGKZ3Evt
RjsC7FDbL017qxS+ZVA/HGkyfiu4cpgV8VUnbql5eAZ+1Ll6Dw==
=hdPa
-----END PGP PUBLIC KEY BLOCK-----'''

    def openstack_liberty(self, os_ver):
        return '''[openstack-liberty]
name=OpenStack Liberty Repository
baseurl=http://mirror.centos.org/centos/{}/cloud/\$basearch/openstack-liberty/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-SIG-Cloud'''.format(os_ver)

    def openstack_liberty_key(self):
        return '''-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v2.0.22 (GNU/Linux)

mQENBFVWcCcBCACfm3eQ0526/I0/p7HpR0NjK7K307XHhnbcbZv1sDUjQABDaqh0
N4gnZcovf+3fj6pcdOmeOpGI0cKE7Fh68RbEIqyjB7l7+j1grjewR0oCFFZ38KGm
j+DWQrj1IJW7JU5fH/G0Cu66ix+dJPcuTB3PJTqXN3ce+4TuG09D+epgwfbHlqaT
pH2qHCu2uiGj/AaRSM/ZZzcInMaeleHSB+NChvaQ0W/m+kK5d/20d7sfkaTfI/pY
SrodCfVTYxfKAd0TLW03kimHs5/Rdz+iZWecVKv6aFxzaywbrOjmOsy2q0kEWIwX
MTZrq6cBRRuWyiXsI2zT2YHQ4UK44IxINiaJABEBAAG0WkNlbnRPUyBDbG91ZCBT
SUcgKGh0dHA6Ly93aWtpLmNlbnRvcy5vcmcvU3BlY2lhbEludGVyZXN0R3JvdXAv
Q2xvdWQpIDxzZWN1cml0eUBjZW50b3Mub3JnPokBOQQTAQIAIwUCVVZwJwIbAwcL
CQgHAwIBBhUIAgkKCwQWAgMBAh4BAheAAAoJEPm5/ud2RCnmATUH/3HDtWxpFkmy
FiA3VGkMt5dp3bgCRSd84X6Orfx1LARowpI4LomCGglGBGXVJePBacwcclorbLaz
uWrW/wU0efz0aDB5c4NPg/yXfNvujvlda8ADJwZXVBQphzvaIKwl4PqBsEnxC10I
93T/0iyphAhfMRJ5R8AbEHMj7uF+TWTX/JoyQagllMqWTwoP4DFRutPdOmmjwvSV
kWItH7hq6z9+M4dhlqeoOvPbL5oCxX7TVmLck02Q5gI4syULOa7sqntzUQKFkhWp
9U0+5KrBQBKezrurrrkq/WZR3WNE1KQfNQ77f7S2JcXJdOaKgJ7xe7Y2flPq98Aq
wKXK7l1c3dc=
=W6yF
-----END PGP PUBLIC KEY BLOCK-----'''

    def docker_repo(self, os_ver):
        return '''[dockerrepo]
name=Docker Repository
baseurl=https://yum.dockerproject.org/repo/main/oraclelinux/{}
enabled=1
gpgcheck=1
gpgkey=https://yum.dockerproject.org/gpg'''.format(os_ver).format(os_ver)


    def centos_base(self, os_ver):
        return '''[base]
name=CentOS-7 - Base
baseurl=http://mirror.centos.org/centos/{os_ver}/os/\$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7

#released updates
[updates]
name=CentOS-7 - Updates
baseurl=http://mirror.centos.org/centos/{os_ver}/updates/\$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7

#additional packages that may be useful
[extras]
name=CentOS-7 - Extras
baseurl=http://mirror.centos.org/centos/{os_ver}/extras/\$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7

#additional packages that extend functionality of existing packages
[centosplus]
name=CentOS-7 - Plus
baseurl=http://mirror.centos.org/centos/{os_ver}/centosplus/\$basearch/
gpgcheck=1
enabled=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7'''.format(os_ver=os_ver)


    def mysql_community(self, os_ver):
        return '''[mysql57-community]
name=MySQL 5.7 Community Server
baseurl=http://repo.mysql.com/yum/mysql-5.7-community/el/{}/\$basearch/
enabled=1
failovermethod=priority
gpgcheck=1
gpgkey=https://raw.githubusercontent.com/chef-cookbooks/yum-mysql-community/master/files/default/mysql_pubkey.asc'''.format(os_ver)


    def bashrc(self):
        return '''export EDITOR=/usr/bin/vim

export PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;36m\]\w\[\033[00m\]\$ '

alias vi='vim'
alias vimr='vim -R -'
alias tailf='tail -n50 -f'
alias ls='ls --color'

LS_COLORS='rs=0:di=01;36:ln=01;35:mh=00:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:su=37;41:sg=30;43:ca=30;41:tw=30;42:ow=34;42:st=37;44:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arj=01;31:*.taz=01;31:*.lzh=01;31:*.lzma=01;31:*.tlz=01;31:*.txz=01;31:*.zip=01;31:*.z=01;31:*.Z=01;31:*.dz=01;31:*.gz=01;31:*.lz=01;31:*.xz=01;31:*.bz2=01;31:*.bz=01;31:*.tbz=01;31:*.tbz2=01;31:*.tz=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.war=01;31:*.ear=01;31:*.sar=01;31:*.rar=01;31:*.ace=01;31:*.zoo=01;31:*.cpio=01;31:*.7z=01;31:*.rz=01;31:*.jpg=01;35:*.jpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.svg=01;35:*.svgz=01;35:*.mng=01;35:*.pcx=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.m2v=01;35:*.mkv=01;35:*.webm=01;35:*.ogm=01;35:*.mp4=01;35:*.m4v=01;35:*.mp4v=01;35:*.vob=01;35:*.qt=01;35:*.nuv=01;35:*.wmv=01;35:*.asf=01;35:*.rm=01;35:*.rmvb=01;35:*.flc=01;35:*.avi=01;35:*.fli=01;35:*.flv=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.yuv=01;35:*.cgm=01;35:*.emf=01;35:*.axv=01;35:*.anx=01;35:*.ogv=01;35:*.ogx=01;35:*.aac=00;36:*.au=00;36:*.flac=00;36:*.mid=00;36:*.midi=00;36:*.mka=00;36:*.mp3=00;36:*.mpc=00;36:*.ogg=00;36:*.ra=00;36:*.wav=00;36:*.axa=00;36:*.oga=00;36:*.spx=00;36:*.xspf=00;36:';
export LS_COLORS

export PATH=\$HOME/bin:\$PATH'''

    def boxinit(self):
        return '''set -e
rm -f /etc/yum.repos.d/*
mv *repo /etc/yum.repos.d
find . -maxdepth 1 -name 'RPM-GPG*' -type f  -exec mv {} /etc/pki/rpm-gpg \;
find . -maxdepth 1 -name 'RPM_GPG*' -type f  -exec mv {} /etc/pki/rpm-gpg \;
yum clean all
yum install -y vim git ipcalc unzip wget curl
cp .vimrc /root
cp .bashrc /root
if [ -e "ifcfg-eth1" ]; then
    mv ifcfg-eth1 /etc/sysconfig/network-scripts
fi
source ~/.bashrc
if [ -e "stackinit" ]; then
    mv stackinit /root
fi
rm boxinit
yum update -y
reboot
'''

    def eth1(self):
        return '''DEVICE="eth1"
BOOTPROTO="none"
ONBOOT="yes"
TYPE="Ethernet"'''

    def send_file(self, file_name, file_contents, host):
        subprocess.call('echo "{}" | ssh {} "cat > {}"'.format(file_contents, host, file_name), shell=True)

    def append_file(self, file_name, file_contents, host):
        subprocess.call('echo "{}" | ssh {} "cat >> {}"'.format(file_contents, host, file_name), shell=True)

    def run(self, hostname, replace_keys):
        if replace_keys:
            print "clearing out old host key(s)"

            hostnames = self.alt_host_names
            hostnames.append(hostname)

            for name in hostnames:
                subprocess.call("sed -i '' '/{}/d' ~/.ssh/known_hosts".format(name), shell=True)

            print "registering new host key"
            subprocess.call("ssh -oStrictHostKeyChecking=no {} uptime".format(hostname), shell=True)

        distro = None

        kernel = subprocess.check_output('''ssh {} 'uname -a' | cut -d " " -f3'''.format(hostname), shell=True)
        os_info = subprocess.check_output('''ssh {} grep NAME /etc/os-release'''.format(hostname), shell=True)

        if 'CentOS' in os_info:
            distro = 'centos'
        else:
            distro = 'oel'

        if distro is None:
            raise Exception("Couldn't figure out distro for " + hostname)

        regex = r"el(\d+)(?:uek)?\.x86_64"
        matches = re.findall(regex, kernel)

        os_ver = matches[0]

        if os_ver:
            print "distro: " + distro + " version: " + os_ver

            print "sending ssh keys from " + self.keys_path
            subprocess.call('scp {} {}:.ssh'.format(self.keys_path, hostname), shell=True)

            print "sending your .vimrc"
            subprocess.call('scp ~/.vimrc {}:'.format(hostname), shell=True)

            print "sending bashrc"
            self.send_file('.bashrc', self.bashrc(), hostname)

            print "sending repos"
            if distro == 'centos':
                if self.openstack:
                    self.send_file('openstack-liberty.repo', self.openstack_liberty(os_ver), hostname)
                    self.send_file('RPM-GPG-KEY-CentOS-SIG-Cloud', self.openstack_liberty_key(), hostname)

                self.send_file('CentOS-Base.repo', self.centos_base(os_ver), hostname)
                self.send_file('iossys.repo', self.iossys(os_ver), hostname)
                self.send_file('epel.repo', self.epel_repo(os_ver), hostname)

                if self.mysql:
                    self.send_file('mysql-community.repo', self.mysql_community(os_ver), hostname)

                if self.docker:
                    self.send_file('docker.repo', self.docker_repo(os_ver), hostname)

            else:
                self.send_file('epel.repo', self.epel_repo(os_ver), hostname)
                self.send_file('RPM-GPG-KEY-EPEL-7', self.epel_key(), hostname)

                if self.openstack:
                    self.send_file('openstack-liberty.repo', self.openstack_liberty(os_ver), hostname)
                    self.send_file('RPM-GPG-KEY-CentOS-SIG-Cloud', self.openstack_liberty_key(), hostname)

                if self.mysql:
                    self.send_file('mysql-community.repo', self.mysql_community(os_ver), hostname)

                if self.docker:
                    self.send_file('docker.repo', self.docker_repo(os_ver), hostname)

            print "Sending boxinit"
            self.send_file('boxinit', self.boxinit(), hostname)
            subprocess.call('ssh {} chmod 755 boxinit'.format(hostname), shell=True)

            if self.sandbox:
                with open("%s/.ssh/automationKeys/id_rsa.pub" % os.environ['HOME']) as f:
                    automation_key = f.readlines()[0]

                self.append_file('.ssh/authorized_keys', automation_key, hostname)

            if self.stackinit:
                print "sending stackinit"
                cwd = os.getcwd()
                file_path = cwd + "/bin/stackinit"
                subprocess.call('scp {} {}:'.format(file_path, hostname), shell=True)

            if self.chefinit:
                print "sending chefinit"
                cwd = os.getcwd()
                file_path = cwd + "/bin/chefinit"
                subprocess.call('scp {} {}:'.format(file_path, hostname), shell=True)

            subprocess.call('ssh {}'.format(hostname), shell=True)

        else:
            raise Exception("Cannot derive version of remote OS.  Cannot Continue")


if __name__ == '__main__':
    stackinit = False
    replace_keys = True
    openstack = False
    mysql = False
    docker = False
    snapshot = None
    keys_path = None
    hostname = None
    sandbox = False
    chefinit = False

    print "starting"

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hiromds:k:n:bc", ['help', 'stackinit', 'auto replace host keys', 'openstack', 'mysql', 'docker', 'snapshot=', 'keyspath=', 'name=', 'sandbox','chefinit'])
    except getopt.GetoptError as err:
        print str(err)
        exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print "boxinit.py [sromd]\n" \
                  "-s install stackinit\n" \
                  "-r replace host keys \n" \
                  "-o add openstack repos\n" \
                  "-m add mysql repos\n" \
                  "-d add docker repos\n" \
                  "-s <snapshot>  defaults to 2016.11.6\n"\
                  "-k <keys path>  defaults to ~/.ssh/automationKeys/*\n" \
                  "-n <hostname" \
                  "-c chefinit" \
                  "-b"

            sys.exit()
        elif opt in ("-c", "--chefinit"):
            chefinit = True
        elif opt in ("-i", "--stackinit"):
            stackinit = True
            openstack = True
        elif opt in ("-r", "--replacehostkeys"):
            replace_keys = True
        elif opt in ("-o", "--openstack"):
            openstack = True
        elif opt in ("-m", "--mysql"):
            mysql = True
        elif opt in ("-d", "--docker"):
            docker = True
        elif opt in ("-s", "--snapshot"):
            snapshot = arg
        elif opt in ("-k", "--keyspath"):
            keys_path = arg
        elif opt in ("-n", "--hostname"):
            hostname = arg
        elif opt in ("-b"):
            sandbox = True

    if hostname == None:
        print "Hostname is required."
        sys.exit(2)

    b = BoxInit(stackinit=stackinit, openstack=openstack, mysql=mysql, docker=docker, snapshot=snapshot, keys_path=keys_path, sandbox=sandbox, chefinit=chefinit)

    b.run(hostname, replace_keys)



