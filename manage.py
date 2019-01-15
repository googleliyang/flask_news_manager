from flask import Flask,session
# 导入扩展flask_session
from flask_session import Session

# 导入sqlalchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 导入script扩展
from flask_script import Manager
# 导入migrate扩展
from flask_migrate import Migrate,MigrateCommand
# 导入配置对象
from config import config_dict

app = Flask(__name__)
# 使用抽取出去的配置信息
app.config.from_object(config_dict['development'])

"""
项目目录搭建：
1、使用扩展实现基本功能
    按照学习的顺序，从后到前，依次使用
2、抽取代码，搭建项目目录

"""
# 让Session扩展和程序实例进行关联
Session(app)
# 实例化sqlalchemy对象
db = SQLAlchemy(app)
# 实例化管理器对象
manage = Manager(app)
# 使用迁移框架
Migrate(app,db)
# 添加迁移命令
manage.add_command('db',MigrateCommand)

@app.route("/")
def index():
    session['itcast'] = '2019'
    return 'hello world2018'


if __name__ == '__main__':
    # app.run(debug=True)
    manage.run()