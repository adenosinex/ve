from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from itertools import count
import os,re,subprocess,hashlib
import pickle
from datetime import datetime, timedelta
import shutil  
import sqlite3
from urllib.parse import urlparse,parse_qs,unquote
from pathlib import Path
import time,os
from progress.bar import Bar
from moviepy  import editor
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip
 
# from base.mytools import *
def cal(f):
    # 函数运行计时
    from functools import wraps

    @wraps(f)
    def func(*a, **b):
        s = time.time()
        ret = f(*a, **b)
        print('{} 耗时:{}'.format(f.__name__, time.time()-s))
        return ret
    return func

 

class Txt_Ana:
    # 文本分析
    def __init__(self) -> None:
        import jieba.posseg as psg
        import jieba
        self.psg=psg
        self.jieba=jieba
        txt_stop=r"X:\bufferx\OneDrive\文档\数据库\文本信息\百度停用词表.txt"
        # txt_file=r"C:\Users\Zin\OneDrive\mycode\data\news html.txt"
        #载入停用词 文本数据
        self.stopwords = [line.strip() for line in FileContent().read_text_line(txt_stop)]
        # 手动繁体
        # f=r'C:\Users\xin\OneDrive\文档\文本信息\完全繁体字.txt'
        # words=open(f,encoding='utf-8').read()
        # self.fan_set={i for i in words if i}
    def good_sentence(self,txt_file):
        # 组合句子
        return ' '.join(self.good_words(txt_file))
    
    def good_words(self,txt_file):
        # 返回文本文件词列表 去停用词
       
        all_content=FileContent().read_text_attemp(txt_file)
        #词频统计 {'a':1,''b':3} 过滤停用词
        segments = dict()
        words_raw = self.jieba.cut(all_content)
        words=list()
        for word in words_raw:
            if word not in self.stopwords:
                segments[word] = segments.get(word, 0) + 1
                words.append(word)

        #按照词频排序
        # sort_segments = sorted(segments.items(), key=lambda item:item[1], reverse=True)
        # words_on_list = []
        # for word, count in sort_segments[:99]:
        #     words_on_list.append(word)
            
        return words
    
    def chapter(path):
        # 小说重新整理章节
        path = str(path)
        file = Path(path)
        r_path = file.with_stem('fix'+file.stem)
        if r_path.exists():
            return r_path
        elif 'fix' in path:
            return

        file_text = open(file, encoding='utf-8').read()
        file_text = file_text.replace('土', '十')
        chapter_name = re.findall('第.{1,20}章.{2,10}', file_text)
        if len(chapter_name) < 10:
            renames(file, file.parent.joinpath('bad', file.name))
            return
        chapter_index = [(file_text.index(i), len(i))for i in chapter_name]
        chapter_content = []
        for i in range(len(chapter_name)-1):
            a, b = chapter_index[i][0] + \
                chapter_index[i][1], chapter_index[i+1][0]
            chapter_content.append(file_text[a:b])
        a, b = chapter_index[-1][0]+chapter_index[-1][1], -1
        chapter_content.append(file_text[a:b])
        out_file_text = ''
        for i in range(len(chapter_name)):
            s = '{}\n {}\n'.format(chapter_name[i], chapter_content[i])
            out_file_text += s

        open(r_path, 'w', encoding='utf-8').write(out_file_text)
        return r_path


    def tclass(self,text):
        # 特殊文本类型识别
        # html 识别
        a=re.findall(r'<[^>]+>',text)
        if a:
            return 'html'
        # 繁体识别 3个不同繁体字认为是繁体文章
        cnt=3
        fan=self.fan_set.copy()
        for i in fan:
            if i in text:
                cnt-=1
                fan.remove(i)
                if cnt==0:
                    return 'fan'

   
    def topn_file(self,p,  getn=4,size=2000):
        # 分析文本 去除数字字母
        text=FileContent().read_text_attemp(p)[:size]
        text=re.sub('[\da-zA-Z-\.]+','',text )
        return self.topn(text,getn=getn)

    def topn(self,text,len_min=2,getn=4,stopword=True):
        # 文本下频率最高的词 无意义词过滤方法 词性 停用词列表
        # 停用词过滤
        if stopword:
            allwords = [ x   for x in self.jieba.cut(text) if len(x) >= len_min and x not in self.stopwords]
        else:
            psg=self.psg
            # 分词列表 附词性分析
            result=psg.cut(text)
            #  词性过滤
            stop_attr = ['a','ad','b','c','d','f','df','m','mq','p','r','rr','s','t','u','v','z']
            allwords = [ x.word   for x in result if len(x.word) >= len_min and x.flag not in stop_attr]
        # 频率最高的词
        r =Counter(allwords).most_common(getn)
        top_words=[i[0] for i in r]
        s=','.join(top_words)
        return s

    def keyin(self ):
        # 查找含关键字的文本
        # p=inputm(desc='path:')
        # key=input('key:')
        p=r'X:\库\db\磁力分类\电影'
        key='色戒'
        files=AllFile().type(p,'text')
        def f(i):
            t=FileContent().read_text_attemp(i)
            if key in t:
                return [i]
            return False
        r=multi_thread(func=f,arg_list=files,desc='find key in')
        r=[i for i in r if i]
        if r[0]:
            print(r[0])


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

    def content(self,p,tag):
        try:
            s = filetype.guess(p).mime
            if tag in s:
                return True
            return 
        except:
            return ''

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
  
def dir_make(arg):
    if not os.path.exists(arg):
        os.makedirs(arg)
def _get_file(p,index):
    # 获取所有文件/夹
    ret=[] 
    if not p:
        return ret
    for f in os.walk(p):
        for i in f[index]:
            file= '{}\\{}'.format(f[0], i)
            ret.append(file)
    return ret

def get_files(p):
    return _get_file(p,index=2)

def get_dirs(p):
    return _get_file(p,index=1)

 

class Db_Mani:
    # 操纵数据库 省去连接提交featch的操作
    def __init__(self,db):
    #    U:/pro/db/av.db
        con = sqlite3.connect(db)
        c = con.cursor()
        self.con, self.c = con, c

    def insm(self, sql, ins):
        ins=[i for i in ins if i]
        if not ins:
            print('insm 0')
            return
        self.c.executemany(sql, ins)
        self.con.commit()

    def ins(self, sql, ins):
       
        self.c.execute(sql, ins)
        self.con.commit()

    def create(self, *sql):
        # 建表
        for i in sql:
            self.c.execute(i)
        self.con.commit()

    def createm(self, sqls):
        # 建多表
        for sql in sqls:
            self.create(sql)
      

    def update(self, sql):
        self.c.execute(sql)
        self.con.commit()

    def query(self, sql,simple=False):
        ret = self.c.execute(sql).fetchall()
        # 多行单列数据 化为数组
        if ret and len(ret[0])==1:
            ret=[i[0] for i in ret]
            # 单行单列返回一个元素
            if not simple and len(ret)==1:
                ret=ret[0]
        return ret
    def query_one(self,sql):
        r=self.query(sql)
        if r:
            return r[0]
    
    def fixtime(self):
        # 数据库 时间戳转为字符
        r=self.query('select id ,ctime from web_fc')
        func=TimeM().timestamp_tos
        ins=[(func(i[1],format='%Y-%m-%d'),i[0]) for i in r if not '-' in i[1]]
        self.insm('update web_fc set ctime=? where id=?',ins)

class VideoM:
    
    def shot_sth(self,file,t,cnt=1):
        try:
            v= editor.VideoFileClip(str(file))  
            if isinstance(t,str ) and '%' in t:
                t=v.duration*int(t.replace('%',''))//100
        except:
            if cnt==1:
                # 意外硬链接随即名再试一次
                newname=Path(file).parent.parent.joinpath('temphd',f'{random.random()}'+Path(file).suffix)
                dir_make(newname.parent)
                os.link(file,newname)
                r=self.shot_sth(newname,t,cnt=0)
                if r:
                    return r
            return
        return v,int(t)

    def shot(self,file,img,t):
        #视频截图
        if os.path.exists(img):
            return img
       
        t=self.shot_sth(file,t)
        if not t:
            return
        v,t=t
        v=v.resize(0.1)
        v.save_frame(img,t=t)
        return img

    def shot_gif(self,file,img,t=3,dur=1):
        # 缩略图 gif
        if os.path.exists(img):
            # print(f'已存在{img}')
            return img
        try:
            t=self.shot_sth(file,t)
            if not t:
                return
            v,t=t
            clip = v.subclip(t,t+dur) .resize(0.3).set_fps(15)
            clip.write_gif(img)
        except:
            # os.link(file,Path(file).with_name('a.mp4'))
            return

    def thumbnail(self,file,img):
        # 缩略图
        if os.path.exists(img):
            return
        try:
            im=Image.open(file)
            im.thumbnail((1080,1080))
            im=im.convert('RGB')
            im.save(img,'JPEG')
        except:
            return
 
def movefile_bydict(args, func, desc='rename',reverse=False):
    '''
    根据元组 文件移动/复制 反向撤销操作不记录日志
    '''
    arg = [i for i in args if i   and not os.path.abspath(i[0])==os.path.abspath(i[1])]
    print(f'{desc} 实际任务 len:{len(arg)}/{len(args)}')
    if not arg:
        return
    
     
    def f(i):
        try:
            if reverse:
                func(i[1], i[0])
            else:
                func(i[0], i[1])
            return [0,'']
        except:
         
            s='失败数目 {}->{}'.format(i[0], i[1]) 
            return [1,s]

    ret=multi_threadpool(args=arg, func=f, desc=desc, pool_size=1)
    ss=[i[1] for i in ret if i[0]==1]
    
    ret=[i[0] for i in ret]
    print(f'error:{sum(ret)}/{len(arg)}')
    
def renamem(ren,file='',flag=0):
    # 改名等待 先输出到文本 1写入 2读取  /9先改名再等待撤销
    arg = [i for i in ren if i]
    if not arg:
        return
    if flag==1:
        arg=[f'{i},{j}' for i,j in arg]
        open(file,'w').write('\n'.join(arg))
        input('renamem txt')
        return
    if flag==2:
        r=open(file,'r').read().split('\n')
        ren=[i.split(',') for i in r if i.strip()]
       
        
    movefile_bydict(ren,func=os.renames,desc='rename')
    if flag==9:
        input('rec:')
        renamer()
        
def renamer(seq_rank=0):
    # 改名恢复 有效文件特点flag
    flag='rename_bydict'
    files=get_files(PickleM.root)
    files.sort(key=lambda x:os.path.getctime(x),reverse=True)
    
    file=files[seq_rank]
    # 程序改正输入
    if not flag in file:
        for i in files:
            if flag in i:
                file=i
                break
    r=PickleM().get(file)
    movefile_bydict(args=r,func=os.renames,desc='recovery',reverse=True)

def hardlink_bydict(arg=''):
    dirset={Path(i[1]).parent for i in arg if i}
    [dir_make(i) for i in dirset]
    movefile_bydict(arg,func=os.link,desc='硬链接')
   
   
class SystemM:
    # 系统接口
    # os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
    video_info='ffmpeg -hide_banner -i "{}"'
    video_compress_movie='ffmpeg -hide_banner  -y -i "{}"  -r 24 -vf scale=1920:1080 -crf 18  "{}"'
    video_compress='ffmpeg -hide_banner -hwaccel cuvid  -y -i "{}"  -r 30  {} -crf 18  "{}"'
    video_trans='ffmpeg -hide_banner  -y -i "{}"    "{}"'
    video_shot='ffmpeg  -ss {} -i "{}"  "{}"'
    video_cuthead='ffmpeg  -ss { } -i "{ }" -c copy  "{}"'
    @staticmethod
    def cmd_get( cmd):
        r = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',errors='ignore').communicate()
        try:
            info=' '.join(r)
        except TypeError:
            # (' ',None)
            print('cmd get type error')
            return ''
        return info

class HashM:
    def _hash_all(self,h,p):
        # hash文件 每次部分读取 c盘异常读写是文件太大 调用缓存
        n=1024*1024*1024
        with open(p,'rb')as f:
            a=f.read(n)
            while a:
                h.update(a)
                a=f.read(n)
        
        r=h.hexdigest().upper()
        return r

    def _hash_part(self,h,p,l=128*1024):
        h.update(open(p,'rb').read(l))
        r=h.hexdigest().upper()
        return r

    def sha1_all(self,p):
        h = hashlib.sha1()
        return self._hash_all(h,p)

    def sha1_head(self,p):
        h = hashlib.sha1()
        return self._hash_part(h,p)
    
    def sha1_parts(self,p):
        # 三等分部分hash 迅雷
        h = hashlib.sha1()
        size = os.path.getsize(p)
        with open(p, 'rb') as stream:
            if size < 0xF000:
                h.update(stream.read())
            else:
                h.update(stream.read(0x5000))
                stream.seek(size // 3)
                h.update(stream.read(0x5000))
                stream.seek(size - 0x5000)
                h.update(stream.read(0x5000))
        return h.hexdigest().upper()
        
class AllFile:
    # 所有文件 自定义获取
    @staticmethod
    def _replacenum(item):
        # 字符串替换后 长度变化
        r= item.replace('\\','')
        a,b=len(item),len(r)
        return a-b

    def _leveln(self,root,index, n=0):
        # 生成过滤 获取n层元素
        r=_get_file(root,index)
        ret=r
        if n>0:
            ret=[i for i in r if self._replacenum(i.replace(root,''))==n]
        return ret
    
    def files(self,p,n=''):
        return self._leveln(p,index=2,n=n)
    
    def dirs(self,p,n=''):
        return self._leveln(p,index=1,n=n)
    
    def dirs_end(self,p ):
        # 叶子目录
        dirs=[i for i in get_dirs(p) if not get_dirs(i)]
        return  dirs

    def type(self,p,type):
        # 特定类型文件
        files=get_files(p)
        ret=files
        if type=='img':
            ret=[i for i in files if FileType_().is_image(i)]
        elif type=='video':
            ret=[i for i in files if FileType_().is_video(i)]
        elif type=='text':
            ret=[i for i in files if FileType_().is_text(i)]
        elif type=='audio':
            ret=[i for i in files if FileType_().is_audio(i)]
        else:
            ret=[i for i in files if  i.endswith(type)]
            
        return ret



def multi_threadpool(func,args, pool_size=1,desc='多线程',split_args=False):
    # 参数去空  
    args=[i  for i in args if i]
    count = len(args)
    if count==0:
        return []
     # 进度显示
    demo_desc='115 舌尖上的中国第1季 2012 7集 国语中字 MP4 1080P 6G'
    desc = '{} thread:{}'.format(desc[:len(demo_desc)], pool_size)
    suffix = ' eta:%(eta).2f  avg:%(avg).2f index:%(index)d(%(max)d) ela:%(elapsed).2f %(percent)d%%'
    if  pool_size == 1:
        ret_list = list(
            map(func, Bar(desc, fill='.', suffix=suffix).iter(args)))
        return ret_list
    # 线程池大小
    if count < pool_size:
        pool_size = count
    # 构造线程池
    pool = ThreadPoolExecutor(max_workers=pool_size)
    if split_args:
        tasks = [pool.submit(func,*arg) for arg in args]
    else:
        tasks = [pool.submit(func,arg) for arg in args]
    # wait(tasks, return_when=ALL_COMPLETED) //不要返回值
    # 收集返回值
    ret_list=[]
   

    with Bar(desc, max=len(args), suffix=suffix) as bar:
        for task in as_completed(tasks):
            if task.done():
                ret_i = task.result()
                ret_list.append(ret_i)
                bar.next()
        return ret_list

from threading import Thread
def thread_back(func,app):
    def f():
        with app.app_context():
            func()
    a=Thread(target=f  )
    a.daemon=True
    a.start()

class SmallFile:
    def thumbnail(self,file,img):
        # 缩略图
        if os.path.exists(img):
            return
        try:
            im=Image.open(file)
            im.thumbnail((1080,1080))
            im=im.convert('RGB')
            im.save(img,'JPEG')
        except:
            return

    def shot_jpg(self,src,dst,ss_rat=0.2  ):
        try:
            # 打开要截取缩略图的视频文件
            video = VideoFileClip(src)
            thumbnail = video.get_frame(t=int(video.duration*ss_rat))  # 截取时间为10s处的缩略图
            im=Image.fromarray(thumbnail)
            im.thumbnail((1080,1080))
            im=im.convert('RGB')
            im.save(dst,'JPEG')
        except:
            return
        
    def shot_gif(self,src,dst,ss_rat=0.2 ,t=1):
        # ss_rat 开始时间 百分比 归一 
        # 时间
        # ffprobe -i a.gif -show_entries format=duration -v quiet -of csv="p=0"
        exe=r'X:\bufferx\OneDrive\应用\module\ffmpeg\ffmpeg.exe'
        prob=r'X:\bufferx\OneDrive\应用\module\ffmpeg\ffprobe.exe'
    
        ss_cmd=f' "{prob}" -i "{src}" -show_entries format=duration -v quiet -of csv="p=0" '
        output = subprocess.Popen(ss_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,text=True)
        out, err = output.communicate()
        ss=int(re.findall('\d+',out)[0])*ss_rat
        r=subprocess.Popen([exe,'-y','-ss',str(ss),'-t','1' ,'-i',str(src),'-r','15','-vf','scale=-1:360',str(dst) ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # ffmpeg -i a.mp4 -ss 00:00:01 -t 3 -vf scale=320:-1 -r 5 -f gif - | gifsicle --optimize=3 --delay=6 > output.gif
        pass

def backup_tag():
    # 备份恢复tag
    src=Db_Mani(r"C:\Users\Zin\Downloads\元数据\数据库\data_explorer(1).db")
    dst=Db_Mani(r'X:/库/code/flask explorer/data_explorer.db')
    data=src.query('select * from tag')
    print(f'tag数量：{dst.query("select count(*) from tag")}')
    dst.insm('insert or ignore into tag values(?,?,?,?)',data)
    print(f'tag数量：{dst.query("select count(*) from tag")}')

def douyin_tag():
    # 提取tag文件
    dst=Path(r'X:\库\DyView\get tag')
    dir_make(dst)
    dirs=[r'X:\库\视频\dy like',r'X:\库\DyView']
    db=Db_Mani(r'X:/库/code/flask explorer/data_explorer.db')
    data=db.query('select tag.tag, file.path from tag,file where file.id=tag.id and tag.tag!="del"')
    print(f'tag数量：{len(data)}')
    files=[]
    for dat in data:
        for dir in dirs:
            if dir in dat[1]:
                files.append(dat)
    ren=[[i[1],dst.joinpath(i[0]+Path(i[1]).name)] for i in files]
    hardlink_bydict(ren)

def list_setitem(listitem,n=3):
    # 有序字典 提取重复列表前n个
    unique_dict = OrderedDict()
    for i in listitem:
        unique_dict[i] = True
    r = list(unique_dict.keys())[:n]
    return  r

def item_vis(item,app):
    # 数据数据添加列 更直观
    item.vsize=f'{item.size//1024**2}MiB'
    # 特定文件指定缩略图名
    if item.type=='video' or item.type=='img':
        # c=dbm.session.query(IdPath).filter_by(id=item.id).first()
        c=app.config['data'].get(item.id)
        if c:
            item.hashname=c 
    else:
        item.hashname=f'{item.id}'
 
    if item.tag and item.tag.like:
        item.is_like=True
    if not Path(item.path).suffix in item.name:
        item.name+=Path(item.path).suffix
    return item

def url_args(url):
    # url参数键值对
    r=dict()
    query_string =  unquote(urlparse(url).query)
    # 解析查询字符串中的键值对参数
    query_params = parse_qs(query_string)
    for key, value in query_params.items():
        r[key]=value[0]
    return r




def item_vis(item,app):
    # 数据数据添加列 更直观
    item.vsize=f'{item.size//1024**2}MiB'
    # 获取缩略图位置
    hashname=app.config['data'].get(item.id)
    item.hashname=f'{item.id}' if not hashname else hashname
    # 添加标记 是否喜欢
    item.is_like=True if item.tag and item.tag.like else False
    # 添加文件后缀
    item.vname =item.name+ Path(item.path).suffix if not Path(item.path).suffix in item.name else item.name
     
    return item
 
def items_vis(items,app):
    return [item_vis(i,app) for i in items]

def srt2vtt(file ):
    content = open(file, "r", encoding="utf-8").read()
    # 替换“,”为“.”
    content = content.replace(',','.')
    lines=content.splitlines()
    newlines=[]
    for i in range(len(lines)-1):
        if ':' in lines[i]:
            newlines.append(lines[i])
            newlines.append(lines[i+1])
            newlines.append('\n')
    content='\n'.join(newlines)
    content=content.replace('\n\n','\n')
    content = "WEBVTT\n\n" + content
    return content

class FilesUni:
    # 统一文件 就近集中，方便复制
    def rename(self,src,dst):
        # 复制文件 保留元数据，优先硬链接
        if os.path.exists(dst):
            return
        try:
            os.link(src,dst)
        except:
            shutil.copy2(src,dst)

    def files_biggest_drive(self,files):
        # 文件按盘位分组，返回数据最大的盘符
        drive_sizes=[(str(i)[0],os.path.getsize(i)) for i in files if os.path.exists(i)]
        drive_size=dict()
        for drive,size in drive_sizes:
            drive_size[drive]=size+drive_size.get(drive,0)
        drive_size_sortDesc=sorted(drive_size.items(),key=lambda x:x[1],reverse=True)
        return drive_size_sortDesc[0][0]
    
    def files_dst_dir(self,files):
        # 文件按盘位分组，返回目标路径
        dst_dir='{}:/collect-view/{}({})'.format(self.files_biggest_drive( files ),datetime.now().strftime("%Y-%m-%d"),len(files))
        dst_dir=Path(dst_dir)
        return dst_dir

    def run(self,files):
        # 多盘位文件，集中到根/collect/y-m-d(num)下 盘位取决于各盘位文件大小
        dst_dir=self.files_dst_dir(files)
        dir_make(dst_dir)
        [self.rename(i,dst_dir.joinpath(Path(i).name)) for i in files]

def thumbnail_index(ins=''):
    # 缩略图索引相对路径
    print('静态文件索引')
    p=r'C:\Users\Zin\Pictures\Saved Pictures\small file'
    c=r'C:\Users\Zin\Pictures\Saved Pictures\small file\index.cache'
    if os.path.exists(c):
        ins=pickle.load(open(c,'rb'))
        print('使用缓存')
    else:
        ins={Path(i).stem:i.replace(p+'\\','').replace('\\','/') for i in get_files(p)}
    pickle.dump(ins,open(c,'wb'))
    return ins

def get_relative_time(timestamp):
    # 获取时间戳相对简短时间
    now =  datetime.now()
    dt=datetime.fromtimestamp(timestamp)
    delta = now - dt
    if delta.days > 0:
        return f'{delta.days}天前'
    elif delta.seconds < 60:
        return '刚刚'
    elif delta.seconds < 60 * 60:
        minutes = delta.seconds // 60
        return f'{minutes}分钟前'
    else:
        hours = delta.seconds // 3600
        return f'{hours}小时前'

def create_small_file( func='',max=2820):
        # 生成缺少的缩略图 函数自定义处理，返回真值掩盖默认操作 
        smallfile_path=r'C:\Users\Zin\Pictures\Saved Pictures\small file'
        db=Db_Mani('data_explorer.db')
        already_ids={Path(i).stem for i in get_files(smallfile_path)}
        current_datetime =  datetime.now()

        # 计算三天前的日期时间
        three_days_ago = current_datetime -  timedelta(days=3)
        data_db=db.query('select id,type,path from file where (type="video" or type="img") and utime>"{}" '.format(three_days_ago))
        data_db=[i for i in data_db if not i[0] in already_ids]
        cnt=count()
        def f(i):
            id,type,path=i
            if next(cnt)>max:
                return
            if func :
                r=func(id,type,path)
                if r:
                    return r
            if    type=='img':
                p=smallfile_path+'/{}.jpg'.format(id)
                SmallFile().thumbnail( path,p)
            elif type=='video':
                p=smallfile_path+'/{}.jpg'.format(id)
                SmallFile().shot_jpg( path,p ) 
              
        ret=multi_threadpool(func=f,args=data_db,desc='生成缩略图jpg gif',pool_size=1 )
        ret=[i for i in ret if i]
        return ret
@cal
def f():
   
    1
    # backup_tag()
    # src=r"X:\库\视频\dy like\7214442324271713571.mp4"
    # dst=r'C:\Users\Zin\Videos\Captures\a.gif'
    # # douyin_tag()
    # print('end')
     
    # VideoM().shot_gif(i,base.joinpath(Path(i).name).with_suffix('.gif'),t='20%' )
 
f()