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

import mcdapi
import requests

from mcdapi import coupon, endpoints

from os import path

# Edit these variables
__proxy_enabled__ = False
__proxy_url__ = 'socks5://127.0.0.1:9050'
__json__ = 'offers.json'
__merchant_id__ = 587
# These IDs will be used in case the offers
# file was not found
__start_id__ = 14760
__end_id__ = 16010


def scraper(start, end):
    print('Starting scraping {num} offers using mcdapi ({version})...'.format(num=(__end_id__ - __start_id__),
                                                                              version=mcdapi.__version__))

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

    headers = coupon.strip_unnecessary_headers(
        coupon.get_random_headers(vmob, plexure))

    r = session.request(endpoints.DEVICE_REGISTRATION['method'], endpoints.DEVICE_REGISTRATION['url'],
                        data=endpoints.DEVICE_REGISTRATION['body'].format(
                            username=username, password=password),
                        headers=headers)

    if r.status_code == 200:
        print('Successfully got a token.')
        token = json.loads(r.content.decode('utf-8'))['access_token']
        headers['Authorization'] = 'bearer ' + token
    else:
        print('ERROR 100')
        exit(100)

    offers = []
    for x in range(start, end + 1):
        print('Requesting offer {}... '.format(x), end='')

        plexure = coupon.generate_plexure_api_key(vmob)
        headers['x-plexure-api-key'] = plexure
        session.headers.update(headers)

        r = session.request(endpoints.REDEEM_OFFER['method'], endpoints.REDEEM_OFFER['url'],
                            data=endpoints.REDEEM_OFFER['body'].format(id=x))

        print('Got a response with code {}'.format(r.status_code))
        offer = {
            'id': x,
            'code': r.status_code,
            'response': json.loads(r.content.decode('utf-8'))
        }
        offers.append(offer)

    return offers


def parser(input_json, merchant_id):
    offers = {}

    for x in input_json:
        if x['code'] == 200:
            if x['response']['merchantId'] == merchant_id:
                obj = {
                    'customTitle': '',
                    'title': x['response']['title'],
                    'description': x['response']['description'],
                    'startDate': x['response']['startDate'],
                    'endDate': x['response']['endDate'],
                    'promoImagePath': x['response']['promoImagePath'],
                    'redemptionId': x['response']['redemptionId'],
                    'special': False
                }

                offers[x['id']] = obj

    return json.dumps(offers, indent=2)


def main():
    if path.exists(__json__):
        print('Using the json file!')
        with open(__json__) as f:
            js = json.loads(f.read())
            f.close()
        start_id = js[0]['id']
        end_id = js[-1]['id'] + 200
        print(start_id)
        print(end_id)
        scraped = scraper(start_id, end_id)
    else:
        print('Json file not found! Using the configured values.')
        scraped = scraper(__start_id__, __end_id__)

    parsed = parser(scraped, __merchant_id__)

    with open(__json__) as f:
        f.write(parsed)


if __name__ == '__main__':
    main()
