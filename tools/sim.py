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
import time

generic_update_json='''[
{ "user": "user1", "x": 1, "y": 1, "z": 1, "area": "NOC", "button": true},
{ "user": "user2", "x": 2, "y": 2, "z": 2, "area": "Radio Statler"},
{ "user": "user3", "x": 3, "y": 3, "z": 3, "area": "Keynote Bullpen"}
]'''

content_type_json_headers={'content-type': 'application/json'}

def post_update(server='http://127.0.0.1:5000', json_data=generic_update_json):
    url = server + '/amd/push'
    result = requests.post(
        url,
        data=json_data,
        headers=content_type_json_headers
    )
    return result


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='Send simulated updates to Tappy Terror'
    )
    arg_parser.add_argument(
        '-w',
        '--wait-time',
        help='time, in ms, to wait between requests',
        default=100,
        type=int
    )
    arg_parser.add_argument(
        '-n',
        '--number',
        help='number of requests to send',
        default=5,
        type=int
    )
    arg_parser.add_argument(
        '-j',
        '--json',
        help='json string to send'
    )
    args = arg_parser.parse_args()

    if args.json is not None:
        try:
            parsed = json.loads(args.json)
        except:
            print 'Unable to parse provided json -- is it valid?'
            raise

    for i in xrange(args.number):
        if args.json is None:
            result = post_update()
        else:
            result = post_update(json_data=args.json)
        try:
            result.raise_for_status()
            print 'Status %d: %s' % (result.status_code, result.json())
        except requests.HTTPError, e:
            print 'Request failed! Status %d, underlying error %s' % (result.status_code, e)
        time.sleep(float(args.wait_time)/1000)
