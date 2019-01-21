from flask import render_template, g, redirect, request, jsonify, current_app, session
from info.utils.commons import login_required
from info.utils.response_code import RET
from info import db
# 导入蓝图
from . import profile_blue

# http://127.0.0.1:5000/user/info
@profile_blue.route("/info")
@login_required
def user_info():
    """
    用户基本信息显示
    1、尝试获取用户信息
    2、如果用户未登录，重定向到项目首页
    3、如果用户已登录，调用模型类中的to_dict函数，获取用户信息
    4、传给模板

    :return:
    """
    user = g.user
    if not user:
        return redirect('/')
    data = {
        'user':user.to_dict()
    }

    return render_template('news/user.html',data=data)

@profile_blue.route('/base_info',methods=['GET','POST'])
@login_required
def base_info():
    """
    用户中心基本资料页面(子页面)
    1、尝试获取用户信息
    2、如果用户已登录，请求方法为get请求，默认加载模板页面
    3、如果是post请求，获取参数
    nick_name,signature,gender
    4、检查参数的完整性
    5、检查性别参数的范围
    6、保存用户信息，直接使用user对象
    7、提交数据到mysql
    8、把redis中缓存的昵称换成修改后的昵称
    9、返回结果

    :return:
    """
    user = g.user
    if request.method == 'GET':
        data = {
            'user': user.to_dict()
        }
        return render_template('news/user_base_info.html',data=data)
    # 获取参数
    nick_name = request.json.get('nick_name')
    signature = request.json.get('signature')
    gender = request.json.get('gender')
    # 检查参数的完整性
    if not all([nick_name,signature,gender]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')
    # 检查性别参数的范围
    if gender not in ['MAN','WOMAN']:
        return jsonify(errno=RET.PARAMERR,errmsg='参数格式错误')
    # 保存用户信息
    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender
    # 提交数据
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')
    # 修改redis缓存中的用户信息
    session['nick_name'] = nick_name
    # 返回结果
    return jsonify(errno=RET.OK,errmsg='OK')







    pass
