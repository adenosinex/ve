# from base.mytools import multi_threadpool,get_files,FileType_,\
#     HashM,VideoM,Txt_Ana,\
#     os,Path
 
from datetime import datetime
from itertools import count
from sqlalchemy import and_,or_,case,distinct,or_,func
# from sqlalchemy.orm import or_
from factory import db,who
from flask import current_app as app
import time,re
 
from tools import *

@who.register_model('name', 'path' )
class File(db.Model):
    id=db.Column(db.String,primary_key=True)
    name=db.Column(db.String,nullable=False)
    size=db.Column(db.Integer,nullable=False)
    type=db.Column(db.String,nullable=False)
    path=db.Column(db.String,nullable=False)
    dir=db.Column(db.String,nullable=False)
    ctime=db.Column(db.String,default=datetime.datetime.now)
    tag=db.relationship('Tag', backref='file',uselist=False)  # 反向引用
     # 小说高频词
    kw=db.Column(db.String,nullable=False)
     # 提取数字
    num=db.Column(db.Integer,nullable=False)

    def set_like(self):
        # 标记喜欢 
        if self.tag:
            taginfo=self.tag
        else:
            taginfo=Tag(id=self.id,utime=int(time.time()))

        if taginfo.like:
            taginfo.like=None
            message= {'op':'like删除成功','id':self.id}
        else:
            taginfo.like=True
            message= {'op':'like添加成功','id':self.id}
        db.session.add(taginfo)
        db.session.commit()
        return message

    def set_tag(self,s):
        # 标记
        if self.tag:
            taginfo=self.tag
        else:
            taginfo=Tag(id=self.id)
        taginfo.tag=s
        message= {'op':'tag设置成功','id':self.id}
        db.session.add(taginfo)
        db.session.commit()
        return message

  
    def set_kw(self,s):
        # 添加高频词
        self.kw=s
        message= {'op':'tag设置成功','id':self.id}
        db.session.add(self)
        db.session.commit()
        return message


class Tag(db.Model):
    id=db.Column(db.String,db.ForeignKey(File.id),primary_key=True)
    like=db.Column(db.Boolean)
    tag=db.Column(db.String)
    utime=db.Column(db.String,default=datetime.datetime.now)
   
  
class Dir(db.Model):
    id=db.Column(db.Integer ,primary_key=True)
    path=db.Column(db.String,unique=True)
    dir=db.Column(db.String)
    is_extra=db.Column(db.Boolean)
    level=db.Column(db.Integer)
    rank=db.Column(db.Integer)

class Log(db.Model):
    id=db.Column(db.Integer ,primary_key=True)
    url=db.Column(db.String)
    is_top=db.Column(db.Boolean)
    utime=db.Column(db.DateTime, default=datetime.datetime.now, index=True)
 

def multi_ruledb( sentens, most=False):
    # 空格句子 多条件查询
    base=File.path
    if ':kw' in sentens:
        sentens=sentens.replace(':kw','')
        base=File.kw

    split_sn=sentens.strip().split(' ')
    if len(split_sn)>1:
        rules=[base.like(f'%{i}%') for i in split_sn if i]
        rule=and_(*rules)
        if most:
            rule=or_(*rules)      
    else:
        rule = base.like(f'%{sentens}%')
    return rule

class InitData:
    def __init__(self) -> None:
        db.create_all()
        self.files_path=app.config.get('FILE_PATH')
        self.smallfiles_path=app.config.get('SMALL_FILE_PATH')

    def _small_file(self,file,id,type):
        # 文件缩小化
        p=''
        if type=='video':
            p=self.smallfiles_path+'/{}.gif'.format(id)
            VideoM().shot_gif(file,p,t='20%')
        elif type=='img':
            p=self.smallfiles_path+'/{}.jpg'.format(id)
            VideoM().thumbnail(file,p)

    def _index_file(self,file):
        # 文件索引
        id=HashM().sha1_head(file)
        # 已经存在跳过 路劲不一样更新路径
        old_entry=File.query.filter_by(id=id).first()
        file_type=FileType_().media_type(file)
        # 缩略图
        # self._small_file(file,id,file_type)
        if  old_entry :
            if old_entry.path!=file:
                old_entry.path=file
                db.session.add(old_entry)
            return 
        # 其他类型文件跳过
        if not file_type:
            return
        item=File(id=id,name=Path(file).name,size=os.path.getsize(file),type=file_type,path=file,dir=str(Path(file).parent))
        db.session.add(item)
        db.session.commit()

    def ana_dyname(self):
         # 使用作者发布信息为名
        def func_rec():
            t=Db_Mani(r'X:/库/code/douyin get/data-dy.db').query('select id,desc,ctime from raw')
            data={i[0]:[i[1],i[2]] for i in t}
            files=db.session.query(File).filter_by(dir='X:\库\视频\dy like').all()
            def f(i):
                if not data.get(Path(i.path).stem):
                    return
               
                # i.name,ctime=data.get(Path(i.path).stem)
                # i.ctime=datetime.datetime.fromtimestamp(int(ctime))
                if i.name!=Path(i.path).stem:
                    i.name,ctime=data.get(Path(i.path).stem)
                    i.ctime=datetime.datetime.fromtimestamp(int(ctime))
                pass
                
            multi_threadpool(func=f,args=files)
            
        def func_old():
            t=Db_Mani(r'X:/库/dyvideo.db')
            sql='select videos.id,videos.desc,authors.nickname,videos.ctime  from videos,authors,heart where videos.id=heart.id and videos.aid=authors.uid'
            a='@林南学姐· '
            rdata=t.query(sql)
            data={i[0]:[f'@{i[2]}·{i[1]}',i[3] ]for i in rdata}

            files=db.session.query(File).filter_by(dir=r'X:\库\DyView\view like').all()
            c=count(1)
            def f(i):
                if data.get(Path(i.path).stem):
                    i.name,ctime=data.get(Path(i.path).stem)
                    i.ctime=datetime.fromtimestamp(int(ctime)) 
                    if next(c)%100==0:
                        db.session.commit()
                    return i
            # [f(i) for i in files ]
            multi_threadpool(func=f,args=files)
        func_rec()
        db.session.commit()

    def ana_txt(self):
         # 文本分析数据
        ana_t=Txt_Ana()
        def f(item):
            # 文本关键词分析
            if   item.kw:
                return
            nword=ana_t.topn_file(item.path)
            item.set_kw(nword)
        multi_threadpool(func=f,args=db.session.query(File).filter_by(type='story').all(),desc='小说高频词提取')
    
    def ana_number(self):
        #  提取数字 排序
        def f(item):
            # 文本关键词分析
            if   item.num:
                return
            try:
                item.num=re.findall('\d+',Path(item.path).name)[0]
            except:
                pass
            
        multi_threadpool(func=f,args=db.session.query(File).filter_by(num=None ).all(),desc='提取数字')
        db.session.commit()

    def create_small_file(self ):
        # 生辰缺少的缩略图
        ids={Path(i).stem for i in get_files(self.smallfiles_path)}
        r=db.session.query(File ).filter(or_(File.type=='video',File.type=='img')).filter(File.id.notin_(ids))
        def f(i):
             self._small_file(i.path,i.id,i.type)
        multi_threadpool(func=f,args=r,desc='生成缩略图 gif',pool_size=4 )

    def init_file(self,file_path):
        # 初始化数据
        # 文件数据与缩略图
        if isinstance(file_path,list):
            files=[]
            for i in file_path:
                files+=get_files(i)
        else:
            files=get_files(file_path)
         # 旧文件
        old_files={i[0] for i in  db.session.query(distinct(File.path)).all()}
        # 只添加新文件
        files=set(files).difference(old_files)
        t=db.session.query(File).count()
        # 文件数据
        multi_threadpool(func=self._index_file,args=files,desc='数据初始化-{}'.format(Path(file_path).name))
        mes1='数据库数据：{}'.format(db.session.query(File).count()-t)
        print(mes1)
        return mes1

    def init_dir(self):
        # 目录数据 擦除重新分析
        # db.session.query(Dir).delete(synchronize_session=False)
        # db.session.commit()
        dirs_old={i[0] for i in db.session.query( Dir.path ).all()}
        dirs={i[0] for i in db.session.query(distinct(File.dir)).all()}.difference(dirs_old)
        count_dir=db.session.query(Dir).count() 
        # 添加目录
        def f(dirs,is_extra=False):
            for item in dirs:
                i=Dir(path=item,dir=str(Path(item).parent),level=item.count('\\'),is_extra=is_extra)
                db.session.add(i)
                db.session.commit()
        f(dirs)
        
        mes1='解析目录：{}'.format(db.session.query(Dir).count()-count_dir )
        count_dir=db.session.query(Dir).count()
         # 含有多个子文件夹的文件夹 添加
        dirs_old={i[0] for i in db.session.query( Dir.path ).all()} 
        import_dirs= db.session.query(Dir.dir,func.count(Dir.dir)).group_by(Dir.dir).filter(Dir.is_extra==False).all() 
        dirs={i[0] for i in import_dirs if i[1]>2}.difference(dirs_old)
        f(dirs,is_extra=True)
        mes2='额外重要目录：{}'.format(db.session.query(Dir).count()-count_dir )

        print(mes1,mes2)
        self.dir_rank() 
        return mes2

    def run(self):
        # 初始化默认目录
        self.init_file(self.files_path)
        self.init_dir()
        self.ana_number()
        self.smallfiles_path()

      
         
    def dir_rank(self):
        # dirs=db.session.query(Dir).order_by(Dir.level).filter_by(rank=None ).all()
        dirs=db.session.query(Dir).order_by(Dir.level).all()
        for i in range(len(dirs)):
            l=len(dirs[:i])
            now=dirs[i]
            for j in range( l):
                comp=dirs[l-j-1]
                if comp.path in now.path:
                    now.rank=comp.rank+1 if comp.rank else 1
                    break
            else:
                now.rank=1
            db.session.add(now)
             
        db.session.commit()

    def reindex_dir(self,app):
        # 重索引文件 应对新增文件 修改文件名
        dirs=db.session.query(Dir.path).filter_by(rank=1).all()
        dir=[i[0] for i in dirs if not '图文数据' in i[0]]
        self.scan_dir(dir,app)
        
    def scan_dir(self,p,app):
        with app.app_context():
            if isinstance(p,list):
                for i in p:
                    # 初始化新文件夹
                    self.init_file(i)
                
            else:
                    # 初始化新文件夹
                    self.init_file(p)
            #  生成缩略图
            self.init_dir()
            self.create_small_file()

        