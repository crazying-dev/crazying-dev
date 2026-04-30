from GET import *
from tool import *

base = '/path/base.html'


@app.route('/')
def index():
	return render_template(base)


@app.route('/AboutMe')
def AboutMe():
	print(2)
	return render_template(base)


@app.route('/bg')
def bg():
	Type = request.args.get('Type', None)
	if (Type is None) or (Type not in ['pc', 'mobile']):
		return abort(404)
	if Type == 'pc':
		file = get_random_file('./static/img/bg/pc')
		if file is None:
			return abort(404)
		return send_file(file, mimetype='image/webg')
	elif Type == 'mobile':
		file = get_random_file('./static/img/bg/mobile')
		if file is None:
			return abort(404)
		return send_file(file, mimetype='image/webg')
	abort(404)


if __name__ == '__main__':
	app.run(debug=True)
