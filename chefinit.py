#!/usr/bin/env python

from boxinit import BoxInit

hostname = 'chef-dev.company.com'

b = BoxInit(chefinit=True, stackinit=False, openstack=False, mysql=False, docker=False, snapshot=None, keys_path='~/.ssh/automationKeys/*')

b.run(hostname, True)
