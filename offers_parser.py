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

# Edit these variables
__proxy_enabled__ = True
__proxy_url__ = 'socks5://127.0.0.1:9050'
__input_file__ = 'offers_scraped.json'
__output_file__ = 'offers_parsed.json'
__merchant_id__ = 587


def main():
    offers = {}

    with open(__input_file__) as f:
        js = json.loads(f.read())

        for x in js:
            if x['code'] == 200:
                if x['response']['merchantId'] == __merchant_id__:
                    obj = {
                        'customTitle': '',
                        'title': x['response']['title'],
                        'description': x['response']['description'],
                        'startDate': x['response']['startDate'],
                        'endDate': x['response']['endDate'],
                        'promoImagePath': x['response']['promoImagePath'],
                        'redemptionId': x['response']['redemptionId']
                    }

                    offers[x['id']] = obj

    with open(__output_file__, 'w') as f:
        print('Found {num} offers matching {merchant}.'.format(num=len(offers), merchant=__merchant_id__))
        f.write(json.dumps(offers, indent=2))


if __name__ == '__main__':
    main()
