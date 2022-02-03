import json
import datetime
from lib.utils import get_json_file


class DataMapperError(Exception):
    pass


class DataMapper:
    qr_data = None
    schema = None

    json = ''
    new_json = {}

    def _set_expires_at(self, expires_value):

        by_type = [x for x in self.settings if x['type'] == expires_value and x['name'] == "vaccine_end_day_complete"]
        if len(by_type) > 0:
            self.expires_at = datetime.datetime.strftime(
                datetime.datetime.fromtimestamp(self.issued_at) + datetime.timedelta(days=int(by_type[0]['value']))
                , '%Y-%m-%d')

    def _save_json(self, data, schema, level=0):

        for key, value in data.items():
            try:
                description = schema[key].get('title') or schema[key].get('description') or key
                description, _, _ = description.partition(' - ')
                if type(value) is dict:
                    self.json += '<p>' + ('&nbsp;' * level) + '<strong>' + description + '</strong></p>'
                    _, _, sch_ref = schema[key]['$ref'].rpartition('/')
                    self._save_json(value, self.schema['$defs'][sch_ref]['properties'], level + 1)
                elif type(value) is list:
                    self.json += '<p>' + ('&nbsp;' * level) + '<strong>' + description + '</strong></p>'
                    _, _, sch_ref = schema[key]['items']['$ref'].rpartition('/')
                    for v in value:
                        self._save_json(v, self.schema['$defs'][sch_ref]['properties'], level + 1)
                else:
                    if description == "vaccine medicinal product":
                        self._set_expires_at(str(value))
                    self.json += '<p>' + ('&nbsp;' * level) + '<strong>' + description + '</strong>' + ':' + str(
                        value) + '</p>'
            except KeyError:
                print('error keys')
                print(data)

    def __set_schema(self, schema_url):
        self.schema = get_json_file(schema_url,
                                    "https://raw.githubusercontent.com/ehn-dcc-development/ehn-dcc-schema/release/1.3.0/DCC.combined-schema.json")

    def __set_settings(self, settings_url):
        self.settings = get_json_file(settings_url, "https://get.dgc.gov.it/v1/dgc/settings")

    def __init__(self, qr_data, schema_url, settings_url, params_string=False):

        i = -260
        j = 1

        if params_string:
            i = str(i)
            j = str(j)

        self.json = ''
        self.qr_data = qr_data[i][j]
        self.expires_at = datetime.datetime.strftime(
                datetime.datetime.fromtimestamp(qr_data[4]),
                '%Y-%m-%d')
        self.issued_at = qr_data[6]
        self.__set_schema(schema_url)
        self.__set_settings(settings_url)

    def _get_header(self):
        header = '<p><strong>Issued on</strong>' + ':' + datetime.datetime.utcfromtimestamp(self.issued_at) \
            .strftime('%Y-%m-%d') + '</p> '
        header += '<p><strong>Document expires at</strong>' + ':' + str(
            self.expires_at) + '</p>'
        return header

    def convert_json(self):
        if self.qr_data is None:
            raise DataMapperError("QR_DATA_IS_WRONG")
        if self.schema is None:
            raise DataMapperError("SCHEMA_IS_WRONG")
        self._save_json(self.qr_data, self.schema['properties'])
        return self._get_header() + self.json
