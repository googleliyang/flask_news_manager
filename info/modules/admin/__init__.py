from flask import Blueprint, session, request, url_for, redirect

admin_blue = Blueprint('admin',__name__,url_prefix='/admin')


from . import views

# 权限校验，作用：是让普通用户无法访问后台页面。
# 使用蓝图定义请求钩子，该请求钩子只会在蓝图被调用时执行。
@admin_blue.before_request
def check_admin():
    # 如果不是管理员，那么直接跳转到主页
    # print('admin run----')
    is_admin = session.get("is_admin", False)
    # 如果不是管理员，并且当前访问的url不是后台登录页
    # request.url.endswith('/admin/login')
    if not is_admin and not request.url.endswith(url_for('admin.login')):
        return redirect('/')


