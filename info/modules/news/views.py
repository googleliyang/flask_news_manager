from flask import session
# 导入蓝图对象
from . import news_blue

@news_blue.route("/")
def index():
    session['itcast'] = '2019'
    return 'hello world2019'


