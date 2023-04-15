from datetime import datetime
from itertools import count
from sqlalchemy import and_,or_,case,distinct,or_,func
# from sqlalchemy.orm import or_
from factory import db ,Flask,config
 
# from tools import *
from sqlalchemy.ext.declarative import AbstractConcreteBase
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from base.mytools import *
class File(db.Model):
    __tablename__ = 'file'
    id = db.Column(db.String(40), primary_key=True)
    secname = db.Column(db.String(44), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    ctime = db.Column(db.DateTime, nullable=False)
    video=  relationship('video', backref="file")
    img=  relationship('Image', backref="file")

# 媒体文件继承
class Media(AbstractConcreteBase ):
    __abstract__ = True
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    directory = db.Column(db.String(255), nullable=False)
    media_type = db.Column(db.String(50), nullable=False)
    # file_id=db.Column(db.String(32), db.ForeignKey(File.id))
    @declared_attr
    def file_id(cls):
        return db.Column(db.String(32), db.ForeignKey(File.id))

class Video(Media):
    __tablename__ = 'video'
    length = db.Column(db.Integer, nullable=False)
    resolution = db.Column(db.String(10), nullable=False)
    frame_rate = db.Column(db.Float, nullable=False)
    # file_id=db.Column(db.String(32), db.ForeignKey(File.id))

class Image(Media):
    __tablename__ = 'image'
    height = db.Column(db.Integer, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    # file_id=db.Column(db.String(32), db.ForeignKey(File.id))

class FileType_:
    def media_type(self,i):
        # 返回文件类型 后缀
        if self.is_video(i):
            return 'video'
        if self.is_image(i):
            return 'img'
        if self.is_audio(i):
            return 'music'
        if self.is_text(i):
            return 'story'

    def suffix(self,p, suffixs):
        # 文件后缀是否在集合中

        # 后缀.MP4 去除 . 比较
        suf=Path(p).suffix[1:]
        if suf.lower() in suffixs:
            return True
        return False


    def is_subtitle(self,p):
        # 字幕
        suffixs = {'srt','ass'}
        return self.suffix(p, suffixs)

    def is_video(self,p):
        
        suffixs = {'mp4', 'ts', 'wmv', 'mkv','avi','mov','.m4v', '.m4a','rmvb','mts','ts','m2ts'}
        return self.suffix(p, suffixs)

    def is_image(self,p):
        suffixs = {'jpg', 'png', 'jpeg'}
        return self.suffix(p, suffixs)
       
    def is_audio(self,p):
        suffixs = {'mp3', 'flac' }
        return self.suffix(p, suffixs)

    def is_text(self,p):
        suffixs = {'txt'}
        return self.suffix(p, suffixs)
  
def file_hash(file):
    h = hashlib.sha1()
    h.update(open(file,'rb').read(128))
    r=h.hexdigest().upper()
    return r
# 添加新文件
def add_file( file):
    if Video.query.filter_by(id=id).first() or Image.query.filter_by(id=id).first():
        return
    id=file_hash(file)
    # 已经存在跳过 路劲不一样更新路径
    if not File.query.filter_by(id=id).first():
        if FileType_().is_video(file):
            name=f'{id}.gif'
        if FileType_().is_video(file):
            name=f'{id}.gif'
        item=File(id=id,secname=name,size=size,ctime=ctime)
    file_type=FileType_().media_type(file)
    
    if  old_file :
        if old_file.path!=file:
            old_file.path=file
            db.session.add(old_file)
        return 
    # 其他类型文件跳过
    if not file_type:
        return
    item=File(id=id,name=Path(file).name,size=os.path.getsize(file),type=file_type,path=file,dir=str(Path(file).parent))
    db.session.add(item)
    db.session.commit()

 
if __name__=='__main__':
    app=Flask(__name__)
     
    app.config.from_object(config['dev'])
    db.init_app(app)
    with app.app_context():
        db.drop_all()
        db.create_all( )