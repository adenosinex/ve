# from base.mytools import multi_threadpool,get_files,FileType_,\
#     HashM,VideoM,Txt_Ana,\
#     os,Path

from datetime import datetime, timedelta
from functools import reduce
from itertools import count
from sqlalchemy import and_, or_, case, distinct, or_, func, text, desc, not_
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
    ctime = db.Column(db.String)
    utime = db.Column(db.String, default=datetime.now)
    tag = db.relationship('Tag', backref='file', uselist=False)  # 反向引用
    file2 = db.relationship('File2', backref='file', uselist=False)  # 反向引用
    # 小说高频词
    kw = db.Column(db.String, nullable=False)
    # 提取数字
    num = db.Column(db.Integer, nullable=False)

    def set_like(self):
        # 标记喜欢
        if self.tag:
            taginfo = self.tag
        else:
            taginfo = Tag(id=self.id, utime=int(time.time()))

        if taginfo.like:
            taginfo.like = None
            message = {'op': 'like删除成功', 'id': self.id}
        else:
            taginfo.like = True
            message = {'op': 'like添加成功', 'id': self.id}
        db.session.add(taginfo)
        db.session.commit()
        return message

    def set_tag(self, s):
        # 标记
        if self.tag:
            taginfo = self.tag
        else:
            taginfo = Tag(id=self.id)
        taginfo.tag = s
        message = {'op': 'tag设置成功', 'id': self.id}
        db.session.add(taginfo)
        db.session.commit()
        return message

    def set_kw(self, s):
        # 添加高频词
        self.kw = s
        message = {'op': 'tag设置成功', 'id': self.id}
        db.session.add(self)
        db.session.commit()
        return message


class File2(db.Model):
    id = db.Column(db.String, db.ForeignKey(File.id), primary_key=True)
    path = db.Column(db.String, nullable=False)


class Tag(db.Model):
    id = db.Column(db.String, db.ForeignKey(File.id), primary_key=True)
    like = db.Column(db.Boolean)
    tag = db.Column(db.String)
    utime = db.Column(db.String, default=datetime.now)


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


@lru_cache(maxsize=128)
def db_query_data(datat, pn, per_page):
    data = {i[0]: i[1] for i in datat}
    # 过滤数据
    base = File.query
    # 目录筛选
    dirs = ''
    # 喜欢
    if data.get('like'):
        base = base.filter(File.tag != None)
        base = base.join(Tag).filter(or_(Tag.like,Tag.tag != 'del')).order_by(
            File.type.desc(), Tag.utime.desc())
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
        s = data.get('kw')
        mul = 1024**2
        base=base.outerjoin(Tag)
        if 'size>' in s:
            n = s.replace('size>', '')
            base = base.filter(File.size > int(n)*mul)
        elif 'size<' in s:
            n = s.replace('size<', '')
            base = base.filter(File.size < int(n)*mul)
        elif 'pathid:' in s:
            n = s.replace('pathid:', '')
            r = Dir.query.filter_by(id=int(n)).first()
            base = base.filter(File.path.like(f'%{r.path}%'))
        else:
            base = base.filter(query_mul_word(data.get('kw')))
            

    # 过滤不存在 标记删除
    base = base.filter(~File.path.startswith('del')).filter(
        ~File.path.startswith('del'))
    ids = [i.id for i in Tag.query.filter(Tag.tag == 'del').all()]
    base = base.filter(not_(File.id.in_(ids)))

    if data.get('sort'):
        s = data.get('sort')
        print(s)
        base = base.order_by(text(s))
    else:
        base = base.order_by(File.ctime.desc())
    # 文件集中需求
    if per_page==-1:
        return base.all()
    else:
        pgn = base.paginate(page=pn, per_page=per_page)
        return pgn, dirs_data


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
        if not r'D:\备份 万一\ds photo\MobileBackup' in file.path:
            return
        try:
            time_str = file.name[4:12]
            if len(time_str) != 8:
                return
            datetime_obj = datetime.strptime(time_str, '%Y%m%d')
        except:
            return
        t = str(datetime_obj)
        if t != file.ctime:
            file.ctime = datetime_obj

    def _process_dyname(self, force=False):
        file = self.fileclass
        id = Path(file.name).stem
        if r'D:\抖音' in file.path:
            raw_data = Db_Mani(
                r'X:/库/dyvideo.db').query_one(f'select id,desc,ctime from videos where id="{id}"')
        elif r'X:\库\视频\dy like' in file.path:
            raw_data = Db_Mani(r'X:/库/code/douyin get/data-dy.db').query_one(
                f'select id,desc,ctime from raw where id="{id}"')
        else:
            return
        if raw_data:
            id, desc, ctime = raw_data
            if not ctime:
                ctime = 0
            if force or file.name != desc:
                file.name, file.ctime = desc, datetime.fromtimestamp(
                    int(ctime))


class InitData:
    def __init__(self) -> None:
        db.create_all()
        self.files_path = app.config.get('FILE_PATH')
        self.smallfiles_path = app.config.get('SMALL_FILE_PATH')

    def update_file(self, file_class,file_path):
        # 路径更新
        file_class.path = file_path
        file_class.dir = str(Path(file_path).parent)
        return file_class

    def add_file(self, file_path):
        # 添加文件数据
        # 其他类型文件跳过
        file_type = FileType_().media_type(file_path)
        if not file_type:
            return
        # 文件索引
        file_data = FileProcessor(file_path)
        # 尝试获取数据库文件
        hashid = file_data.hashid_file
        old_file_class = File.query.filter_by(id=hashid).first()
        # 有旧文件 更新路径
        if old_file_class:
            old_file_class = self.update_file(old_file_class,file_path)
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

    def create_small_file(self):
        # 生辰缺少的缩略图
        ids = {Path(i).stem for i in get_files(self.smallfiles_path)}
        r = db.session.query(File).filter(
            or_(File.type == 'video', File.type == 'img')).filter(File.id.notin_(ids))

        def f(i):
            if i.type == 'video':
                p = self.smallfiles_path+'/{}.gif'.format(i.id)
                SmallFile().shot_gif(i.path, p)
            elif i.type == 'img':
                p = self.smallfiles_path+'/{}.jpg'.format(i.id)
                SmallFile().thumbnail(i.path, p)

        multi_threadpool(func=f, args=r, desc='生成缩略图jpg gif', pool_size=4)

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

        def fchenckpath(i):
            if not os.path.exists(i.path):
                i.path = 'del '+i.path
                db.session.add(i)
        multi_threadpool(func=fchenckpath, args=files, desc='再次初始化 字段 ')
        db.session.commit()

    def rinit_file(self, file_path):
        # 再次初始化数据 dy
        # 文件数据与缩略图
        files = get_files(file_path)

        # 只添加新文件
        files = db.session.query(File).filter(
            File.path.like(f'%{file_path}%')).all()
        cnt_files = db.session.query(File).count()
        # 文件数据

        def f(i):
            a = FileProcessor(i.path, i.id)
            r = a.get_data_File()
            i.ctime = r.ctime
            db.session.add(i)
            db.session.commit()

        multi_threadpool(func=f, args=files,
                         desc='再次初始化-{}'.format(Path(file_path).name))
        mes1 = '数据库数据：{}'.format(db.session.query(File).count()-cnt_files)
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

        # self.create_small_file()


 


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
        dirs = [r'X:\库\视频\dy like', r'X:\库\DyView',
                r'D:\备份 万一\ds photo\video',]
        #   r'D:\抖音\mp4\add',r'D:\抖音\mp4\tag']
        data_init=InitData()
        num=data_init.init_files_bydirs(dirs)
        if num>1000:
            data_init.init_dir(force=True)
        else:
            data_init.init_dir()
    
    def run(self):
        today =  datetime.now().strftime("%Y%m%d")
        cache_file='daily.cache'
        if not os.path.exists(cache_file) or today!=open(cache_file,'r',encoding='utf-8').read():
            self.keep_3day_logs()
            self.scan_dir()
            with open('daily.cache','w',encoding='utf-8') as f:
                f.write(today)
        print('日常任务')
