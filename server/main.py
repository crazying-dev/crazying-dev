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

# tool.py
def get_random_file(dir_path):
	# 收集所有文件
	files = []
	for name in os.listdir(dir_path):
		fp = os.path.join(dir_path, name)
		if os.path.isfile(fp):
			files.append(fp)
	if not files:
		return None
	return os.path.abspath(os.path.normpath(random.choice(files)))

# tool.py end


def http_request(url, method: Literal["GET", "POST"] = "GET", params=None, json_data=None, timeout=5):
	"""
	    通用 HTTP 请求函数
	    :param url: 请求地址
	    :param method: 请求方式，GET / POST
	    :param params: URL 查询参数，字典
	    :param json_data: POST JSON 体，字典
	    :param timeout: 超时时间
	    :return: 响应文本 / 错误信息
	    """
	params = params or {}
	json_data = json_data or {}
	
	try:
		if method.upper() == "GET":
			resp = requests.get(url, params=params, timeout=timeout)
		elif method.upper() == "POST":
			resp = requests.post(url, params=params, json=json_data, timeout=timeout)
		else:
			# 方法不合法：内容None，自定义状态码-1
			return None, -1
		
		# 正常返回：(响应内容, 真实HTTP状态码)
		return resp.text, resp.status_code
	
	except requests.exceptions.RequestException:
		# 网络、超时、连接失败等：内容None，自定义状态码0
		return None, 0



#GET.py
@app.route('/GET')
def indexGet():
	return render_template('index.html')


@app.route('/AboutMe/GET')
def AboutMeGet():
	return render_template('HTML/AboutMe.html')


		
#GET.py end

#page.py
@app.route('/')
def index():
	return render_template(base)


@app.route('/AboutMe')
def AboutMe():
	return render_template(base)

#   page.py end

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
		return send_file(file, mimetype='image/webg')
	elif Type == 'mobile':
		file = get_random_file(os.path.join(BASE_DIR, 'img', 'bg', 'mobile'))
		if file is None:
			return abort(500)
		return send_file(file, mimetype='image/webg')
	abort(400)

@app.route('/rss.xml')
def rss():
	return redirect("https://api.crazying-dev.top/rss.xml")
	
@app.errorhandler(404)
def not_found(error):
	return render_template('error/404.html'),404


@app.route('/post/<int:post_id>')
def post(post_id):
	return render_template(base)

@app.route('/post/<int:post_id>/GET')
def postGET(post_id):
	return render_template("/HTML/PostBase.html")


if __name__ == '__main__':
	app.run(debug=True)
