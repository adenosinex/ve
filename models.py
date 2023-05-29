# from base.mytools import multi_threadpool,get_files,FileType_,\
#     HashM,VideoM,Txt_Ana,\
#     os,Path

from datetime import datetime, timedelta
from functools import reduce
from itertools import count
from sqlalchemy import and_, or_, case, distinct, or_, func, text, desc, not_
from sqlalchemy.orm import aliased
# from sqlalchemy.orm import or_
from factory import *
from flask import current_app as app
import time
import re

from tools import *

# @who.register_model('name', 'path' )


class File(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String, nullable=False)
    path = db.Column(db.String, nullable=False)
    dir = db.Column(db.String, nullable=False)
    ctime = db.Column(db.DateTime)
    utime = db.Column(db.DateTime, default=datetime.now)
    tag = db.relationship('Tag', backref='file', uselist=False)  # 反向引用
    shot = db.relationship('Shot', backref='file' )  # 反向引用
    video = db.relationship('Video', backref='file', uselist=False )  # 反向引用
    
    # 小说高频词
    kw = db.Column(db.String, nullable=False)
    # 提取数字
    num = db.Column(db.Integer, nullable=False)

    def set_like(self):
        # 标记喜欢
        if self.tag:
            tag_obj = self.tag
        else:
            tag_obj = Tag(id=self.id, utime=int(time.time()))
        is_add_like=True
        if tag_obj.like:
            tag_obj.like = None
            is_add_like=False
        else:
            tag_obj.like = True
             
        db.session.add(tag_obj)
        db.session.commit()
        tag_obj.is_empty_del()
        return is_add_like

    def set_tag(self, tagtext):
        # 标记
        if self.tag:
            taginfo = self.tag
        else:
            taginfo = Tag(id=self.id)

        is_set=True
        # 新建 删除
        if not taginfo.tag or not tagtext in taginfo.tag:
            s=taginfo.tag if taginfo.tag else ''
            taginfo.tag  = f'{s},{tagtext}'
        else:
            taginfo.tag=taginfo.tag.replace(tagtext,'')
            is_set=False

         # 重构tag 规格化分开
        if taginfo.tag:
            s=','.join(re.findall('\w+',taginfo.tag))
            taginfo.tag=s.strip(',')
           
            
        
        db.session.add(taginfo)
        db.session.commit()
        taginfo.is_empty_del()
        return is_set

    def set_kw(self, s):
        # 添加高频词
        self.kw = s
        message = {'op': 'tag设置成功', 'id': self.id}
        db.session.add(self)
        db.session.commit()
        return message


class Video(db.Model):
    id = db.Column(db.String,db.ForeignKey(File.id),  primary_key=True)
    duration = db.Column(db.Integer)
    resolution = db.Column(db.String(20))
    mime = db.Column(db.String(20))
    audio_mime = db.Column(db.String(20))
    frame_rate = db.Column(db.Float)
    bit_rate = db.Column(db.Integer)
    sample_rate=db.Column(db.Integer)
   
    @staticmethod
    def add_video(id):
        # 添加文件视频信息
        p=File.query.get(id)
        if p.type=='video' and os.path.exists(p.path):
            if Video.query.get(id):
                return
            info=VideoM.get_info(p.path)
            if not info:
                return
            t=Video(id=id,**info)
            db.session.add(t)

    @staticmethod
    def scan_data():
        min_size=current_app.config.get('VIDEODATA_MINSIZE',500) 
        videos=File.query.filter(File.type=='video',File.size>min_size*1024**2).filter(~File.id.in_(db.session.query(Video.id))).all()
        # r=orm_dict(videos[0])
        with db.session.no_autoflush:
            multi_threadpool(func=Video.add_video,args=[i.id for i in videos],desc='扫描大视频数据')
        db.session.commit()

def orm_dict(obj):
    # 类转为字典 输出
    r=dict(obj.__dict__)
    # 黑名单
    for k in ['_sa_instance_state','_sa_adapter','hashname','id']:
        if r.get(k):
            del r[k]
    # 空与列表
    for k in list(r.keys() ):
        if not r[k]:
            del r[k]
        elif isinstance(r[k],list):
            del r[k]
    # r=dict(r)
    return r

class Shot(db.Model):
    id = db.Column(db.String,  primary_key=True)
    pid = db.Column(db.String ,db.ForeignKey(File.id) )
    stime=db.Column(db.String, nullable=False)
    ctime=db.Column(db.DateTime, nullable=datetime.now)
    is_auto=db.Column(db.Boolean, default=False)

    # 添加一条截图
    @staticmethod
    def add(path,pid,stime):
        id=HashM().sha1_head(path)
        t=Shot(id=id, pid=pid,stime=stime,ctime=datetime.now())
        db.session.add(t)
        db.session.commit()

    @staticmethod
    def scan(p=r'X:\库\索引\videoshot_preview' ):
        ids={i.id for i in Shot.query.all()}
        @ignore_errors
        def f(path):
            id=HashM().sha1_head(path)
            if id in ids:
                return
            ids.add(id)
            pid,stime=Path(path).stem.split('-')
            t=Shot(id=id, pid=pid,stime=stime,ctime=datetime.now(),is_auto=True)
            db.session.add(t)
            db.session.commit()
        multi_threadpool(func=f,args=get_files(p),desc='添加预览图信息')
    
    
    
class Tag(db.Model):
    id = db.Column(db.String, db.ForeignKey(File.id), primary_key=True)
    like = db.Column(db.Boolean)
    tag = db.Column(db.String)
    utime = db.Column(db.String, default=datetime.now)
    
    @staticmethod
    def del_empty():
        # 删除空标记
        empty_tag=Tag.query.filter(Tag.like==None,Tag.tag==None).all()
        [db.session.delete(i) for i in empty_tag]
        db.session.commit()
        print('删除空tag',len(empty_tag))

    def is_empty_del(self):
        if not self.like and not self.tag:
            db.session.delete(self)
            db.session.commit()

class Dir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String, unique=True)
    dir = db.Column(db.String)
    is_extra = db.Column(db.Boolean)
    level = db.Column(db.Integer)
    rank = db.Column(db.Integer)


class VisitedPages(db.Model):
    __tablename__ = 'visited_pages'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String)
    is_top = db.Column(db.Boolean)
    utime = db.Column(db.DateTime, default=datetime.now, index=True)
    @staticmethod
    def log_url(url):
        # 记录url
        if not url in {'/', '/?','/keep' }:
            # '/?pn=2'
            last_url =request.url
            db.session.add(VisitedPages(url=last_url ))
            db.session.commit()
            print('VisitedPages: '+last_url)

def query_col_like(sentens):
    return or_(File.name.like(f'%{sentens}%'), File.path.like(f'%{sentens}%'), File.kw.like(f'%{sentens}%'),\
               Tag.tag.like(f'%{sentens}%'))

def query_mul_word(sentens, most=False):
    # 空格句子 多条件查询
    most = False
    if 'or' in sentens:
        sentens = sentens.replace('or', '')
        most = True
    split_sn = sentens.strip().split(' ')
    if len(split_sn) > 1:
        rules = [query_col_like(i) for i in split_sn if i]
        rule = and_(*rules)
        if most:
            rule = or_(*rules)
    else:
        rule = query_col_like(sentens)
    return rule


def db_query_kw(kw,base):
    # 搜索技巧 实现
    mul = 1024**2
    base=base.outerjoin(Tag)
    # 获取参数值
    def get_value(pattern,s):
        t=re.findall(pattern,s)
        if t:
            return t[0]
        
    for s in kw.split(' '):
        # 大小
        if 'size' in s:
            num=get_value('size[<>](\d+)',s)
            if num and '>' in s:
                base = base.filter(File.size > int(num )*mul)
            elif num and '<' in s:
                base = base.filter(File.size < int(num )*mul)
        # 路径id
        elif 'pathid' in s:
            part_text=get_value('pathid:(\d+)',s)
            if  part_text :
                r = Dir.query.filter_by(id=int(part_text )).first()
                base = base.filter(File.path.like(f'%{r.path}%'))
        # 分辨率
        elif 'rat' in s:
            part_text=get_value('rat:(\w+)',s)
            if  part_text :
                part_text=part_text.lower()
                rat_tonum={'4k':'2160','2k':'1440','1k':'1080' }
                rat_num=rat_tonum.get(part_text)
                if not rat_num and part_text.endswith('p'):
                    rat_num=part_text[:-1]
                if rat_num:
                    base = base.filter(Video.resolution.like(f'%{rat_num}'))
        # 编码方式  
        elif 'mime' in s:
            part_text=get_value('mime:(\w+)',s)
            if  part_text :
                if 'h264' in part_text:
                    base = base.filter(Video.mime.like(f'%264%'))
                elif 'h265' in part_text:
                    base = base.filter(Video.mime.like(f'%265%'))
                elif 'other' in part_text:
                    base = base.filter( not_(Video.mime.like(f'%264%')),not_(Video.mime.like(f'%265%'))  )
                
    return base

@lru_cache(maxsize=128)
def db_query_data(datat, pn, per_page):
    # 数据筛选
    data = {i[0]: i[1] for i in datat}
     # 过滤不存在 标记删除,路径不存在
    base = File.query.filter(~File.path.startswith('del'))
    ids = [i.id for i in Tag.query.filter(Tag.tag == 'del').all()]
    base = base.filter(not_(File.id.in_(ids)))
    # 连接表
    base=base.outerjoin(Video)
    # 目录筛选
    dirs = ''
    
    # 喜欢
    if data.get('like'):
        base = base.filter(File.tag != None)
        base = base.join(Tag).filter(or_(Tag.like,Tag.tag != 'del')) 
        
    # 路径模式
    dirs_data = []
    if data.get('dir_num'):
        dir_num = int(data.get('dir_num'))
        if dir_num == 0 or dir_num == -1:
            item = Dir.query.order_by(Dir.level).first()
        else:
            item = Dir.query.filter_by(id=dir_num).first()
        # 目录筛选 文件夹列表第一个为父文件夹
        if item:
            request_path = item.path
            # 根文件夹
            if dir_num == -1:
                print(item.level)
                dirs = Dir.query.order_by(Dir.path).filter_by(rank=1).all()
            # 子文件夹
            else:
                dirs = Dir.query.filter_by(dir=request_path).all()
            # 寻找父文件夹
            pdirs = Dir.query.filter_by(path=item.dir).first()
            # 顶层文件夹 设为/
            if not pdirs:
                pdirs = Dir(id=-1, path='/')

            def f(i):
                # 只保留爷目录名 方便查看
                t = Path(i.path).parent.parent
                i.vpath = i.path if dir_num == - \
                    1 else i.path.replace(str(t), '')
                return i
            dirs_data = {
                'parent': f(pdirs),
                'current': f(item),
                'dirs': [f(i) for i in dirs]
            }
            base = base.filter(File.dir == request_path)

    # 类型字筛选
    type = data.get('type')
    if type and type != 'all':
        base = base.filter(File.type == type)
    # 关键词筛选
    if data.get('kw'):
        querys = data.get('kw')
        base=db_query_kw(querys,base)
        # 去除条件
        kw=re.sub('\w+:\w+','',querys)
        kw=re.sub('\w+[><]\w+','',kw)
        if kw:
            base = base.filter(query_mul_word(kw.strip()))
            
    # 排序
    if data.get('sort'):
        querys = data.get('sort')
        print(querys)
        if data.get('like') and querys=='file.utime desc'   :
            base = base.order_by(Tag.utime.desc())
        else:
            base = base.order_by(text(querys))
    else:
        base = base.order_by(File.ctime.desc())
    

    # 文件集中需求
    kw=data.get('kw')
    # for i in  base.order_by(None).order_by(func.random()).limit(5).all():
    #     print(i.name)
    if per_page==-1:
        # 限制数目
        if kw:
            if 'sort:random' in kw:
                base=base.order_by(None).order_by(func.random())
            limit = re.findall('num<(\d+)',kw)
            if limit:
                return  base.limit( int(limit[0]) ).all()
        return base.all()
    else:
        pgn = base.paginate(page=pn, per_page=per_page)
        return pgn, dirs_data

def get_video_shotset(id,time_start,dst_dir):
    # 获取截图参数
    video_item=File.query.get(id)
    video_path=Path(video_item.path)
    time=int(float(time_start))
    img_path=Path(dst_dir).joinpath(f"{video_path.stem}-{time }.jpg")
    return video_path,str(img_path),time

 

class FileProcessor:
    # 文件索引 自定义信息
    def __init__(self, file, hash=''):
        if hash:
            self.hashid_file = hash
        else:
            self.hashid_file = HashM().sha1_head(file)
        self.file = file

    def get_data_File(self):
        # 初始化，修改数据
        file = self.file
        file_type = FileType_().media_type(file)
        self.fileclass = File(id=self.hashid_file, name=Path(file).name,
                              size=os.path.getsize(file), type=file_type, path=file, dir=str(Path(file).parent), ctime=datetime.fromtimestamp(os.path.getmtime(file)), utime=datetime.now())
        self._process_dyname()
        self._process_appletime()
        return self.fileclass

    def _process_appletime(self):
        # 录像指定时间
        file = self.fileclass
        if not r'D:\备份 万一\ds photo' in file.path:
            return
        try:
            # 'IMG_20221003_181419.MOV'
            time_str = file.name[4:19]
            if len(time_str) != 15:
                return
            datetime_obj = datetime.strptime(time_str, '%Y%m%d_%H%M%S')
        except:
            return
        t = str(datetime_obj)
        if t != file.ctime:
            file.ctime = datetime_obj

    def _process_dyname(self, force=False):
        file = self.fileclass
        id = Path(file.name).stem
        if r'55473676897' in file.path:
            pass
        if r'D:\抖音' in file.path:
            raw_data = Db_Mani(
                r'X:/库/dyvideo.db').query_one(f'select id,desc,ctime from videos where id="{id}"')
        elif r'X:\库\视频\dy like' in file.path:
            raw_data = Db_Mani(r'X:/库/code/douyin get/data-dy.db').query_one(f'select id,desc,ctime from raw where id="{id}"')
        else:
            return
        
        if raw_data:
            id, desc, ctime = raw_data
            if not ctime:
                ctime = 0
            ctime=datetime.fromtimestamp( int(ctime))
            if not file.ctime==ctime:
                file.ctime=ctime

            if force or file.name != desc:
                file.name = desc

class InitData:
    def __init__(self) -> None:
        db.create_all()
        self.files_path = app.config.get('FILE_PATH')
        self.smallfiles_path = app.config.get('SMALL_FILE_PATH')
        self.now_hash_id=set()

    def _update_file(self, file_class,file_path):
        # 类对象 路径更新
        file_class.path = file_path
        file_class.dir = str(Path(file_path).parent)
        return file_class

    def add_file(self, file_path):
        # 添加文件数据
        # 其他类型文件跳过
        file_path=str(file_path)
        file_type = FileType_().media_type(file_path)
        if not file_type:
            return
        # 文件索引
        file_data = FileProcessor(file_path)
        # 尝试获取数据库文件
        hashid = file_data.hashid_file
        if hashid in self.now_hash_id:
            return
        self.now_hash_id.add(hashid)
        old_file_class = File.query.filter_by(id=hashid).first()
        # 有旧文件 更新路径
        if old_file_class:
            old_file_class = self._update_file(old_file_class,file_path)
            db.session.add(old_file_class)
        else:
            item = file_data.get_data_File()
            db.session.add(item)
        return True

    def ana_txt(self):
        # 文本分析数据
        ana_t = Txt_Ana()

        def f(item):
            # 文本关键词分析
            if item.kw:
                return
            nword = ana_t.topn_file(item.path)
            item.set_kw(nword)
        multi_threadpool(func=f, args=db.session.query(
            File).filter_by(type='story').all(), desc='小说高频词提取')

    def ana_number(self):
        #  提取数字 排序
        def f(item):
            # 文本关键词分析
            if item.num:
                return
            try:
                item.num = re.findall('\d+', Path(item.path).name)[0]
            except:
                pass

        multi_threadpool(func=f, args=db.session.query(
            File).filter_by(num=None).all(), desc='提取数字')
        db.session.commit()

    def _check_file_del(self,i):
            if not os.path.exists(i.path):
                i.path = 'del '+i.path
                db.session.add(i)
                return True

    def scan_dir_isdel(self,d):
        files = File.query.filter(File.path.like(f"%{d}%")).all()
        r=multi_threadpool(func=self._check_file_del, args=files, desc=f'检查文件删除-{Path(d).name}')
        db.session.commit()
        r=[i for i in r if i]
        return len(r)

    def rindex_col(self):
        # 设置字段
        files = File.query.filter(File.ctime == None).all()
        def fsetctime(i):
            if os.path.exists(i.path):
                i.ctime = datetime.fromtimestamp(os.path.getmtime(i.path))
                if not i.utime:
                    i.utime = i.ctime
                db.session.add(i)

        files = File.query.all()
        multi_threadpool(func=self._check_file_del, args=files, desc='再次初始化 字段 ')
        db.session.commit()

    def rinit_file(self, file_path):
        # 再次初始化数据时间 dy apple
        # 文件数据与缩略图
        # files_path = get_files(file_path)

        # 只添加新文件
        files = db.session.query(File).filter(File.path.like(f'%{file_path}%')).all()
       
        # 文件数据
        self.cnt=0
        def f(i):
            a = FileProcessor(i.path.replace('del','').strip(), i.id)
            try:
                r = a.get_data_File()
            except:
                return
            if not i.ctime==r.ctime:
                i.ctime = r.ctime
                db.session.add(i)
                self.cnt+=1

        multi_threadpool(func=f, args=files,
                         desc='再次初始化-{}'.format(Path(file_path).name))
        db.session.commit()
        mes1 = '更新数据：{}({})'.format(self.cnt,len(files))
        print(mes1)
        return mes1

    def init_files_bydirs(self, file_dirs):
        # 初始化目录数据 返回修改行数
        # 文件数据与缩略图
        if isinstance(file_dirs, list):
            files = []
            for i in file_dirs:
                files += get_files(i)
            file_dirsv=file_dirs[0]+'-mul'
        else:
            files = get_files(file_dirs)
            file_dirsv=file_dirs 
         # 旧文件
        old_files = {i[0] for i in db.session.query(distinct(File.path)).all()}
        # 只添加新文件
        files = set(files).difference(old_files)
        cnt_files = db.session.query(File).count()
        # 文件数据
        with db.session.no_autoflush:
            r = multi_threadpool(func=self.add_file, args=files,
                                desc='数据初始化-{}'.format(Path(file_dirsv).name))
        db.session.commit()
        mes1 = '文件添加量：{}'.format(db.session.query(File).count()-cnt_files)
        print(mes1)
        return len([i for i in r if i])

    def init_dir(self, force=False):
        # 目录数据 擦除重新分析
        if force:
            db.session.query(Dir).delete(synchronize_session=False)
            db.session.commit()
        # 获取新增目录
        dirs = {i[0] for i in db.session.query(distinct(File.dir)).all()}.difference( 
            {i[0] for i in db.session.query(Dir.path).all()})
        if not dirs:
            return 'not new dirs'
        count_dir = db.session.query(Dir).count()
        # 添加直接目录
        def f(dirs, is_extra=False):
            for item in dirs:
                i = Dir(path=item, dir=str(Path(item).parent),
                        level=item.count('\\'), is_extra=is_extra)
                db.session.add(i)
                
        f(dirs)
        mes1 = '解析目录：{}'.format(db.session.query(Dir).count()-count_dir)
        count_dir = db.session.query(Dir).count()
        # 含有多个子文件夹的文件夹 添加
        import_dirs = db.session.query(Dir.dir, func.count(Dir.dir)).group_by(
            Dir.dir).filter(Dir.is_extra == False).all()
        dirs = {i[0] for i in import_dirs if i[1] >= 2}.difference({i[0] for i in db.session.query(Dir.path).all()})
        f(dirs, is_extra=True)
        db.session.commit()
        mes2 = '额外重要目录：{}'.format(db.session.query(Dir).count()-count_dir)

        print(mes1, mes2)
        self.dirs_rank()
        return mes2

    def run(self):
        # 初始化默认目录
        self.init_files_bydirs(self.files_path)
        self.init_dir()
        self.ana_number()
        self.smallfiles_path()

    def dirs_rank(self):
        # 目录相对排位 1 2 3
        # 按目录层级排序 从头开始 第一个非子目录设为1 后续目录倒退看，是否是前面目录的子目录，是则设为对应rank+1，否（遍历完也不是）为1 前面的已全部排位
        dirs = db.session.query(Dir).order_by(Dir.level).all()
        for now_dir_index in range(len(dirs)):
            now = dirs[now_dir_index]
            for comp_dir_index in range(now_dir_index):
                comp = dirs[now_dir_index-comp_dir_index-1]
                if comp.path in now.path:
                    now.rank = comp.rank+1  
                    break
            else:
                now.rank = 1
            db.session.add(now)
        db.session.commit()

    def reindex_dir(self, app):
        # 重索引文件 应对新增文件 修改文件名
        dirs = db.session.query(Dir.path).filter_by(rank=1).all()
        dir = [i[0] for i in dirs if not '图文数据' in i[0]]
        self.scan_dir(dir, app)

    def scan_dir(self, p):
        if isinstance(p, list):
            r=0
            for i in p:
                # 初始化新文件夹
                r+=self.init_files_bydirs(i)
        else:
            # 初始化新文件夹
            r = self.init_files_bydirs(p)
        #  生成缩略图
        self.init_dir(force=True if r > 10**3 else False)
 

class DailyTask:
    def keep_3day_logs(self):
        # 只保留三天的历史记录
        today = datetime.now()  # 获取当前日期和时间
        delta = timedelta(days=3)  # 创建一个 timedelta 对象表示过去的三天
        three_days_ago = today - delta    # 计算出三天前的日期和时间
        r = db.session.query(VisitedPages).filter(
            VisitedPages.utime < three_days_ago, VisitedPages.is_top == None).all()
        if r:
            [db.session.delete(i) for i in r]
            db.session.commit()
            print('清除3天前访问记录：',len(r))

    def scan_dir(self):
        dirs = [r'X:\库\视频\dy like', 
                # r'X:\库\DyView',
                r'D:\备份 万一\ds photo\video',]
        #   r'D:\抖音\mp4\add',r'D:\抖音\mp4\tag']
        data_init=InitData()
        num=data_init.init_files_bydirs(dirs)
        if num>1000:
            data_init.init_dir(force=True)
        else:
            data_init.init_dir()

    def _copy(self,src,dst):
        # 复制文件 保留元数据，优先硬链接
        if os.path.exists(dst):
            return
        dir_make(Path(dst).parent)
        try:
            os.link(src,dst)
        except:
            shutil.copy2(src,dst)

    def back_code(self,today):
        print('代码备份 flask explorer ',today)
        p=rf'E:\备份\flask explorer\{today}' 
        src=r'X:\库\code\flask explorer'
        def f(i):
            self._copy(i,rel_abs(i,src,p))
        ren=[ f(i) for i  in get_files(src)] 
       
    def run(self):
        today =  datetime.now().strftime("%Y%m%d")
        cache_file='daily.cache'
        print('日常任务')
        if not os.path.exists(cache_file) or today!=open(cache_file,'r',encoding='utf-8').read():
            print('清除log 添加文件')
            self.keep_3day_logs()
            self.scan_dir()
            self.back_code(today)
            create_small_file()
            with open('daily.cache','w',encoding='utf-8') as f:
                f.write(today)
            
        else:
            print(today)
