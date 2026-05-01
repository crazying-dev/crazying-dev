from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "✅ Flask 运行成功！"

if __name__ == '__main__':
    app.run()