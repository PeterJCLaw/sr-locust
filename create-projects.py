#!./bin/python

import json
import requests

from locustfile import username, password

host = "https://f17-vm.local"
baseurl = host + "/ide/control.php/"

def ide_post(s, endpoint, params):
    params_json = json.dumps(params)
    r = s.post(baseurl + endpoint, data=params_json, verify=False)
    returned = r.json()
    if 'error' in returned:
        raise Exception(returned['error'])
    return returned

session = requests.Session()

ide_post(session, 'auth/authenticate', {'username': username, 'password':password})

for i in xrange(100):
    proj_name = "test-{}".format(i)
    args = {
        'team': 'ABC',
        'project': proj_name,
    }
    ide_post(session, 'proj/new', args)
    print "Created project '{}'.".format(proj_name)
