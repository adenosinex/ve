# from base.mytools import multi_threadpool,get_files,FileType_,\
#     HashM,VideoM,Txt_Ana,\
#     os,Path
 
from datetime import datetime,timedelta
from itertools import count
from sqlalchemy import and_,or_,case,distinct,or_,func,text,desc
# from sqlalchemy.orm import or_
from factory import * 
from flask import current_app as app
import time,re
 
from tools import *

# @who.register_model('name', 'path' )
class File(db.Model):
    id=db.Column(db.String,primary_key=True)
    name=db.Column(db.String,nullable=False)
    size=db.Column(db.Integer,nullable=False)
    type=db.Column(db.String,nullable=False)
    path=db.Column(db.String,nullable=False)
    dir=db.Column(db.String,nullable=False)
    ctime=db.Column(db.String )
    utime=db.Column(db.String,default=datetime.now)
    tag=db.relationship('Tag', backref='file',uselist=False)  # 反向引用
    file2=db.relationship('File2', backref='file',uselist=False)  # 反向引用
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

class File2(db.Model):
    id=db.Column(db.String,db.ForeignKey(File.id),primary_key=True)
    path=db.Column(db.String,nullable=False)
     
class Tag(db.Model):
    id=db.Column(db.String,db.ForeignKey(File.id),primary_key=True)
    like=db.Column(db.Boolean)
    tag=db.Column(db.String)
    utime=db.Column(db.String,default= datetime.now)
   
  
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
    utime=db.Column(db.DateTime, default=datetime.now, index=True)

     


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

class FileProcessor:
    # 文件索引 自定义信息
    def __init__(self, file,hash='' ):
        if hash:
            self.hashid_file=hash
        else:
            self.hashid_file=HashM().sha1_head(file)
        self.file =file
    
    def get_data_File(self):
        # 初始化，修改数据
        file=self.file 
        file_type=FileType_().media_type(file)
        self.fileclass = File(id=self.hashid_file,name=Path(file).name,\
            size=os.path.getsize(file),type=file_type,path=file,dir=str(Path(file).parent)\
            ,ctime=datetime.fromtimestamp(os.path.getmtime(file))\
            ,utime=datetime.now())
        self.process_dyname()
        self.process_appletime()
        return self.fileclass

    def process_appletime(self):
        # 录像指定时间
        file=self.fileclass
        if not r'D:\备份 万一\ds photo\MobileBackup' in file.path:
            return
        try:
            time_str = file.name[4:12]
            if len(time_str)!=8:
                return
            datetime_obj = datetime.strptime(time_str, '%Y%m%d')
        except:
            return
        t=str(datetime_obj)
        if t !=file.ctime:
            file.ctime=datetime_obj
            
       
    def process_dyname(self,force=False):
        file=self.fileclass
        id=Path(file.name).stem
        if   r'D:\抖音' in file.path:
            raw_data=Db_Mani(r'X:/库/dyvideo.db').query_one(f'select id,desc,ctime from videos where id="{id}"')
        elif   r'X:\库\视频\dy like' in file.path:
            raw_data=Db_Mani(r'X:/库/code/douyin get/data-dy.db').query_one(f'select id,desc,ctime from raw where id="{id}"')
        else:
            return
        if raw_data:
            id,desc,ctime=raw_data
            if not ctime:
                ctime=0
            if force or file.name!=desc:
                file.name,file.ctime=desc,datetime.fromtimestamp(int(ctime))
             
                

 

class InitData:
    def __init__(self) -> None:
        db.create_all()
        self.files_path=app.config.get('FILE_PATH')
        self.smallfiles_path=app.config.get('SMALL_FILE_PATH')

    def _index_file(self,file):
        # 添加文件数据
        # 其他类型文件跳过
        file_type=FileType_().media_type(file)
        if not file_type:
            return
        # 文件索引
        file_data=FileProcessor(file)
        # 已经存在跳过 路劲不一样更新路径
        hashid_file=file_data.hashid_file
        file_old=File.query.filter_by(id=hashid_file).first()
        
        def f_movefile(fileobj):
            fileobj.path=file
            fileobj.dir=str(Path(file).parent)
            return fileobj
        # 存在旧文件 更新路径，生产更新或添加第二路径
        if  file_old :
            # 文件路径修改
            if app.config.get('IS_PRO'):
                file2_old=File2.query.filter_by(id=hashid_file).first()
                if not file2_old:
                    file2_old=File2(id=hashid_file,path=file)
                else:
                    file2_old=f_movefile(file2_old)
                db.session.add(file2_old)

            elif file_old.path!=file:
                file_old=f_movefile(file_old)
                db.session.add(file_old)
            db.session.commit()
            return 
         
        item=file_data.get_data_File()
        db.session.add(item)
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
            if i.type=='video':
                p=self.smallfiles_path+'/{}.gif'.format(i.id)
                SmallFile().shot_gif(i.path,p )
            elif i.type=='img':
                p=self.smallfiles_path+'/{}.jpg'.format(i.id)
                SmallFile().thumbnail(i.path,p)
              
        multi_threadpool(func=f,args=r,desc='生成缩略图jpg gif',pool_size=4 )

    def rindex_col(self  ):
        # 设置字段
        files=File.query.filter(File.ctime==None).all()
        def fsetctime(i):
            if os.path.exists(i.path):
                i.ctime=datetime.fromtimestamp(os.path.getmtime(i.path))
                if not i.utime:
                    i.utime=i.ctime
                db.session.add(i)

        files=File.query.all()
        def fchenckpath(i):
            if not os.path.exists(i.path):
                i.path='del '+i.path
                db.session.add(i)
        multi_threadpool(func=fchenckpath,args=files,desc='再次初始化 字段 '  )
        db.session.commit()
     
    def rinit_file(self,file_path ):
        # 再次初始化数据 dy
        # 文件数据与缩略图
        files=get_files(file_path)

        # 只添加新文件
        files=db.session.query(File).filter(File.path.like(f'%{file_path}%')).all()
        cnt_files=db.session.query(File).count()
        # 文件数据
        def f(i):
            a=FileProcessor(i.path,i.id)
            r=a.get_data_File()
            i.ctime=r.ctime
            db.session.add(i)
            db.session.commit()

        multi_threadpool(func=f,args=files,desc='再次初始化-{}'.format(Path(file_path).name) )
        mes1='数据库数据：{}'.format(db.session.query(File).count()-cnt_files)
        print(mes1)
        return mes1
    
    def init_file(self,file_path ):
        # 初始化数据
        # 文件数据与缩略图
        if isinstance(file_path,list):
            files=[]
            for i in file_path:
                files+=get_files(i)
        else:
            files=get_files(file_path)
         # 旧文件
        if app.config.get('IS_PRO'):
            old_files={i[0] for i in  db.session.query(distinct(File2.path)).all()}
        else:
            old_files={i[0] for i in  db.session.query(distinct(File.path)).all()}
        # 只添加新文件
        files=set(files).difference(old_files)
        cnt_files=db.session.query(File).count()
        # 文件数据
        multi_threadpool(func=self._index_file,args=files,desc='数据初始化-{}'.format(Path(file_path).name) )
        mes1='数据库数据：{}'.format(db.session.query(File).count()-cnt_files)
        print(mes1)
        return mes1

    def init_dir(self):
        # 目录数据 擦除重新分析
        # db.session.query(Dir).delete(synchronize_session=False)
        # db.session.commit()
        dirs_old={i[0] for i in db.session.query( Dir.path ).all()}
        dirs={i[0] for i in db.session.query(distinct(File.dir)).all()}.difference(dirs_old)
        count_dir=db.session.query(Dir).count() 
        # 添加直接目录
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
        
    def scan_dir(self,p ):
         
        if isinstance(p,list):
            for i in p:
                # 初始化新文件夹
                self.init_file(i)
            
        else:
                # 初始化新文件夹
                self.init_file(p)
        #  生成缩略图
        self.init_dir()
        
        # self.create_small_file()



class IdPath(dbm.Model):
    # 缩略图位置
    __bind_key__ = 'sqlite'
    __tablename__ = 'mytable'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)