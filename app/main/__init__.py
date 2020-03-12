from flask import Blueprint

# 实例化蓝本，传入蓝本所在的包以及蓝本的名称
main = Blueprint('main', __name__)

# 避免循环引用，放在最后。'.'表示当前包。
from . import views, errors