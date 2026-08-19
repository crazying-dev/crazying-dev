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


@app.route('/CommentMe/GET')
def CommentMeGet():
	return render_template('HTML/CommentMe.html')


@app.route('/MyWrite/GET')
def MyWriterGet():
	return render_template('HTML/MyWriter.html')


@app.route('/friend/GET')
def FriendGet():
	return render_template('HTML/Friend.html')


@app.route('/privacy/GET')
def PrivacyGet():
	return render_template('HTML/Privacy.html')


#GET.py end
#api.py
import re

@app.route('/api/xhs-title')
def get_xhs_title():
    url = request.args.get('url', '')
    if not url:
        return jsonify({'error': '缺少 url 参数'}), 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        resp.encoding = resp.apparent_encoding or 'utf-8'
        html = resp.text

        # 提取 <title> 标签内容
        match = re.search(r'<title\b[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if not match:
            return jsonify({'error': '未找到页面标题'}), 404

        title = match.group(1).strip()
        # 截取 " - 小红书" 前的内容（兼容 "- 小红书" 或 " - 小红书 RED" 等）
        if ' - 小红书' in title:
            title = title.split(' - 小红书')[0].strip()
        elif '-小红书' in title:
            title = title.split('-小红书')[0].strip()

        return jsonify({'title': title})
    except Exception as e:
        return jsonify({'error': f'请求失败: {str(e)}'}), 500


@app.route('/api/bili-title')
def get_bili_title():
    url = request.args.get('url', '')
    if not url:
        return jsonify({'error': '缺少 url 参数'}), 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com/'
        }
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        data = resp.json()

        # 从 JSON 中提取用户名
        if data.get('code') == 0:
            name = None
            # web-interface/card 接口: data.card.name
            if 'card' in data.get('data', {}):
                name = data['data']['card'].get('name')
            # space/acc/info 接口: data.name
            elif 'name' in data.get('data', {}):
                name = data['data'].get('name')

            if name:
                return jsonify({'title': name})

        return jsonify({'error': '未能从 API 响应中提取用户名'}), 404
    except Exception as e:
        return jsonify({'error': f'请求失败: {str(e)}'}), 500

#api.py end
#page.py
@app.route('/')
def index():
	return render_template(base, content_template='index.html')

@app.route('/AboutMe')
def AboutMe():
	return render_template(base, content_template='HTML/AboutMe.html')

@app.route('/CommentMe')
def CommentMe():
	return render_template(base, content_template='HTML/CommentMe.html')

@app.route('/MyWrite')
def MyWrite():
	return render_template(base, content_template='HTML/MyWriter.html')

@app.route('/friend')
def friend():
	return render_template(base, content_template='HTML/Friend.html')

@app.route('/privacy')
def privacy():
	return render_template(base, content_template='HTML/Privacy.html')


#page.py end

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
	return render_template('error/404.html'), 404


@app.route('/post/<int:post_id>')
def post(post_id):
	return render_template(base)


@app.route('/post/<int:post_id>/GET')
def postGET(post_id):
	return render_template("/HTML/PostBase.html")

@app.route('/pinshu/phone')
def PinShu_Phone():
	return render_template("/PinShu/Phone.html")


if __name__ == '__main__':
	app.run()
