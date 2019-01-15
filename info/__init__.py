from flask import Flask
# 导入扩展flask_session
from flask_session import Session
# 导入sqlalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 导入配置对象
from config import config_dict


# 实例化sqlalchemy对象
db = SQLAlchemy()


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


    return app


