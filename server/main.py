import os
import random

from flask import *

app = Flask(__name__)


base = 'path/base.html'

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



@app.route('/')
def index():
	return render_template(base)


@app.route('/AboutMe')
def AboutMe():
	print(2)
	return render_template(base)



@app.route('/bg')
def bg():
	Type = request.args.get('type', None)
	if (Type is None) or (Type not in ['pc', 'mobile']):
		return abort(404)
	if Type == 'pc':
		file = get_random_file('/static/img/bg/pc')
		if file is None:
			return abort(404)
		return send_file(file, mimetype='image/webg')
	elif Type == 'mobile':
		file = get_random_file('/static/img/bg/mobile')
		if file is None:
			return abort(404)
		return send_file(file, mimetype='image/webg')
	abort(404)


if __name__ == '__main__':
	app.run(debug=True)
