# 导入redis模块
from redis import StrictRedis

class Config:
    DEBUG = None
    # 配置密钥
    SECRET_KEY = 'mMr88P+cvbxFXvcpX9PpiBTWMDLtGNkI7fwKhVv7GWuv9QZyRoyUsw=='

    # 配置数据库的链接
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@localhost/info_python37'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置状态保持session信息的存储
    SESSION_TYPE = 'redis'
    SESSION_REDIS = StrictRedis(host='127.0.0.1', port=6379)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = 86400

# 定义开发环境的配置类
class DevelopmentConfig(Config):
    DEBUG = True

# 定义生产环境的配置类
class ProductionConfig(Config):
    DEBUG = False

# 实现不同环境下的配置类的字典映射
config_dict = {
    'development':DevelopmentConfig,
    'production':ProductionConfig
}
