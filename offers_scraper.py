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

import json, mcdapi, requests, sys
from datetime import datetime
from mcdapi import coupon, endpoints

# Edit these variables
__proxy_enabled__ = True
__proxy_url__ = 'socks5://127.0.0.1:9050'
__output_file__ = 'offers_scraped.json'
__start_id__ = 10000
__end_id__ = 20000


def main():
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd) #used to print the offer title without a unicode error
    print('Starting scraping {num} offers using mcdapi ({version})...'.format(num=(__end_id__ - __start_id__ + 1),
                                                                              version=mcdapi.__version__))
    start_time = datetime.now()
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
                        data=endpoints.DEVICE_REGISTRATION['body'].format(username=username, password=password),
                        headers=headers)

    if r.status_code == 200:
        print('Successfully got a token.')
        token = json.loads(r.content.decode('utf-8'))['access_token']
        headers['Authorization'] = 'bearer ' + token
    else:
        print('ERROR 100')
        exit(100)

    offers = []
    for x in range(__start_id__, __end_id__ + 1):
        print('Requesting offer {}... '.format(x), end='')

        plexure = coupon.generate_plexure_api_key(vmob)
        headers['x-plexure-api-key'] = plexure
        session.headers.update(headers)

        r = session.request(endpoints.REDEEM_OFFER['method'], endpoints.REDEEM_OFFER['url'],
                            data=endpoints.REDEEM_OFFER['body'].format(id=x))

        print('Got a response with code {}'.format(r.status_code), end='')

        if r.status_code == 200:
            response = json.loads(r.content)
            print(': {} [{} - {}]'.format(response['title'].translate(non_bmp_map), response['startDate'], response['endDate']))
            offer = {
               'id': x,
               'code': r.status_code,
               'response': json.loads(r.content.decode('utf-8'))
            }
            offers.append(offer)
        else:
            print(': {}'.format(json.loads(r.content)['error']))
    with open(__output_file__, 'w') as f:
         f.write(json.dumps(offers))

    end_time = datetime.now()
    print('Elapsed time: ' + str(end_time - start_time))


if __name__ == '__main__':
    main()
