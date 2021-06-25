from pyzbar.pyzbar import decode
from PIL import Image
from base45 import b45decode
from zlib import decompress
from flynn import decoder as flynn_decoder
from flask import Flask, request, render_template
from os.path import splitext
from flask_sslify import SSLify
from flask_babel import Babel, gettext
import os
from lib.datamapper import DataMapper as data_mapper

is_prod = os.environ.get('PRODUCTION', None)
ga_id = os.environ.get('GA_ID', None)

app = Flask(__name__)

app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['MAX_CONTENT_LENGTH'] = 4096 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.jpeg']
app.config['GITHUB_PROJECT'] = 'https://github.com/debba/greenpass-covid19-qrcode-decoder'
app.config[
    'DCC_SCHEMA'] = 'https://raw.githubusercontent.com/ehn-dcc-development/ehn-dcc-schema/release/1.3.0/DCC.combined-schema.json'
app.glb_schema = {}
app.converted_schema = ''
app.config['LANGUAGES'] = {
    'en': 'English',
    'it': 'Italiano'
}
babel = Babel(app)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())


if is_prod:
    sslify = SSLify(app)


@app.context_processor
def inject_user():
    return dict(github_project=app.config['GITHUB_PROJECT'], is_prod=is_prod, ga_id=ga_id,
                app_name=gettext('Green Pass COVID-19 QRCode Decoder'))


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
                return render_template('error.html', error='UPLOAD_EXTENSIONS_ERROR', file_ext=file_ext), 400

        qr_decoded = decode(Image.open(image.stream))[0].data[4:]
        qrcode_data = decompress(b45decode(qr_decoded))
        (_, (header_1, header_2, cbor_payload, sign)) = flynn_decoder.loads(qrcode_data)
        data = flynn_decoder.loads(cbor_payload)
        dm = data_mapper(data, app.config['DCC_SCHEMA'])
        return render_template('data.html', data=dm.convert_json())
    return render_template('error.html', error='UPLOAD_IMAGE_WITH_NO_NAME')


if __name__ == '__main__':
    app.run(debug=True)
