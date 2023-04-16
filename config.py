# sqlite:///:memory: (or, sqlite://)
#  sqlite:///relative/path/to/file.db
#  sqlite:////absolute/path/to/file.db

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    TESTING = True
    SECRET_KEY='fdsds'
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    T_THUMBNAIL='20%'
    SAVE='C:/Users/Zin/Documents/testdata/upload'

class DevelopmentConfig(Config):
     
    FLASK_DEBUG=False
    PER_PAGE=5
    SQLALCHEMY_DATABASE_URI = r'sqlite:///data_explorer_dev.db'
    FILE_PATH=r'C:\Users\Zin\Documents\testdata\mixdata'
    SMALL_FILE_PATH=r'C:\Users\Zin\Documents\testdata\t'

class Development2Config(Config):
    DEBUG = False
    PER_PAGE=100
    SQLALCHEMY_DATABASE_URI = r'sqlite:///data_explorer.db'
    FILE_PATH=[r'D:\真子集',r'E:\picture\a长篇小说',r'E:\picture\t\图文数据\女演员图\julia 图',r'E:\music']
    SMALL_FILE_PATH=r'C:\Users\Zin\Pictures\Saved Pictures\small file'

class ProdConfig(Config):
    DEBUG = False
    PER_PAGE=100
    IS_PRO=True
     
    SMALL_FILE_PATH=r'C:\Users\Zin\Pictures\Saved Pictures\small file'
    SQLALCHEMY_DATABASE_URI = r'sqlite:///data_explorer.db'
   
    

class Filterc(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = r'sqlite:///data-filter.db'
    IMGS_PATH=r'X:\bufferx\OneDrive\图片\people'
    THUMBNAIL_PATH=r'C:\Users\Zin\Pictures\Saved Pictures\thumbnailfilter'
   

class TestingConfig( Config):
    FLASK_DEBUG=True
    SQLALCHEMY_DATABASE_URI = r'sqlite:///test_data.db'

config = {
    'dev': DevelopmentConfig,
    'dev2': Development2Config,
    'pro':  ProdConfig,
    'test': TestingConfig,
    'temp': Filterc,
    'default': DevelopmentConfig
}