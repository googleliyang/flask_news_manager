# 导入flask内置的对象
from flask import request,jsonify,current_app,make_response
# 导入蓝图对象
from . import passport_blue
# 导入自定义的状态码
from info.utils.response_code import RET
# 导入工具captcha
from info.utils.captcha.captcha import captcha
# 导入redis数据库的实例
from info import redis_store,constants

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


    pass











