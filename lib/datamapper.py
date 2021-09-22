import json
from urllib.request import urlopen


class DataMapperError(Exception):
    pass


class DataMapper:
    qr_data = None
    schema = None

    json = ''
    new_json = {}

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
                        self.json += '<p>' + ('&nbsp;' * level) + '<strong>' + description + '</strong>' + ':' + str(
                            value) + '</p>'
                except KeyError:
                    print('error keys')
                    print(data)

    def __set_schema(self, schema_url):
        sch = urlopen(schema_url)
        self.schema = json.load(sch)

    def __init__(self, qr_data, schema_url, params_string=False):

        i = -260
        j = 1

        if params_string:
            i = str(i)
            j = str(j)

        self.json = ''
        self.qr_data = qr_data[i][j]
        self.__set_schema(schema_url)

    def convert_json(self):
        if self.qr_data is None:
            raise DataMapperError("QR_DATA_IS_WRONG")
        if self.schema is None:
            raise DataMapperError("SCHEMA_IS_WRONG")
        self._save_json(self.qr_data, self.schema['properties'])
        return self.json
