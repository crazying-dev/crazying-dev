from APP import *


@app.route('/GET')
def indexGet():
	return render_template('index.html')


@app.route('/AboutMe/GET')
def AboutMeGet():
	return render_template('HTML/AboutMe.html')
