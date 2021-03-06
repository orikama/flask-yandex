from flask import Flask, redirect, request, render_template
import requests

from my_app import MyApp
from yandex_images import FuckinCaptchaError

app = Flask(__name__)

bla_bla = MyApp(1080, 1920)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def post():
    text = request.form['text']

    try:
        img_sources = bla_bla.get_images(text, 6)
    except FuckinCaptchaError as e:
        return e.html_captcha

    return render_template('index.html', text=text, img_sources=img_sources)


# NOTE: The mystery behind handling captcha remained unsolved
@app.route('/checkcaptcha', methods=['POST', 'GET'])
def fuckin_captcha():
    key = request.args.get('key', default = '*', type = str)
    retpath = request.args.get('retpath', default = '*', type = str)
    rep = request.args.get('rep', default = '*', type = str)

    params = {
        "key": key,
        "retpath": retpath,
        "rep": rep,
    }

    resp = requests.get('https://yandex.ru/checkcaptcha', params)

    return resp.content #redirect('/')


if __name__ == '__main__':
    app.debug = True
    app.run()
