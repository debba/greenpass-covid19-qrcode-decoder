from pyzbar.pyzbar import decode
from PIL import Image
from base45 import b45decode
from zlib import decompress
from flynn import decoder as flynn_decoder
from urllib.request import urlopen
from flask import Flask, request, render_template
from os.path import splitext
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4096 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png']
app.config[
    'DCC_SCHEMA'] = 'https://raw.githubusercontent.com/ehn-dcc-development/ehn-dcc-schema/release/1.3.0/DCC.combined-schema.json'
app.glb_schema = {}
app.converted_schema = ''


def recursive_save_data(data, schema, level=0):
    for key, value in data.items():
        description = schema[key].get('title') or schema[key].get('description') or key
        description, _, _ = description.partition(' - ')
        if type(value) is dict:
            app.converted_schema += '<p>' + ('&nbsp;' * level) + '<strong>' + description + '</strong>' + '</p>'
            _, _, sch_ref = schema[key]['$ref'].rpartition('/')
            recursive_save_data(value, app.glb_schema['$defs'][sch_ref]['properties'], level + 1)
        elif type(value) is list:
            app.converted_schema += '<p>' + ('&nbsp;' * level) + '<strong>' + description + '</strong>' + '</p>'
            _, _, sch_ref = schema[key]['items']['$ref'].rpartition('/')
            for v in value:
                recursive_save_data(v, app.glb_schema['$defs'][sch_ref]['properties'], level + 1)
        else:  # value is scalar
            app.converted_schema += '<p>' + ('&nbsp;' * level) + '<strong>' + description + '</strong>' + ':' + str(
                value) + '</p>'


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/qrdata', methods=['POST'])
def qrdata():
    if request.files['image'].filename != '':
        app.converted_schema = ''
        image = request.files['image']
        filename = image.filename
        file_ext = splitext(filename)[1]
        if filename != '':
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                return render_template('error.html', error='UPLOAD_EXTENSIONS_ERROR'), 400

        qr_decoded = decode(Image.open(image.stream))[0].data[4:]
        qrcode_data = decompress(b45decode(qr_decoded))
        (_, (header_1, header_2, cbor_payload, sign)) = flynn_decoder.loads(qrcode_data)
        data = flynn_decoder.loads(cbor_payload)

        sch = urlopen(app.config['DCC_SCHEMA'])
        app.glb_schema = json.load(sch)

        recursive_save_data(data[-260][1], app.glb_schema['properties'])

        return render_template('data.html', data=app.converted_schema)
    return render_template('error.html', error='UPLOAD_IMAGE_WITH_NO_NAME')


if __name__ == '__main__':
    app.run(debug=True)
