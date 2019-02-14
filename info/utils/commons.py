from info.models import User
from flask import session, current_app,g


# 定义函数，实现对模板数据的格式化输出
def index_filter(index):
    if index == 0:
        return 'first'
    elif index == 1:
        return 'second'
    elif index == 2:
        return 'third'
    else:
        return ''

# 装饰器：封装检查用户登录状态的代码,
# 概念：不修改原有代码的前提下，添加新的功能，本质是闭包。。。
# 问题：封装代码后，在视图函数中使用装饰器，发现被装饰的函数名变成了wrapper！装饰器修改了被装饰的函数的属性__name__

# functools模块的作用：让被装饰器装饰的函数的属性不发生变化。
import functools

def login_required(f):
    @functools.wraps(f)
    def wrapper(*args,**kwargs):
        user_id = session.get('user_id')
        # 根据user_id查询mysql数据库
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        # 使用应用上下文对象g，来临时存储用户数据，
        # 把查询结果的user对象，赋值给g的属性存储
        g.user = user

        return f(*args,**kwargs)
    # wrapper.__name__ = f.__name__
    return wrapper



