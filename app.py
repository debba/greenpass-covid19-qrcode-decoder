from flask import Flask, redirect, request, render_template
from os.path import splitext
from flask_sslify import SSLify
from flask_babel import Babel, gettext
import os
from lib.greenpass import GreenPassDecoder as greenpass_decoder

is_prod = os.environ.get('PRODUCTION', None)
ga_id = os.environ.get('GA_ID', None)
sharethis_script_src = os.environ.get('SHARETHIS_SCRIPT_SRC', None)
app_url = os.environ.get('APP_URL', None)

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
                sharethis_script_src=sharethis_script_src, app_url=app_url,
                app_name=gettext('Green Pass COVID-19 QRCode Decoder'))


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/qrdata', methods=['GET', 'POST'])
def qrdata():
    if request.method == 'POST':
        if request.files['image'].filename != '':
            app.converted_schema = ''
            image = request.files['image']
            filename = image.filename
            file_ext = splitext(filename)[1]
            if filename != '':
                if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                    return render_template('error.html', error='UPLOAD_EXTENSIONS_ERROR', file_ext=file_ext), 400

            try:
                decoder = greenpass_decoder(image.stream)
                return render_template('data.html', data=decoder.decode(app.config['DCC_SCHEMA']))
            except (ValueError, IndexError) as e:
                print(e)
                return render_template('error.html', error='UPLOAD_IMAGE_NOT_VALID'), 400

        return render_template('error.html', error='UPLOAD_IMAGE_WITH_NO_NAME'), 500
    else:
        return redirect('/')