#!/usr/bin/env bash

ADMIN_LOGIN='admin'
ADMIN_FIRST_NAME='admin'
ADMIN_LAST_NAME='user'
ADMIN_EMAIL='nik.ogura@gmail.com'
BASE_ORG_NAME='fargle'
BASE_ORG_LONG_NAME='infrastructure engineering'
CHEF_SERVER_PACKAGE='chef-server-core-12.10.0-1.el7.x86_64.rpm'
CHEF_SERVER_PACKAGE_URL='https://packages.chef.io/stable/el/7/chef-server-core-12.10.0-1.el7.x86_64.rpm'
OS_PACKAGE_MANAGER='rpm'

LDAP_USER='username'
LDAP_PASSWORD='password'
LDAP_HOST='ldap.server'
LDAP_PORT='636'
LDAP_BASE_DN='dc=company,dc=com'
LDAP_BIND_DN='uid=<user>,cn=users,dc=company,dc=com'
LDAP_LOGIN_ATTRIBUTE='uid'
LDAP_DESC='Open Directory'


# ------------------ Password Management ------------------------

declare -a PASSKEYS=(
ADMIN_PASSWORD
)

# PASSWORDS

for key in ${PASSKEYS[@]}; do
    if [ -z ${!key} ]; then
        echo "No passwords found.  Generating them now and exiting.  Run this script again to actually install OpenStack."

        declare -A SECRETS

        for i in ${PASSKEYS[@]}; do
            SECRETS[$i]=$(openssl rand -hex 10)
        done

        for i in "${!SECRETS[@]}"; do
          #echo "$i => ${SECRETS[$i]}"
          sed -i  "/^# PASSWORDS/a $i=${SECRETS[$i]}
            " $0
        done

        exit 0
    fi
done

# -------------------- Chef Server -------------------------------

echo "Have Passwords.  Installing Chef Server"

if [[ $OS_PACKAGE_MANAGER == 'rpm' ]]; then
    wget $CHEF_SERVER_PACKAGE_URL
    sudo rpm -Uvh $CHEF_SERVER_PACKAGE

elif [[ $OS_PACKAGE_MANAGER == 'dpkg' ]]; then
    wget $CHEF_SERVER_PACKAGE_URL
    sudo dpkg -i $CHEF_SERVER_PACKAGE
else
    echo "Unsupported Package Manager"
    exit 1
fi

echo "Server Installed"

echo "Reconfiguring Chef Server"

chef-server-ctl reconfigure

sudo chef-server-ctl reconfigure

sudo chef-server-ctl user-create $ADMIN_LOGIN $ADMIN_FIRST_NAME $ADMIN_LAST_NAME $ADMIN_EMAIL $ADMIN_PASSWORD --filename $ADMIN_LOGIN.pem

chef-server-ctl org-create $BASE_ORG_NAME $BASE_ORG_LONG_NAME --association_user $ADMIN_LOGIN --filename $BASE_ORG_NAME.pem

echo "Installation Complete"

# ------------  Chef Manage --------------------------------------

echo "Installing Chef Manage"

sudo chef-server-ctl install chef-manage

sudo chef-server-ctl reconfigure

sudo chef-manage-ctl reconfigure --accept-license

# ------------ Push Jobs -----------------------------------------
#sudo chef-server-ctl install opscode-push-jobs-server

#sudo chef-server-ctl reconfigure

#sudo opscode-push-jobs-server-ctl reconfigure

# ------------ Reporting -----------------------------------------

sudo chef-server-ctl install opscode-reporting

sudo chef-server-ctl reconfigure

sudo opscode-reporting-ctl reconfigure

# LDAP Integration
#CONFIG=$(echo <<'EOF'
#ldap['base_dn']           = '$LDAP_BASE_DN'
#ldap['bind_dn']           = '$LDAP_BIND_DN'
#ldap['bind_password']     = '$LDAP_PASSWORD'
#ldap['host']              = '$LDAP_HOST'
#ldap['port']              = $LDAP_PORT
#ldap['system_adjective']  = '$LDAP_DESC'
#ldap['ssl_enabled']       = true
#ldap['login_attribute']   = '$LDAP_LOGIN_ATTRIBUTE'
#EOF
#)
#
#echo "$CONFIG" | sudo tee -a /etc/opscode/chef-server.rb
#
#sudo chef-server-ctl reconfigure
#sudo chef-manage-ctl reconfigure
