import os
from datetime import datetime

import pandas as pd

# Column name of import records
from geo_corder import GeoCorder
from google_client import create_google_client

doc_id = os.environ.get('GOOGLE_DOC_ID')

class LocationFetcher:
    cols_name = [
        'area', 'location', 'type', 'lat', 'lng', 'address',
        'time_slot', 'period_from', 'period_to', 'description',
        'original_info', 'contributor', 'status', 'updated'
    ]

    def __init__(self, json=None):
        self.client = create_google_client(json)

    def fetch_locations(self, doc_id, sheet_name):
        doc = self.client.open_by_key(doc_id)
        wks = doc.worksheet(sheet_name)
        records = wks.get_all_values()
        data = records[1:]
        return pd.DataFrame(data=data, columns=LocationFetcher.cols_name)


def get_locations_as_df(doc_id):
    fetcher = LocationFetcher()
    df = fetcher.fetch_locations(doc_id, '愛媛')
    df.period_from.format


def get_latlng_from_google(areas: object, locations: object) -> object:
    corder = GeoCorder()
    return [corder.geocoding(area, location) for area, location in zip(areas, locations)]


def set_location_by_geocoding(df, key):
    areas = df.area
    locations = df.location

    corder = GeoCorder(key)
    latlng_list = [corder.geocoding(area, location) for area, location in zip(areas, locations)]
    return create_geocorded_df(df, latlng_list)


def create_geocorded_df(df, latlng_list):
    df_latlng = pd.DataFrame(data=latlng_list)
    df.lat = df_latlng.lat
    df.lng = df_latlng.lng
    df['address'] = df_latlng.address
    return df


def update_locations_on_google(df, doc_id, sheet_name):

    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

    client = create_google_client()
    sh = client.open_by_key(doc_id)
    ws = sh.worksheet(sheet_name)

    for i, row in df.iterrows():
        print("No:{} Row:{}".format(i, row))

        if pd.notnull(row.lat) and pd.notnull(row.lng):
            ws.update_cell(i+2, 4, row.lat)
            ws.update_cell(i+2, 5, row.lng)
            ws.update_cell(i+2, 6, row.address)
            ws.update_cell(i+2, 13, row.status)
            ws.update_cell(i+2, 14, row.updated)


def load_locations(gdoc_id=None, sheet_id='test', key=None):
    if gdoc_id is None:
        gdoc_id = doc_id

    fetcher = LocationFetcher()
    df = fetcher.fetch_locations(doc_id, sheet_id)

    corder = GeoCorder(key)
    latlng_list = [corder.geocoding(area, location)
                   for area, location in zip(df.area, df.location)]
    return create_geocorded_df(df, latlng_list)


def update_locations(df, sheet_id='test'):
    update_locations_on_google(df, doc_id, sheet_id)
