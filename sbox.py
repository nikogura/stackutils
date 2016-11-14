#!/usr/bin/env python

import os
from keystoneauth1.identity import v3
from keystoneauth1 import session
import novaclient.client
import glanceclient
import subprocess

class sbox:
    def __init__(self):
        self.auth_url ='http://controller.company.com:5000/v3'
        self.username = os.environ['OS_USERNAME']
        self.password = os.environ['OS_PASSWORD']
        self.project_name = os.environ['OS_PROJECT_NAME']

    def get_hostname(self):
        auth = v3.Password(
            auth_url=self.auth_url,
            username=self.username,
            password=self.password,
            project_name=self.project_name,
            user_domain_id='default',
            project_domain_id='default',

        )

        sess = session.Session(auth=auth)
        nova = novaclient.client.Client('2.1', session=sess)
        glance = glanceclient.Client('1', session=sess)

        image_name = glance.images.get(nova.servers.list(search_opts={'name': 'sandbox-nik'})[0].image['id']).to_dict()['name']

        if 'CentOS' in image_name:
            hostname = 'sandbox-centos'

        elif 'Oracle' in image_name:
            hostname = 'sandbox-oel'

        return hostname

if __name__ == '__main__':
    sb = sbox()
    subprocess.call('ssh {}'.format(sb.get_hostname()), shell=True)
