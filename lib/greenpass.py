from pyzbar.pyzbar import decode
from PIL import Image
from base45 import b45decode
from zlib import decompress
from flynn import decoder as flynn_decoder
from lib.datamapper import DataMapper as data_mapper


class GreenPassDecoder(object):
    stream_data = None

    def __init__(self, stream_data):
        self.stream_data = decode(Image.open(stream_data))[0].data

    def decode(self, schema, settings):
        qr_decoded = self.stream_data[4:]
        qrcode_data = decompress(b45decode(qr_decoded))
        (_, (header_1, header_2, cbor_payload, sign)) = flynn_decoder.loads(qrcode_data)
        data = flynn_decoder.loads(cbor_payload)
        dm = data_mapper(data, schema, settings)
        return dm.convert_json()
