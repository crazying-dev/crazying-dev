import os
import random
import json

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



#GET.py
@app.route('/GET')
def indexGet():
	return render_template('index.html')


@app.route('/AboutMe/GET')
def AboutMeGet():
	return render_template('HTML/AboutMe.html')

@app.route('/post/<int:id>/GET')
def postGet(id):
	Type = request.args.get('type', None)
	with open(f'post/{id}.json','r') as _f:
		info = json.loads(_f.read())
	if Type == 'avatar':
		return info['avatar']
	elif Type == 'message':
		return info['message']
	elif Type == 'data':
		return info['data']
	elif Type == 'desc':
		return info['desc']
	elif Type == 'title':
		return info['title']
	elif Type is None:
		return render_template('/path/post.html')
	else:
		return abort(400)
		
#GET.py end

#page.py
@app.route('/')
def index():
	return render_template(base)


@app.route('/AboutMe')
def AboutMe():
	print(2)
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
	f = app.open_resource('posts.json', 'r', encoding='utf-8')
	posts = json.loads(f.read().replace('<;;;>',f'https://{webside}'))
	

	xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
	xml += '<rss version="2.0">\n<channel>\n'
	xml += f'<title>我的站点</title>\n<link>{webside}</link>\n<description>个人博客</description>\n'

	for p in posts:
		xml += f"""
<item>
  <title>{p['title']}</title>
  <link>{p['link']}</link>
  <description>{p['desc']}</description>
  <pubDate>{p['date']}</pubDate>
</item>
"""
	xml += '</channel>\n</rss>'

	res = make_response(xml)
	res.headers["Content-Type"] = "application/xml"
	f.close()
	return res

@app.route('/post/<int:id>')
def post(id):
	return render_template(base)

	
@app.errorhandler(404)
def not_found(error):
	return render_template('error/404.html'),404

if __name__ == '__main__':
	app.run(debug=True)
