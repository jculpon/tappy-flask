# -*- coding: utf-8 -*-
"""
    Tappy Terror Simulator
    ----------------------

    Command-line tool for simulating location updates from the OpenAMD API.

    :license: MIT; details in LICENSE
"""
from __future__ import unicode_literals

import argparse
import requests
import json

generic_update_json='''[
{ 'user': 'user1', 'x': 1, 'y': 1, 'z': 1, 'area': 'NOC' },
{ 'user': 'user2', 'x': 2, 'y': 2, 'z': 2, 'area': 'Radio Statler' },
{ 'user': 'user3', 'x': 3, 'y': 3, 'z': 3, 'area': 'Keynote Bullpen'}
]'''

content_type_json_headers={'content-type': 'application/json'}

def post_update(server='http://127.0.0.1:5000', data=generic_update_json):
    url = server + '/amd/push'
    requests.post(
        url,
        data=json.dumps(data),
        headers=content_type_json_headers
    )

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='Send simulated updates to Tappy Terror'
    )
    args = arg_parser.parse_args()

    post_update()
