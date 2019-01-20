from flask import session, render_template, current_app, jsonify, request
# 导入蓝图对象
from . import news_blue
# 导入模型类
from info.models import User,Category,News
# 导入自定义的状态码
from info.utils.response_code import RET
# 导入常量文件
from info import constants

@news_blue.route("/")
def index():
    """
    项目首页加载
    一、加载用户信息
    1、使用模板加载项目首页----把static文件夹粘贴到info/目录下
    展示用户信息：检查用户登录状态-----如果用户已登录显示用户信息，否则提供登录注册入口
    1、尝试从redis中获取用户的session信息
    2、如果获取到user_id,根据user_id查询用户信息
    3、把查询结果作为用户数据返回给模板

    二、加载新闻分类
    1、查询新闻分类数据，mysql
    ca = Category.query.all()
    2、判断查询结果是否有数据
    3、如果有数据，遍历查询结果，调用模型类中的to_dict函数
    4、返回新闻分类数据

    三、加载新闻点击排行数据
    1、查询新闻点击排行数据，mysql
    2、根据新闻点击次数添加查询条件,News，order_by,desc,limit(6)
    3、判断查询结果
    4、遍历查询结果，调用模型类中的to_dict函数
    5、返回新闻排行数据


    :return:
    """
    # 从redis中获取user_id
    user_id = session.get('user_id')
    # 根据user_id查询mysql数据库
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 加载新闻分类数据
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询分类数据失败')
    # 判断查询结果
    if not categories:
        return jsonify(errno=RET.NODATA,errmsg='无新闻分类数据')
    # 遍历查询结果，调用模型类中的to_dict函数，获取字典数据
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())

    # 新闻点击排行数据加载
    try:
        news_rank = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询新闻排行数据失败')
    # 判断查询结果
    if not news_rank:
        return jsonify(errno=RET.NODATA,errmsg='无新闻点击排行数据')
    # 遍历查询结果
    news_rank_list = []
    for news in news_rank:
        news_rank_list.append(news.to_dict())

    # 定义字典，给模板传入用户数据
    # if user:
    #     user.to_dict()
    # else:
    #     user = None
    data = {
        'user_info':user.to_dict() if user else None,
        'category_list':category_list,
        'news_rank_list':news_rank_list
    }

    return render_template('news/index.html',data=data)


@news_blue.route("/news_list")
def get_news_list():
    """
    新闻列表数据加载
    获取参数---检查参数---业务处理---返回结果
    1、获取参数
    cid，page，per_page,需要给默认值
    2、检查参数，转换参数的数据类型
    3、根据分类id查询指定分类下的新闻数据，按照新闻的发布时间倒叙排序，并且进行分页
        实现形式一：写多条查询语句
        if cid == 1:如果是最新，查询所有新闻，过滤条件为空
            News.query.filter().order_by(News.create_time.desc()).paginate(page,per_page,False)
        else:
            如果选择了不是'最新'的分类,根据分类id进行查询新闻数据
            News.query.filter(News.category_id==cid).order_by(News.create_time.desc()).paginate(page,per_page,False)
        实现形式二：写一条查询语句
        filters = []
        if cid > 1:如果不是最新，添加分类id
            filters.append(News.category_id==cid)
        News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    4、获取分页后的数据，总数据items、当前页数page、总页数pages
    5、遍历总数据，调用模型类中的to_dict函数，获取新闻的字典数据
    6、返回结果
        总数据items、当前页数page、总页数pages

    :return:
    """
    # 获取参数，get请求，args属性
    cid = request.args.get("cid",'1')
    page = request.args.get('page','1')
    per_page = request.args.get('per_page','10')
    # 检查参数的类型
    try:
        cid,page,per_page = int(cid),int(page),int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='参数类型错误')
    # 定义查询数据的过滤条件
    filters = []
    # 判断分类id不是最新，添加分类id给filters过滤条件
    if cid > 1:
        filters.append(News.category_id == cid)
    # filters里面存储的就是查询条件的对象
    # print(filters)
    # 根据过滤条件，查询新闻列表数据，过滤条件、新闻发布时间排序、分页查询
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='查询新闻列表数据失败')
    # 获取分页后的新闻数据，总新闻数据、总页数、当前页数
    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page
    # 定义容器，遍历分页后的新闻列表数据，调用模型类中to_dict函数
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_dict())
    # 定义字典，返回数据
    data = {
        'news_dict_list':news_dict_list,
        'total_page':total_page,
        'current_page':current_page
    }
    return jsonify(errno=RET.OK,errmsg='OK',data=data)







    pass






@news_blue.route("/favicon.ico")
def favicon():
    """
    网站favicon图标的加载：
    1、浏览器自动加载，默认会访问的url，以获取图标：http://127.0.0.1:5000/favicon.ico
    2、定义路由，route('/favicon.ico'),实现把文件发送给浏览器，找到static/news/favicon.ico文件的路径。

    代码实现后，浏览器无法获取favicon图标的解决办法：
    1、清除浏览器浏览记录
    2、清除浏览器缓存
    3、彻底退出浏览器，重新启动。

    原因：因为浏览器加载favicon不是每次请求都加载。

    """
    return current_app.send_static_file('news/favicon.ico')
