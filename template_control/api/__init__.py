import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask
from spider_template.db_actions.mongo_action import TemplateInfo

template = TemplateInfo()


def setup_log():
    # 设置日志的记录等级
    logging.basicConfig(level="INFO")  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 10, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app():
    setup_log()
    app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(app_path, 'templates')
    static_path = os.path.join(app_path, 'templates/static')
    app = Flask(__name__, template_folder=template_path, static_folder=static_path)
    from template_control.api.template_info import template_blu
    app.register_blueprint(template_blu)
    from template_control.api.verify import verify_blu
    app.register_blueprint(verify_blu)
    from template_control.api.index import index_blu
    app.register_blueprint(index_blu)
    return app
