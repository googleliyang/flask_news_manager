from flask import session,render_template,current_app
# 导入蓝图对象
from . import news_blue
# 导入模型类
from info.models import User


@news_blue.route("/")
def index():
    """
    项目首页加载
    1、使用模板加载项目首页----把static文件夹粘贴到info/目录下
    展示用户信息：检查用户登录状态-----如果用户已登录显示用户信息，否则提供登录注册入口
    1、尝试从redis中获取用户的session信息
    2、如果获取到user_id,根据user_id查询用户信息
    3、把查询结果作为用户数据返回给模板
    :return:
    """
    # 从redis中获取user_id
    user_id = session.get('user_id')
    # 根据user_id查询mysql数据库
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 定义字典，给模板传入用户数据
    # if user:
    #     user.to_dict()
    # else:
    #     user = None

    data = {
        'user_info':user.to_dict() if user else None
    }

    return render_template('news/index.html',data=data)


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
