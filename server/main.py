import os
import random
import json
import requests
from typing import Literal

from flask import *

app = Flask(__name__)

base = 'path/base.html'
webside = 'www.crazying-dev.top'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def get_random_file(dir_path):
    files = []
    for name in os.listdir(dir_path):
        fp = os.path.join(dir_path, name)
        if os.path.isfile(fp):
            files.append(fp)
    if not files:
        return None
    return os.path.abspath(os.path.normpath(random.choice(files)))


def http_request(url, method: Literal["GET", "POST"] = "GET", params=None, json_data=None, timeout=5):
    params = params or {}
    json_data = json_data or {}
    try:
        if method.upper() == "GET":
            resp = requests.get(url, params=params, timeout=timeout)
        elif method.upper() == "POST":
            resp = requests.post(url, params=params, json=json_data, timeout=timeout)
        else:
            return None, -1
        return resp.text, resp.status_code
    except requests.exceptions.RequestException:
        return None, 0


MOCK_WORK_DATA = [
    {"name": "fairy-forum", "from": "https://github.com/crazying-dev/fairy-forum", "run": 1, "join": 1, "help": 1},
    {"name": "MAIWR", "from": "https://github.com/crazying-dev/MAIWR", "run": 1, "join": 1, "help": 1},
    {"name": "crazying-dev", "from": "https://crazying-dev.top", "run": 1, "join": 0, "help": 1},
    {"name": "API", "from": "https://api.crazying-dev.top", "run": 1, "join": 0, "help": 0},
    {"name": "img", "from": "https://img.crazying-dev.top", "run": 1, "join": 0, "help": 0}
]

MOCK_POST_DATA = [
    {"title": "个人站完工", "link": "/post/1"},
    {"title": "Vue重构完成", "link": "/post/2"},
    {"title": "Flask后端部署", "link": "/post/3"}
]

MOCK_FRIEND_DATA = [
    {"name": "测试友人1", "url": "https://example.com", "img": "//img.crazying-dev.top/crazying-dev.top/me.png"},
    {"name": "测试友人2", "url": "https://example.com", "img": "//img.crazying-dev.top/crazying-dev.top/me.png"}
]


@app.route('/api/work')
def api_work():
    try:
        data, status = http_request('https://api.crazying-dev.top/work')
        if status == 200 and data:
            return jsonify(json.loads(data))
        return jsonify(MOCK_WORK_DATA), 200
    except:
        return jsonify(MOCK_WORK_DATA), 200


@app.route('/api/post')
def api_post():
    try:
        data, status = http_request('https://api.crazying-dev.top/post')
        if status == 200 and data:
            return jsonify(json.loads(data))
        return jsonify(MOCK_POST_DATA), 200
    except:
        return jsonify(MOCK_POST_DATA), 200


@app.route('/api/friend')
def api_friend():
    try:
        data, status = http_request('https://api.crazying-dev.top/friend')
        if status == 200 and data:
            return jsonify(json.loads(data))
        return jsonify(MOCK_FRIEND_DATA), 200
    except:
        return jsonify(MOCK_FRIEND_DATA), 200


@app.route('/')
def index():
    return render_template(base)


@app.route('/AboutMe')
def AboutMe():
    return render_template(base)


@app.route('/CommentMe')
def CommentMe():
    return render_template(base)


@app.route('/MyWrite')
def MyWrite():
    return render_template(base)


@app.route('/friend')
def friend():
    return render_template(base)


@app.route('/privacy')
def privacy():
    return render_template(base)


@app.route('/favicon.ico')
def favicon():
    return redirect("https://img.crazying-dev.top/crazying-dev.top/favicon.ico")


@app.route('/bg')
def bg():
    Type = request.args.get('type', None)
    if (Type is None) or (Type not in ['pc', 'mobile']):
        return abort(400)
    if Type == 'pc':
        file = get_random_file(os.path.join(BASE_DIR, 'img', 'bg', 'pc'))
        if file is None:
            return abort(500)
        return send_file(file, mimetype='image/webp')
    elif Type == 'mobile':
        file = get_random_file(os.path.join(BASE_DIR, 'img', 'bg', 'mobile'))
        if file is None:
            return abort(500)
        return send_file(file, mimetype='image/webp')
    abort(400)


@app.route('/rss.xml')
def rss():
    return redirect("https://api.crazying-dev.top/rss.xml")


@app.errorhandler(404)
def not_found(error):
    return render_template(base), 404


@app.route('/post/<int:post_id>')
def post(post_id):
    return render_template(base)


if __name__ == '__main__':
    app.run(debug=True)