#!/user/bin/env python
import os

import location_importer as li
import minchizu_browser as minchizu
import click

# @click.command()
@click.option('--docid', default=None, help='google spreadsheet id')
@click.option('--sheet', default='test', help='Sheet name for loading location informations')
@click.option('--url', default='https://minchizu-e6818.firebaseapp.com', help='minchizu url')
@click.option('--json',
              default=os.environ.get('GOOGLE_ACCESS_KEY_JSON'),
              help='json of google access key for access to google spread sheet')
@click.option('--geokey',
              default=os.environ.get('GOOGLE_GEOCODING_KEY'),
              help='access key for google geocoding')
def upload(docid, sheet, url, json, geokey):
    click.echo('Upload MinnanoChizu')

    click.echo('Load spread sheet')
    df = li.load_locations(doc_id, sheet, geokey)
    click.echo('Upload locations to Minchizu')
    df_updated = minchizu.register_locations(df, url)
    click.echo('Update spread sheet')
    li.update_locations(df_updated, sheet)
    click.echo('Finished!')


if __name__ == '__main__':
    doc_id = os.environ.get('GOOGLE_DOC_ID')
    json = os.environ.get('GOOGLE_ACCESS_KEY_JSON')
    url = os.environ.get('MINCHIZU_URL')
    key = os.environ.get('GOOGLE_GEOCODING_KEY')
    upload(doc_id, 'test', url , json, key)