from flask import Flask, render_template
from eapi import eapi_bp
from auth import auth_bp

app = Flask(__name__)
app.register_blueprint(eapi_bp, url_prefix='/api/e')   # 注册电费 API 蓝图
app.register_blueprint(auth_bp, url_prefix='/auth') # 注册登录蓝图

# app.register_blueprint()

@app.route('/')
def index():
    return render_template("login.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
