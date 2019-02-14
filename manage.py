# 导入script扩展
from flask_script import Manager
# 导入migrate扩展
from flask_migrate import Migrate,MigrateCommand

# 导入程序实例app
from info import create_app,db,models

# 调用info/__init__.py文件中的工厂函数，获取app
from info.models import User

app = create_app('development')

"""
项目目录搭建：
1、使用扩展实现基本功能
    按照学习的顺序，从后到前，依次使用
2、抽取代码，搭建项目目录

*********************************
项目接口数据交互的思路：是使用request.json/form/args.....???
1、如果是get请求，就是args；判断交互的数据(参数)是不是敏感数据？如果不是隐私数据，就使用args。
2、如果是表单提交，建议是post请求，比如登录、注册、发布信息等，form/json。
3、后端代码返回数据，还是从redis中取数据，需要判断前端需不需要数据，如果需要就返回，否则不返回！
4、redis中一般会存临时数据，避免频繁读写mysql的磁盘数据，提高项目的性能。



"""

# 实例化管理器对象
manage = Manager(app)
# 使用迁移框架
Migrate(app,db)
# 添加迁移命令
manage.add_command('db',MigrateCommand)

"""
数据库迁移步骤：
1、生成迁移仓库
python manage.py db init
2、生成迁移文件(脚本)
python manage.py db migrate -m 'init_tables'
3、执行迁移文件
python manage.py db upgrade

"""

# 创建管理员账户
# 在script扩展，自定义脚本命令，以自定义函数的形式实现创建管理员用户
# 以终端启动命令的形式实现；
# 在终端使用命令：
# python manage.py create_supperuser -n 用户名 -p 密码
# python manage.py db init
@manage.option('-n', '-name', dest='name')
@manage.option('-p', '-password', dest='password')
def create_supperuser(name, password):
    if not all([name, password]):
        print('参数缺失')
    user = User()
    user.nick_name = name
    user.mobile = name
    user.password = password
    user.is_admin = True
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    print('管理员创建成功')

if __name__ == '__main__':
    # app.run(debug=True)
    print(app.url_map)
    manage.run()