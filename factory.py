from flask import Blueprint, current_app, Response,\
    session, request, redirect, flash, url_for, jsonify, current_app, send_from_directory
from flask import render_template, request, Response, abort, url_for, session, redirect, flash, current_app

from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, current_app
from flask_migrate import Migrate
# from flask_whooshee import Whooshee
# from models import *
from config import config
# from flask_cors import CORS

db = SQLAlchemy()
bt = Bootstrap()
dbm = SQLAlchemy()
migrate = Migrate(  db)
def creat_app(config_name='dev'):
    app = Flask(__name__)
    # app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///data_explorer.db'
    app.config.from_object(config[config_name])
    db.init_app(app)
    migrate.init_app(app)
    bt.init_app(app)
    # who.init_app(app)
    app.config['SQLALCHEMY_BINDS'] = {
        'sqlite': 'sqlite:///:memory:'
    }

    # 初始化 SQLAlchemy，并指定 bind 参数连接 SQLite3 数据库
    dbm.init_app(app)
    with app.app_context():
        dbm.create_all(bind='sqlite')
    # 注册蓝本
    from blueprint_api import api_bp
    api_bp.static_folder = app.config.get('SMALL_FILE_PATH')
    app.register_blueprint(api_bp)
    from blueprint_los import bp
    app.register_blueprint(bp)
    from blueprint_new_layout import bp
    app.register_blueprint(bp)

    register_shell_context(app)
    register_commands(app)
    return app


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db)


def register_commands(app):
    @app.cli.command()
    def new():
        db.create_all()
