# -*- coding: utf-8 -*-

#  Copyright 2019 Giacomo Ferretti
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import json

import requests
from mcdapi import coupon, endpoints

# Edit these variables
__proxy_enabled__ = True
__proxy_url__ = 'socks5://127.0.0.1:9050'
__output_file__ = 'offers_parsed_special.json'


def main():
    session = requests.session()

    if __proxy_enabled__:
        session.proxies = {
            'http': __proxy_url__,
            'https': __proxy_url__
        }

    device_id = coupon.get_random_device_id()
    username = coupon.generate_username(device_id)
    password = coupon.generate_password(device_id)
    vmob = coupon.generate_vmob_uid(device_id)
    plexure = coupon.generate_plexure_api_key(vmob)

    headers = coupon.strip_unnecessary_headers(coupon.get_random_headers(vmob, plexure))

    r = session.request(endpoints.DEVICE_REGISTRATION['method'], endpoints.DEVICE_REGISTRATION['url'],
                        data=endpoints.DEVICE_REGISTRATION['body'].format(username=username, password=password), headers=headers)

    if r.status_code == 200:
        print('Successfully got a token.')
        token = json.loads(r.content)['access_token']
        headers['Authorization'] = 'bearer ' + token
    else:
        print('ERROR 100: Cannot get token')
        exit(100)

    r = session.request(endpoints.AVAILABLE_OFFERS['method'], endpoints.AVAILABLE_OFFERS['url'], headers=headers,
                        params=endpoints.AVAILABLE_OFFERS['params'])

    print(r.status_code)
    offers = json.loads(r.content)

    with open('offers_parsed.json') as f:
        offers_parsed = json.loads(f.read())



    offers_f = []
    for x in offers:
        obj = {
            'id': x['id'],
            'title': x['title'].strip(),
            'description': x['description'].strip(),
            'image': x['image'],
            'startDate': x['startDate'],
            'endDate': x['endDate'],
            'dailyStartTime': x['dailyStartTime'],
            'dailyEndTime': x['dailyEndTime'],
            'daysOfWeek': x['daysOfWeek']
        }

        offers_f.append(obj)

    print(json.dumps(offers_f, indent=2))


if __name__ == '__main__':
    main()
