#!/usr/bin/env python

from sbox import sbox
from boxinit import BoxInit
import subprocess

sb = sbox()

hostname = sb.get_hostname()

b = BoxInit(stackinit=False, openstack=False, mysql=False, docker=False, snapshot=None, keys_path='~/.ssh/automationKeys/*', alt_host_names=['sandbox.company.com'], sandbox=True)

b.run(hostname, True)

