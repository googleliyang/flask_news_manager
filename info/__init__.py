from flask import Flask
# 导入扩展flask_session
from flask_session import Session
# 导入sqlalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 导入配置对象
from config import config_dict,Config
# 导入redis的连接对象
from redis import StrictRedis
# 导入wtf扩展包提供的csrf保护模块
from flask_wtf import CSRFProtect,csrf


# 实例化sqlalchemy对象
db = SQLAlchemy()
# 实例化redis对象，用来保存和业务相关的数据，比如图片验证码，短信验证码
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT,decode_responses=True)

# 导入标准日志模块和日志处理模块
import logging
from logging.handlers import RotatingFileHandler


# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG) # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)


# 定义工厂函数，封装创建程序实例的代码；
# 作用：可以给函数传入参数，动态的决定，以什么模式下运行代码,
def create_app(config_name):

    app = Flask(__name__)
    # 使用抽取出去的配置信息
    app.config.from_object(config_dict[config_name])

    # 让Session扩展和程序实例进行关联
    Session(app)
    # 通过函数，实现db和app的关联
    db.init_app(app)
    # 项目开启csrf保护
    CSRFProtect(app)
    # 生成csrf_token令牌，给每个请求的客户端
    """
    csrf保护的实现：
    1、在后端首先开启保护，CSRFProtect会验证http请求方法中的post、put、patch、delete四种；
    2、还会验证请求头中是否设置X-CSRFToken或者X-CSRF-Token其中之一。
    3、会比较ajax请求信息中的token和cookie中的token是否一致，如果一致，请求合法，否则，滚！
    区别：
    1、原来是表单，比较的是表单中的token和cookie中的token是否一致。
    2、现在是ajax，比较的是ajax中token和cookie中的token是否一致。
    
    """
    @app.after_request
    def after_request(response):
        csrf_token = csrf.generate_csrf()
        response.set_cookie('csrf_token',csrf_token)
        return response

    # 导入自定义的过滤器
    from info.utils.commons import index_filter
    # 第一个参数表示自定义的函数名，第二个参数表示过滤器的名称
    app.add_template_filter(index_filter,'index_filter')


    # 导入蓝图
    from info.modules.news import news_blue
    app.register_blueprint(news_blue)
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)
    from info.modules.profile import profile_blue
    app.register_blueprint(profile_blue)

    from info.modules.admin import admin_blue
    app.register_blueprint(admin_blue)

    return app



"""
import hashlib

hashlib.md5
hashlib.sha256
from werkzeug.security import  generate_password_hash,check_password_hash

"""

