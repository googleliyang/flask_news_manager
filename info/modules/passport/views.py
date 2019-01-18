# 导入flask内置的对象
from flask import request,jsonify,current_app,make_response,session
# 导入蓝图对象
from . import passport_blue
# 导入自定义的状态码
from info.utils.response_code import RET
# 导入工具captcha
from info.utils.captcha.captcha import captcha
# 导入redis数据库的实例
from info import redis_store,constants,db
# 导入正则
import re,random
# 导入云通讯
from info.libs.yuntongxun.sms import CCP
# 导入模型类
from info.models import User
# 导入日期模块
from datetime import datetime

# 前端index.html文件中的153行img标签的src属性，
# 应该指向当前的视图函数
@passport_blue.route("/image_code")
def generate_image_code():
    """
    生成图片验证码
    # var url = '/image_code?image_code_id=' + imageCodeId;
    1、获取uuid，image_code_id
    2、判断获取是否成功，如果没有uuid，直接终止程序运行
    3、调用captcha扩展包，生成图片验证码，name，text，image
    4、把图片验证码的内容，存入redis数据库，根据uuid作为后缀名
    5、把图片返回前端
    'http://127.0.0.1:5000/?a=1&b=' + 2
    http://127.0.0.1:5000/?a=1&b=2
    :return:
    """
    # 获取参数
    image_code_id = request.args.get("image_code_id")
    # 判断参数是否存在，如果参数不存在，直接终止程序运行
    if not image_code_id:
        return jsonify(errno=RET.PARAMERR,errmsg='参数缺失')
    # 如果有uuid，调用工具captcha生成图片验证码
    name,text,image = captcha.generate_captcha()
    # 把图片验证码的text内容存入redis数据库
    try:
        redis_store.setex('ImageCode_' + image_code_id,constants.IMAGE_CODE_REDIS_EXPIRES,text)
    except Exception as e:
        # 操作数据库，如果发生异常，需要记录项目日志
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')
    # 把图片返回前端,使用响应对象，返回图片
    response = make_response(image)
    # 修改响应的数据类型，不修改浏览器可以解析，因为浏览器使用的img标签，但是如果通过测试工具测接口，无法显示图片！！
    response.headers['Content-Type'] = 'image/jpg'
    return response



@passport_blue.route('/sms_code',methods=['POST'])
def send_sms_code():
    """
    发送短信
    获取参数----检查参数----业务处理----返回结果
    1、获取参数，前端ajax发送过来的手机号、图片验证码、图片验证码的编号(uuid)
    2、检查参数的完整性，mobile,image_code,image_code_id
    3、检查手机号格式，正则
    4、尝试从redis中获取真实的图片验证码，根据uuid来从redis中拿出唯一的图片验证码
    5、判断获取是否成功
    6、如果获取成功，应该把redis中存储的图片验证码给删了，因为图片验证码只能比较一次，所以只能读取redis数据库一次
    7、比较图片验证码是否正确
    8、生成6位数的随机数，作为短信验证码
    9、把短信验证码存入redis数据库中，便于后面用户注册时进行比较
    10、调用云通讯发送短信，保存发送结果
    11、判断发送是否成功
    12、返回结果

    var params = {
        'mobile':mobile,
        'image_code':imageCode,
        'image_code_id':imageCodeId
    }

    :return:
    """
    # 获取参数
    mobile = request.json.get('mobile')
    image_code = request.json.get("image_code")
    image_code_id = request.json.get("image_code_id")
    # 检查参数的完整性
    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')
    # 检查手机号的格式:13012345678 99999
    if not re.match(r'1[3456789]\d{9}$',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')
    # ------

    # 检查图片验证码，对比，从redis中获取真实的图片验证码和用户的图片验证码进行比较
    try:
        real_image_code = redis_store.get('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='获取数据失败')
    # 判断数据是否存在
    if not real_image_code:
        return jsonify(errno=RET.NODATA,errmsg='数据已过期')
    # 如果数据存在，把redis中的数据删除
    try:
        redis_store.delete('ImageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    # 比较图片验证码是否正确
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR,errmsg='图片验证码错误')
    # 检查手机号是否注册
    try:
        # User.query.filter_by(mobile=mobile).first()
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询用户数据失败')
    else:
        # 判断查询结果，用户是否注册
        if user is not None:
            return jsonify(errno=RET.DATAEXIST,errmsg='手机号已注册')

    # 生成6位数的短信随机码
    sms_code = '%06d' % random.randint(0, 999999)
    print(sms_code)
    # 存入redis数据库
    try:
        redis_store.setex('SMSCode_' + mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='保存短信验证码失败')
    # 调用云通讯，发送短信
    try:
        ccp = CCP()
        # 第一个参数表示手机号，第二个参数为列表(短信验证码的内容，有效期)，第三个参数为测试模板编号1
        result = ccp.send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES/60],1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg='发送短信异常')
    # 判断发送结果
    if result == 0:
        return jsonify(errno=RET.OK,errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRDERR,errmsg='发送失败')


@passport_blue.route('/register',methods=['POST'])
def register():
    """
    用户注册---本质是把用户信息写入mysql数据库
    获取参数----检查参数----业务处理----返回结果
    1、获取参数，mobile，sms_code,password
    2、检查参数的完整性
    3、检查手机号格式
    4、检查短信验证码，尝试从redis中获取真实的短信验证码
    5、判断获取结果
    6、先比较短信验证码是否正确，因为短信验证码可以比较多次！！比较多次的本质就是可以get数据库多次
    7、删除redis中存储的真实短信验证码
    8、确认用户未注册
    9、使用模型类保存用户数据，密码进行加密存储
    10、提交数据到mysql数据库，如果发生异常，需要回滚
    11、实现状态保持，缓存用户信息到redis中
    12、返回结果

    """
    # 获取参数
    mobile = request.json.get("mobile")
    sms_code = request.json.get("sms_code")
    password = request.json.get("password")
    # 检查参数的完整性
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')
    # 检查手机号格式
    if not re.match(r'1[3456789]\d{9}$',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')
    # 尝试从redis中获取短信验证码
    try:
        real_sms_code = redis_store.get('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据失败')
    # 判断查询结果
    if not real_sms_code:
        return jsonify(errno=RET.NODATA,errmsg='数据已过期')
    # 先比较短信验证码是否正确
    if real_sms_code != str(sms_code):
        return jsonify(errno=RET.DATAERR,errmsg='短信验证码错误')
    # 删除redis中的短信验证码
    try:
        redis_store.delete('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
    # 确认用户是否已注册
    try:
        # User.query.filter_by(mobile=mobile).first()
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询用户数据失败')
    else:
        # 判断查询结果，用户是否注册
        if user is not None:
            return jsonify(errno=RET.DATAEXIST,errmsg='手机号已注册')
    # 构造模型类对象，保存用户数据
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # 本质上调用了模型类中的generate_password_hash函数(werkzeug模块)，实现了密码加密存储
    user.password = password
    # 提交数据到mysql
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 如果保存数据发生异常，需要进行回滚
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')
    # 缓存用户信息，实现状态保持
    session['user_id'] = user.id
    session['mobile'] = mobile
    session['nick_name'] = mobile
    # 返回结果
    return jsonify(errno=RET.OK,errmsg='注册成功')


@passport_blue.route("/login",methods=['POST'])
def login():
    """
    登录
    获取参数----检查参数----业务处理----返回结果
    1、获取参数，mobile，password
    2、检查参数的完整性
    3、检查手机号格式
    4、根据手机号查询数据库，确认用户已注册
    5、判断查询结果
    6、判断密码是否正确
    7、保存用户的登录时间，提交数据到mysql数据库
    8、实现状态保持
    9、返回结果
    user = User()
    user.check_password(password)
    user = User.query.filter(User.mobile==mobile).first()
    user.check_psssword(password)

    :return:
    """
    # 获取参数
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    # 检查参数的完整性
    if not all([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg='参数错误')
    # 检查手机号格式
    if not re.match(r'1[3456789]\d{9}$',mobile):
        return jsonify(errno=RET.PARAMERR,errmsg='手机号格式错误')
    # 根据手机号查询用户是否存在
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询数据失败')

    # 判断查询结果是否存在
    # if not user:
    #     return jsonify(errno=RET.NODATA,errmsg='用户未注册')
    # 判断密码是否正确
    # if not user.check_password(password):
    #     return jsonify(errno=RET.PWDERR,errmg='密码错误')

    # 判断用户和密码
    if not user or not user.check_password(password):
        return jsonify(errno=RET.PWDERR,errmsg='用户名或密码错误')
    # 保存用户的登录时间
    # 如果是import datetime 调用：datetime.datetime.now()
    user.last_login = datetime.now()
    # 提交数据到mysql
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg='保存数据失败')
    # 状态保持，缓存用户信息
    session['user_id'] = user.id
    session['mobile'] = mobile
    # 登录可以执行多次,如果用户修改了昵称，为修改后的结果，如果没有修改，还是手机号
    session['nick_name'] = user.nick_name
    # 返回结果
    return jsonify(errno=RET.OK,errmsg='OK')

    pass











