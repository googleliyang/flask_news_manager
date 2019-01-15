
# 导入script扩展
from flask_script import Manager
# 导入migrate扩展
from flask_migrate import Migrate,MigrateCommand

# 导入程序实例app
from info import create_app,db

# 调用info/__init__.py文件中的工厂函数，获取app
app = create_app('development')

"""
项目目录搭建：
1、使用扩展实现基本功能
    按照学习的顺序，从后到前，依次使用
2、抽取代码，搭建项目目录

"""

# 实例化管理器对象
manage = Manager(app)
# 使用迁移框架
Migrate(app,db)
# 添加迁移命令
manage.add_command('db',MigrateCommand)



if __name__ == '__main__':
    # app.run(debug=True)
    print(app.url_map)
    manage.run()