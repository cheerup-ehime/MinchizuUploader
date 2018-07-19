import pandas as pd

import numpy as np
import os

import location_importer
import location_importer as li
import minchizu_browser

json = os.environ.get('GOOGLE_ACCESS_KEY_JSON')
doc_id = os.environ.get('GOOGLE_DOC_ID')
key = os.environ.get('GOOGLE_GEOCODING_KEY')

def test_load_locations():
    locations = ['清流の里ひじかわ', #return latlng, location is true
                 '宇津集会所', #return latlng, but location is not false
                 '村島集会所'  # not return latlng
                ]
    area = '大洲市'


    df_locations = li.load_locations(doc_id, 'test', key)

    ## 正しく取得できる
    assert df_locations.loc[0]['lat'] == 33.460975
    assert df_locations.loc[0]['lng'] == 132.67699
    assert df_locations.loc[0]['address'] == '日本、〒797-1503 愛媛県大洲市肱川町宇和川３０３０'

    ## 取得できるが誤っている（別の場所）
    assert pd.isnull(df_locations.loc[1]['lat'])
    assert pd.isnull(df_locations.loc[1]['lng'])
    assert pd.isnull(df_locations.loc[1]['address'])

    ## 取得できない
    assert pd.isnull(df_locations.loc[2]['lat'])
    assert pd.isnull(df_locations.loc[2]['lng'])
    assert pd.isnull(df_locations.loc[2]['address'])



def test_get_locations_as_df():
    doc_id = os.environ.get('GOOGLE_DOC_ID')
    df = li.get_locations_as_df(doc_id)
    assert df is not None
    assert df.location[0] == '清流の里ひじかわ'
    assert df.start_date[0] == '2018/07/18'
    assert df.end_date[0] == '2018/07/19'
    assert df.status[0] == ''



def test_set_location_by_geocoding():
    df = li.get_locations_as_df(doc_id)
    df_updated = li.set_location_by_geocoding(df, key)
    assert df_updated is not None

    assert df_updated.location[0] == '清流の里ひじかわ'
    assert df_updated.lat[0] == 33.460975
    assert df_updated.lng[0] == 132.67699
    assert df_updated.address[0] == '日本、〒797-1503 愛媛県大洲市肱川町宇和川３０３０'

def test_update_locations_on_google():
    fetcher = location_importer.LocationFetcher()
    df = fetcher.fetch_locations(doc_id, '愛媛')
    df2 = li.set_location_by_geocoding(df, key)

    df2.status = 'DONE'
    df2.updated = minchizu_browser.get_now_string()

    li.update_locations_on_google(df2, doc_id, 'test')
