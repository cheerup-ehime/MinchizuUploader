import os
import re
from time import sleep
import requests

def create_loc_dict(lat, lng, addr):
    return {
        'lat': lat,
        'lng': lng,
        'address': addr
    }

class GeoCorder:
    def __init__(self, key=None):
        self.wait_time = 0.3  # (sec)
        self.base_url = 'https://maps.googleapis.com/maps/api/geocode/json?language=ja&address={}&key={}'
        self.headers = {'content-type': 'application/json'}
        if key is None:
            self.key = os.environ.get('GOOGLE_GEOCODING_KEY')
        else:
            self.key = key

    def geocoding(self, area, location):
        url = self.base_url.format(location, self.key)
        r = requests.get(url, headers=self.headers)
        data = r.json()
        loc_dict = {}
        sleep(self.wait_time)

        if 'results' in data and \
            len(data['results']) > 0 and \
            'formatted_address' in data['results'][0]:
            address = data['results'][0]['formatted_address']
            lat = data['results'][0]['geometry']['location']['lat']
            lng = data['results'][0]['geometry']['location']['lng']

            if re.search(area, address) is None:
                return create_loc_dict(None, None, None)

            return create_loc_dict(lat, lng, address)
        else:
            return create_loc_dict(None, None, None)