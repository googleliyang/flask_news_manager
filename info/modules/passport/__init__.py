from flask import Blueprint


passport_blue = Blueprint('passport_blue',__name__)


# 需要把使用蓝图对象的文件，再次导入到创建蓝图对象的下面
from . import views


