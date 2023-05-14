 
from collections import OrderedDict
from flask import g
from itertools import count
import pickle
import re
import time
from sqlalchemy import not_

import urllib3

from factory import *
from forms import *
from models import *
from tools import *
app=creat_app('dev2')
# flask run --port 80 --host 0.0.0.0
per_page=100
get_files
def keep_3day_logs():
    # 只保留三天的历史记录
    today = datetime.now()  # 获取当前日期和时间
    delta = timedelta(days=3)  # 创建一个 timedelta 对象表示过去的三天
    three_days_ago = today - delta    # 计算出三天前的日期和时间
    r=db.session.query(Tag ).filter(Tag.utime<three_days_ago ,and_(Tag.like==None,Tag.like==None,)).all()
    [db.session.delete(i) for i in r]
    db.session.commit()

def memory_smallfile(ins=''):
    print('静态文件索引')
    p=r'C:\Users\Zin\Pictures\Saved Pictures\small file'
    c=r'C:\Users\Zin\Pictures\Saved Pictures\small file\index.cache'
    if os.path.exists(c):
        ins=pickle.load(open(c,'rb'))
        print('使用缓存')
    else:
        ins={Path(i).stem:i.replace(p+'\\','').replace('\\','/') for i in get_files(p)}
    pickle.dump(ins,open(c,'wb'))
    app.config['data']=ins
 
    return ins


 

with app.app_context():
        pass 
        r=memory_smallfile()
         
        # InitData().rindex_col()
        pass 
        # InitData().scan_dir(r'X:\库\视频\dy like')
        # InitData().scan_dir(r'X:\库\DyView')
        # InitData().scan_dir(r'D:\备份 万一\ds photo\video')
        # InitData().scan_dir(r'D:\抖音\mp4\tag')
        # InitData().scan_dir(r'D:\抖音\mp4\add')
        InitData().init_file
        FileProcessor.get_data_File
        # InitData().rinit_file(r'X:\库\视频\dy like\like')
        FileProcessor.process_dyname
       


@app.route('/',methods=['GET', 'POST'])
def index( ):
    # 记录url
    if not request.full_path in {'/', '/?','/keep' }:
        # '/?pn=2'
        last_url =request.url
        db.session.add(Log(url=last_url ))
        db.session.commit()
        print('log: '+last_url)
    
    sf=SearchForm()
    filter_form=FilterForm()
    sort_form=SortForm()
    if sf.validate_on_submit():
        search_kw=sf.search.data.strip() if sf.search.data else ''
        search_type=sf.select.data
         
        like=sf.like.data
        # 表单数据转发get
        kwargs_page=dict()
        kwargs_page['pn']=1
        if search_type!='none':
            kwargs_page['type']=search_type
        if search_kw:
            kwargs_page['kw']=search_kw
        # if is_dir:
        #     kwargs_page['dir_num']=-1
        if like:
            kwargs_page['like']=True
        # 保留get参数
        kwargs_page.update(dict(request.args))

        return redirect( url_for('index',**kwargs_page ))
    else:
         # 旧数据提取
        kwargs_page=dict()  
        old_args=url_args(request.url)
        kwargs_page.update(old_args)
        
 
        # 表单预填充
        if kwargs_page.get('type'): 
            sf.select.data=kwargs_page.get('type')
            filter_form.media_type.data=kwargs_page.get('type')
        if kwargs_page.get('sort'): 
            sort_form.media_type.data=kwargs_page.get('sort').replace(' desc','').replace(' asc','')
        
        if kwargs_page.get('kw'):
            sf.search.data=kwargs_page.get('kw')
           
        if kwargs_page.get('like'):
            sf.like.data=True
           
        pn=int(request.args.get('pn',1))
    # 数据获取处理
    start_time=time.time()
    base,dirs_data=db_query_data( kwargs_page)
    
    # 无参数按添加时间排序
    if len(kwargs_page)==0 or (len(kwargs_page)==1 and kwargs_page.get('pn')):
        base=base.order_by(File.utime.desc())
    else:
        base=base.order_by(File.ctime.desc())
    pgn=base.paginate(page=pn,per_page=per_page)
    pgn.items=[item_vis(i) for i in pgn.items]
    # 获取元数据与数据
    data=dict()
    data['form']=sf
    data['pagination']=pgn
    data['dirs_data']=dirs_data
    data['filter_form']=filter_form
    data['sort_form']=sort_form
    data.update({
    'pages':f'{pgn.per_page}/{pgn.total}',
    'spend_time':'{:.3f}毫秒'.format( (time.time()-start_time)*1000),
    'type':kwargs_page.get('type')
    })
 
  
    # 目录链接去除指派目录
    kwargs_link=kwargs_page.copy()
    if 'dir_num' in kwargs_link:
       kwargs_link.pop('dir_num')
    if 'pn' in kwargs_link:
       kwargs_link.pop('pn')
    if 'pn' in kwargs_page:
       kwargs_page.pop('pn')

   
    return render_template('index.html',endpoint='index',kwargs_link =kwargs_link,kwargs_page=kwargs_page,**data)
    
    
def url_add_args(kw):
     # url添加参数
    # 旧数据提取
    kwargs=url_args(request.referrer)
    kwargs['pn']=1
    kwargs.update(kw)
    url=url_for('index',**kwargs )
    return url

@app.route('/media/<value>',methods=['GET', 'POST'])
def media(value):
    # 文件类型筛选
    url=url_add_args({'type':value})
    return redirect( url)

flag=False
@app.route('/sort/<value>',methods=['GET', 'POST'])
def sort(value):
    # 文件排序
    global flag
    if flag:
        value+=' desc'
    else:
        value+=' asc'
    flag=not flag
    url=url_add_args({'sort':value})
    return redirect( url)

    
def url_args(url):
    # url参数键值对
    r=dict()
    query_string =  unquote(urlparse(url).query)
    # 解析查询字符串中的键值对参数
    query_params = parse_qs(query_string)
    for key, value in query_params.items():
        r[key]=value[0]
    return r


@app.route('/log/<string:op>')
@app.route('/log/<int:id>/<string:op>')
def logs(id='',op=''):
    # 置顶/删除记录 删除所有/除指定
    if id or op:
        if id   :
            log=db.session.query(Log).filter_by(id=id).first()
            if op=='top':
                log.utime=datetime.utcnow()
                if log.is_top:
                    log.is_top=False
                else:
                    log.is_top=True
            else:
                db.session.delete(log)
        elif op=='delall':
            logs=db.session.query(Log).all()
            [db.session.delete(i)for i in logs]
        elif op=='del':
            logs=db.session.query(Log).filter(or_(Log.is_top==None,Log.is_top==False)).all()
            [db.session.delete(i)for i in logs]
        db.session.commit()
    return redirect(request.referrer) 


@app.route('/log')
def show_logs( ):
    # 历史记录
    logs=db.session.query(Log).order_by(Log.utime.desc()).limit(30).all()
    toplogs=db.session.query(Log).filter_by(is_top=True).order_by(Log.utime.desc()).all()
    losgs_set=[i.id for i in toplogs]
    logs=toplogs+[i for i in logs if not i.id in losgs_set]
    index=count(1)
    # log拓展信息
    def f(i):
        i.time=i.utime 
        i.index=next(index)
        dir_num=parse_qs(urlparse(i.url).query).get('dir_num',' ')[0]
        pn=parse_qs(urlparse(i.url).query).get('pn',' ')[0]
        name=''
        if dir_num:
            dir_obj=db.session.query(Dir).filter_by(id=dir_num).one_or_none()
            if dir_obj:
                name=Path(dir_obj.path).name
                name='path:'+name
            elif  dir_num =='-1':
                name='path:all'
        if pn:
            name+=' pn:'+pn
        i.name=name
        return i
    logs=[f(i) for i in logs]
    return render_template('logs.html',logs=logs)

@app.route('/keep')
def old_page():
    last_url=db.session.query(Log).order_by(Log.utime.desc()).first()
    if last_url:
        return redirect(last_url.url)
    else:
        return redirect(request.referrer)

@app.route('/vue')
def func_vue( ):
    return render_template('vue.html',now=datetime.now())

def db_query_data(data):
    # 过滤数据
    base=File.query 
    # 目录筛选
    dirs=''
    # 喜欢
    if data.get('like'):  
        base=base.filter(File.tag!=None  )
        base=base.join(Tag).filter(Tag.tag!='del').order_by(File.type.desc(),Tag.utime.desc())
        

    # 路径模式
    dirs_data=[]
    if  data.get('dir_num') :  
        dir_num=int(data.get('dir_num') )
        if dir_num==0 or dir_num==-1:
            item=Dir.query.order_by(Dir.level).first()
        else:
            item=Dir.query.filter_by(id=dir_num).first()
        # 目录筛选 文件夹列表第一个为父文件夹
        if item:
            request_path=item.path
            # 根文件夹      
            if dir_num==-1:
                print(item.level)
                dirs=Dir.query.order_by(Dir.path).filter_by( rank=1).all()
            # 子文件夹
            else:
                dirs=Dir.query.filter_by( dir =request_path).all()
            # 寻找父文件夹
            pdirs=Dir.query.filter_by( path =item.dir).first()
            # 顶层文件夹 设为/
            if not pdirs:
                pdirs=Dir(id=-1,path='/')
            
            def f(i):
                # 只保留爷目录名 方便查看
                t=Path(i.path).parent.parent
                i.vpath=i.path  if dir_num==-1 else i.path.replace(str(t),'')
                return i
            dirs_data={
                'parent':f(pdirs),
                'current': f(item),
                'dirs':[ f(i) for i in dirs]
            }
            base=base.filter(File.dir==request_path)

    # 类型字筛选
    type=data.get('type') 
    if   type and type!='all':
        base=base.filter(File.type==type) 
    # 关键词筛选
    if   data.get('kw'):
        s=data.get('kw')
        mul=1024**2
        if 'size>' in s:
            n=s.replace('size>','')
            base=base.filter(File.size>int(n)*mul)
        elif 'size<' in s:
            n=s.replace('size<','')
            base=base.filter(File.size<int(n)*mul)
        elif 'pathid:' in s:
            n=s.replace('pathid:','')
            r=Dir.query.filter_by(id=int(n)).first()
            base=base.filter(File.path.like(f'%{r.path}%'))
        else:
            base=base.filter(multi_ruledb(data.get('kw')))
    # 过滤不存在 标记删除
    base=base.filter(~File.path.startswith('del')).filter(~File.path.startswith('del'))
    ids=[i.id for i in Tag.query.filter(Tag.tag=='del').all()]
    base=base.filter(not_(File.id.in_(ids)))

    if data.get('sort'):
        s=data.get('sort')
        print(s)
        base=base.order_by(text(s))
    else:
        base=base.order_by(File.num)
       

    return base,dirs_data
 


def item_vis(item):
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
 
def items_vis(items):
    return [item_vis(i) for i in items]

@app.route('/detail/<id>',methods=['GET', 'POST'])
def detail(id):
    tf=TagForm()
    item=db.session.query(File).filter_by(id=id).first()
    if tf.validate_on_submit():
        tag=tf.tag.data
        item.set_tag(tag)
        return redirect(request.referrer)
    
    tags_all_src  =  db.session.query(Tag.tag, db.func.count(Tag.tag).label('cnt')).filter(Tag.tag!=None).group_by(Tag.tag).order_by( desc('cnt')).all()
    tags_rec_src =[i[0] for i in db.session.query( Tag.tag  ).filter(Tag.tag!=None).order_by(Tag.utime.desc()).limit(15).all()]
    # tags_rec_src =[i  for i in db.session.query(Tag.tag   ).order_by(Tag.utime.desc()).all()]
    # 有序字典 提取重复列表前n个
    tags_rec = list_setitem(tags_rec_src,3)

    tags_all=[f'{i[1]}-{i[0]}' for i in tags_all_src  if i[0]]
    item=item_vis(item)
    dir=db.session.query(Dir).filter(Dir.path==item.dir).first()
    item.dirobj=dir
    return render_template('detail.html',post=item,form=tf,tags=tags_rec+tags_all)
     

@app.route('/play/<id>')
def func_name(id):
    return render_template('play.html',id=id)

@app.route('/add',methods=['GET', 'POST'])
def add_files( ):
    form=AddDirForm()
    message=''
    if form.validate_on_submit():
        d=form.path.data+','
        paths=[i.strip() for i in d.split(',') if i]
        
        def f( ):
            with app.app_context():
                InitData().scan_dir(paths)
                t=Thread(target=lambda :os.system('rungetsmallfile.bat'))
                t.start()
        a=Thread(target=f )
        a.daemon=True
        a.start()
        # r=InitData().scan_dir(paths)
        # flash(r)
        flash('正在添加数据')
        return redirect('/add')
    return render_template('add.html',form=form,message=message)

def files_info(p):
    # 遍历文件信息
    class DbDate:
        pass
    cnt=count(1)
    def f(i):
        t=DbDate()
        t.index=next(cnt)
        t.name=Path(i).name
        t.size=os.path.getsize(i)
        t.vsize=f'{t.size//1024**2}MB'
        return t
    posts=[f(i) for i in get_files(p)]
    return posts

@app.route('/share',methods=['GET', 'POST'])
def share( ):
    form=UpFile()
    p=app.config.get('SAVE')
    dir_make(p)
    if form.validate_on_submit():
        # 获取所有file
        files=request.files.getlist('file')
        for file in files:
            file.save('{}/{}'.format(p,file.filename))
       
        return redirect(request.referrer)
    # 展示文件
    data={
        'now':datetime.now(),
        'form':form,
        'posts':files_info()
    }
   
    return render_template('share.html',**data)
    
if __name__=='__main__':
    
    app.run(port=80,host='0.0.0.0',debug=False)
    sort
    db_query_data
     