
from flask import Flask
# 导入扩展flask_session
from flask_session import Session
# 导入sqlalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 导入配置对象
from config import config_dict


# 实例化sqlalchemy对象
db = SQLAlchemy()

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

    # 导入蓝图
    from info.modules.news import news_blue
    app.register_blueprint(news_blue)

    return app


