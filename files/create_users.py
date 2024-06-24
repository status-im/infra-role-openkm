#!/usr/bin/env python3
import sys
import json
import argparse
import logging
import requests
from os import environ as env
from urllib.parse import urlencode

HELP_DESCRIPTION = 'Utility for creating users via OpenKM REST API.'
HELP_EXAMPLE = 'Example: cat users.json  | ./create_users.py'

# Setup logging.
log_format = '[%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
LOG = logging.getLogger(__name__)

class OpenKM:

    def __init__(
        self,
        username,
        password,
        host='localhost',
        port=8080,
        prefix='openkm/rest'
    ):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.prefix = prefix
        self.url = 'http://%s:%d/%s' % (
            self.host, self.port, self.prefix
        )

    def _request(self, method, path, payload=None, params=None):
        if not hasattr(self, 'token') and path != 'auth/login':
            self.token = self._login()
        headers = {
            'Content-Type': 'application/json' if payload else 'application/x-www-form-urlencoded',
            'Authorization': getattr(self, 'token', None),
        }
        url = '%s/%s' % (self.url, path)
        LOG.debug('request: %s %s', method, url)
        LOG.debug('payload: %s', payload)
        LOG.debug('params: %s', params)
        LOG.debug('headers: %s', params)
        resp = requests.request(
            method, url,
            data=json.dumps(payload),
            params=None if not params else urlencode(params).encode('utf-8'),
            headers=headers,
        )
        LOG.debug('status: %s', resp.status_code)
        LOG.debug('response: %s', resp.text)
        LOG.debug('headers: %s', resp.headers)
        resp.raise_for_status()
        return resp.json() if resp.text else None

    def _login(self):
        resp = self._request('POST', 'auth/login', payload={
            'username': self.username,
            'password': self.password
        })
        return resp['Authorization']

    def roles(self):
        return self._request('GET', 'auth/roles')

    def create_user(self, userid, name, email, password):
        return self._request('POST', 'auth/users', payload={
            'id':       userid,
            'name':     name,
            'password': password,
            'email':    email,
            'active':   True,
        })

    def update_user(self, userid, name, email, password):
        return self._request('PUT', 'auth/users/%s' % userid, params={
            'name':     name,
            'email':    email,
            #'password': password,
        })

    def get_user_roles(self, userid):
        return self._request('GET', 'auth/users/%s/roles' % userid)

    def set_user_role(self, userid, roleid='ROLE_USER'):
        return self._request('POST', 'auth/users/%s/roles' % userid, params={
            'roleId': roleid,
        })

    def delete_user(self, userid):
        return self._request('DELETE', 'auth/users/%s' % userid)

    def get_user(self, userid):
        return self._request('GET', 'auth/users/%s' % userid)

    def create_or_update_user(self, userid, name, email, password, roleid):
        #self.create_user(userid, name, email, password) 
        self.update_user(userid, name, email, password) 
        #if self.get_user(userid):
        #else:
        #    self.create_user(userid, name, email, password) 
        #self.set_user_role(userid, roleid=roleid)


def parse_args():
    parser = argparse.ArgumentParser(
        description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE
    )
    parser.add_argument('-H', '--openkm-host', default='localhost',
                      help='OpenKM REST API host.')
    parser.add_argument('-p', '--openkm-port', default=8080,
                      help='OpenKM REST API port.')
    parser.add_argument('-U', '--openkm-username', default=env.get('OPENKM_USERNAME'),
                      help='OpenKM REST API username.')
    parser.add_argument('-P', '--openkm-password', default=env.get('OPENKM_PASSWORD'),
                      help='OpenKM REST API password.')
    parser.add_argument('-d', '--dry-run', action='store_true',
                      help='Do not add any members, just print.')
    parser.add_argument('-l', '--log-level', default='INFO',
                      help='Logging level.')

    args = parser.parse_args()

    assert args.openkm_username ,parser.error('No OpenKM username set!')
    assert args.openkm_password ,parser.error('No OpenKM password set!')

    return args


def main():
    args = parse_args()

    LOG.setLevel(args.log_level.upper())

    okm = OpenKM(
        args.openkm_username,
        args.openkm_password,
        args.openkm_host,
        args.openkm_port
    )
    LOG.info('Connected to OpenKM: http://%s:%d',
             args.openkm_host, args.openkm_port)

    okm.roles()
    LOG.info('Successful login. Token acquired.')

    LOG.info('Creating or updating user: %s', 'testuser')
    okm.create_or_update_user('testuser', 'TestUser', 'test@logos.co', '123qwe', 'USER_ROLE')


if __name__ == '__main__':
    main()

