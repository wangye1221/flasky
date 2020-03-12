from flask import render_template
from . import main


# app_errorhandler装饰器作用于全局。
@mian.app_errorhandler(404)
def page_not_found(e) -> 'html':
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_server_error(e) -> 'html':
    return render_template('500.html'), 500