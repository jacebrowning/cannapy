"""Module for an interface to the WSLCB Socrata-based open data portal."""

import os
import time
from sodapy import Socrata
import pandas as pd

# WSLCB Socrata Open Data Portal URL
WSLCB_PORTAL_URL = 'data.lcb.wa.gov'

# WSLCB Socrata Open Data Portal Dataset Columns (order by cannapy)
WSLCB_PORTAL_DATASET_COLUMNS = {
    '3qmf-vgdg': ['date', 'license_number', 'county_name', 'city_name',
                  'action'],
    '8rrd-wvpk': ['sales_date', 'sales_year_month', 'pounds_harvested',
                  'grams_harvested'],
    'bhbp-x4eb': ['license', 'type', 'createdate', 'active', 'organization',
                  'address', 'address_line_2', 'city', 'state', 'zip',
                  'county', 'dayphone', 'ubi'],
    'dgm4-3cm6': ['visit_date', 'license_number', 'county_name', 'city_name',
                  'case', 'violation_code', 'wac_code', 'penalty_type'],
    'kdyh-jjfc': ['sales_date', 'sales_year_month', 'type',
                  'child_usableweight_grams', 'child_usableweight_pounds'],
    'msk5-ts9q': ['sessiontimedate', 'orgname', 'inventory_type',
                  'usableweight_grams', 'usableweight_pounds', 'price'],
    'w7wg-8m52': ['date', 'license_number', 'city_name', 'county_name',
                  'activity'],
    'vbqh-2tf4': ['sales_date', 'sales_year_month', 'organization', 'type',
                  'childweight_pounds', 'childweight_grams']
}


class WSLCBPortal(object):
    """An interface to the WSLCB Socrata-based open data portal."""

    def __init__(self, app_token=''):
        """Constructor."""
        # Set the user's Socrata app token:
        # https://dev.socrata.com/docs/app-tokens.html
        if app_token == '':
            # See if an environment variable is set
            app_token = os.getenv('WSLCB_APP_TOKEN', '')
        self._app_token = app_token

        # The Socrata client property will be initialized on first get
        self._client = None

    def get_dataset_metadata(self, dataset_id):
        """Return the requested dataset's metadata."""
        metadata = self.client.get_metadata(dataset_id)
        return metadata

    def get_dataset_count(self, dataset_id):
        """Return the requested dataset's total number of rows."""
        metadata = self.client.get(dataset_id, select='count(*)')
        return int(metadata[0]['count'])

    def get_dataset(self, dataset_id):
        """Return the requested dataset (limited to 100K rows)."""
        return self.client.get(dataset_id, limit=100000)

    def get_entire_dataset(self, dataset_id, order_by):
        """Return the requested dataset (w/ automated paging)."""
        count = self.get_dataset_count(dataset_id)
        limit = 100000
        dataset = []
        for offset in range(0, count, limit):
            dataset.extend(self.client.get(dataset_id, order=order_by,
                                           offset=offset, limit=limit))
        return dataset

    def get_dataframe(self, dataset_id):
        """Return the requested dataset loaded in a Pandas DataFrame."""
        dataset = self.get_dataset(dataset_id)
        columns = WSLCB_PORTAL_DATASET_COLUMNS[dataset_id]
        dataframe = pd.DataFrame.from_records(dataset, columns=columns)
        return dataframe

    def dataset_last_updated(self, dataset_id):
        """Return the requested dataset's last update timestamp."""
        # Retrieve the source dataset's metadata
        metadata = self.get_dataset_metadata(dataset_id)

        # Retrieve dataset last update timestamp in epoch/Unix time
        last_updated = metadata['rowsUpdatedAt']

        # Convert to a localized Python time.struct_time
        # https://docs.python.org/3/library/time.html#time.struct_time
        last_updated = time.localtime(last_updated)

        return last_updated

    @property
    def app_token(self):
        """The user's Socrata open data portal app token."""
        return self._app_token

    @app_token.setter
    def app_token(self, value):
        self._app_token = value

    @property
    def client(self):
        """A sodapy client interface to the WSLCB Socrata open data portal."""
        if self._client is None:
            self._client = Socrata(WSLCB_PORTAL_URL, self.app_token)

        return self._client
