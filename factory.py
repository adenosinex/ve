from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask import Flask,current_app
from flask_whooshee import Whooshee
# from models import *
from config import config
# from flask_cors import CORS

db=SQLAlchemy()
bt=Bootstrap()
who=Whooshee()

def creat_app(config_name='dev'):
    app=Flask(__name__)
     
    app.config.from_object(config[config_name])
    db.init_app(app)
    bt.init_app(app)
    who.init_app(app)
    # cors=CORS( supports_credentials=True)
    # 缩略图路径
    # cors.init_app(app)
    from blueprint_api import api_bp
    api_bp.static_folder=app.config.get('SMALL_FILE_PATH')
    app.register_blueprint(api_bp)

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
         

 
