from flask import Flask,session
# 导入扩展flask_session
from flask_session import Session
# 导入redis模块
from redis import StrictRedis

app = Flask(__name__)
# 配置密钥
app.config['SECRET_KEY'] = 'mMr88P+cvbxFXvcpX9PpiBTWMDLtGNkI7fwKhVv7GWuv9QZyRoyUsw=='
# 配置状态保持session信息的存储
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = StrictRedis(host='127.0.0.1',port=6379)
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400

"""
项目目录搭建：
1、使用扩展实现基本功能
    按照学习的顺序，从后到前，依次使用
2、抽取代码，搭建项目目录

"""
# 让Session扩展和程序实例进行关联
Session(app)

@app.route("/")
def index():
    session['itcast'] = '2019'
    return 'hello world2018'


if __name__ == '__main__':
    app.run(debug=True)