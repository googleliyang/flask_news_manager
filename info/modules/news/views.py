from flask import session,render_template,current_app
# 导入蓝图对象
from . import news_blue

@news_blue.route("/")
def index():
    """
    项目首页加载
    1、使用模板加载项目首页----把static文件夹粘贴到info/目录下


    :return:
    """
    session['itcast'] = '2019'
    return render_template('news/index.html')


@news_blue.route("/favicon.ico")
def favicon():
    """
    网站favicon图标的加载：
    1、浏览器自动加载，默认会访问的url，以获取图标：http://127.0.0.1:5000/favicon.ico
    2、定义路由，route('/favicon.ico'),实现把文件发送给浏览器，找到static/news/favicon.ico文件的路径。

    代码实现后，浏览器无法获取favicon图标的解决办法：
    1、清除浏览器浏览记录
    2、清除浏览器缓存
    3、彻底退出浏览器，重新启动。

    原因：因为浏览器加载favicon不是每次请求都加载。

    """
    return current_app.send_static_file('news/favicon.ico')
