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
import os

import requests
from mcdapi import endpoints

__proxy_enabled__ = True
__proxy_url__ = 'socks5://127.0.0.1:9050'
__image_folder__ = 'images'
__offers_file__ = 'offers_parsed.json'


def main():
    if not os.path.isdir(__image_folder__):
        os.mkdir(__image_folder__)

    session = requests.session()

    if __proxy_enabled__:
        session.proxies = {
            'http': __proxy_url__,
            'https': __proxy_url__
        }

    # Load offers
    with open(__offers_file__) as f:
        offers = json.loads(f.read())

    for x in offers:
        params = endpoints.PROMO_IMAGE['params']
        params['path'] = x['promoImagePath']
        params['imageFormat'] = 'png'
        r = session.request(endpoints.PROMO_IMAGE['method'], endpoints.PROMO_IMAGE['url'].format(size=512),
                            params=params)

        if r.status_code == 200:
            with open(os.path.join(__image_folder__, x['promoImagePath']), 'wb') as f:
                f.write(r.content)


if __name__ == '__main__':
    main()