#!/usr/bin/env python

from boxinit import BoxInit

hostname = 'controller.company.com'

b = BoxInit(stackinit=True, openstack=True, mysql=False, docker=False, snapshot=None, keys_path='~/.ssh/automationKeys/*', alt_host_names=['controller.company.com'])

b.run(hostname, True)
