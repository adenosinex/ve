 
from collections import OrderedDict
from flask import g
from itertools import count
import pickle
import re
import time
from flask_sqlalchemy import get_debug_queries
from sqlalchemy import not_

import urllib3

from factory import *
from forms import *
from models import *
from tools import *
app=creat_app('dev2')
# flask run --port 80 --host 0.0.0.0
per_page=100
 
# 常规任务
with app.app_context():
        app.config['data']=thumbnail_index()
        DailyTask().run()
        pass 
        db_query_data

 

VisitedPages

def collect_file(url):
    # 收集文件 url参数筛选 后台程序
    data=db_query_data( tuple(url_args(url).items()),-1,-1)
    files_path=[i.path for i in  data]
    dst_dir=FilesUni().files_dst_dir(files_path)
    flash(f'正在收集:{dst_dir}')
    def f():
        FilesUni().run(files_path)
    Thread(target=f).run()

@app.route('/',methods=['GET', 'POST'])
def index( ):
    VisitedPages.log_url(request.full_path)

    search_form=SearchForm()
    filter_form=FilterForm()
    sort_form=SortForm()
    # 表单数据转发get
    if search_form.validate_on_submit():
        search_kw=search_form.search.data.strip() if search_form.search.data else ''
        kwargs_page=dict(request.args)
        kwargs_page['pn']=1
        if search_kw:
            kwargs_page['kw']=search_kw
        return redirect( url_for('index',**kwargs_page ))
    else:
         # 旧数据提取
        kwargs_page=url_args(request.url)
         # 文件收集 断点
        if kwargs_page.get('collect'): 
            collect_file(request.referrer)
            return redirect(request.referrer)# 文件收集
        
        # 表单预填充
        if kwargs_page.get('type'): 
            filter_form.media_type.data=kwargs_page.get('type')
        
        if kwargs_page.get('sort'): 
            sort_form.media_type.data=kwargs_page.get('sort').replace(' desc','').replace(' asc','')
        
        if kwargs_page.get('kw'):
            search_form.search.data=kwargs_page.get('kw')
        # 默认页码1
        pn=int(request.args.get('pn',1))
    # 数据获取处理
    start_time=time.time()
    pgn,dirs_data=db_query_data( tuple(kwargs_page.items()),pn,per_page)
    pgn.items=items_vis(pgn.items,app)
    # 获取元数据与数据
    data=dict()
    data['form']=search_form
    data['filter_form']=filter_form
    data['sort_form']=sort_form
    data['pagination']=pgn
    data['dirs_data']=dirs_data
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
    



@app.route('/media/<value>',methods=['GET', 'POST'])
def media(value):
    # 文件类型筛选
    url=url_add_args({'type':value})
    return redirect( url)

flag_is_desc=True
@app.route('/sort/<value>',methods=['GET', 'POST'])
def sort(value):
    # 文件排序
    global flag_is_desc
    if flag_is_desc:
        value+=' desc'
    else:
        value+=' asc'
    flag_is_desc=not flag_is_desc
    url=url_add_args({'sort':value})
    return redirect( url)

@app.route('/log/<string:op>')
@app.route('/log/<int:id>/<string:op>')
def logs( op,id='' ):
    # 置顶/删除记录 删除所有/除指定
    if id   :
        log=db.session.query(VisitedPages).filter_by(id=id).first()
        if op=='top':
            log.utime=datetime.utcnow()
            if log.is_top:
                log.is_top=False
            else:
                log.is_top=True
        else:
            db.session.delete(log)
    elif op=='delall':
        logs=db.session.query(VisitedPages).all()
        [db.session.delete(i)for i in logs]
    elif op=='del':
        logs=db.session.query(VisitedPages).filter(or_(VisitedPages.is_top==None,VisitedPages.is_top==False)).all()
        [db.session.delete(i)for i in logs]
    db.session.commit()
    return redirect(request.referrer) 


@app.route('/log')
def show_logs( ):
    # 历史记录
    logs=db.session.query(VisitedPages).order_by(VisitedPages.is_top.desc(),VisitedPages.utime.desc()).all()
    index=count(1)
    # log拓展信息 相对时间-索引排序-参数名
    def f(i):
        i.vtime=get_relative_time(i.utime.timestamp() )
        i.index=next(index)
        args=url_args(i.url)
        name=''
        if args.get(' dir_num'):
            dir_obj=db.session.query(Dir).filter_by(id= args.get(' dir_num')).one_or_none()
            if dir_obj:
                name=Path(dir_obj.path).name
                name='path:'+name
            elif   args.get(' dir_num') =='-1':
                name='path:all'
        if args.get(' pn') and not args.get(' pn')=='1':
            name+=' pn:'+args.get('pn')
        if args.get('kw'):
            name+=' kw:'+args.get('kw')
        i.name=name
        return i
    logs=[f(i) for i in logs]
    return render_template('logs.html',logs=logs)

@app.route('/keep')
def old_page():
    # 继续浏览 
    last_url=db.session.query(VisitedPages).order_by(VisitedPages.utime.desc()).first()
    if last_url:
        return redirect(last_url.url)
    else:
        return redirect(request.referrer)

@app.route('/vue')
def func_vue( ):
    return render_template('vue.html',now=datetime.now())



@app.route('/detail/<id>',methods=['GET', 'POST'])
def detail(id):
    # 详情页 文件对象。接受表单设置tag 返回所有tag，文件所在目录
    tf=TagForm()
    item=db.session.query(File).filter_by(id=id).first()
    if tf.validate_on_submit():
        tag=tf.tag.data
        item.set_tag(tag)
        return redirect(request.referrer)
    
    tags_all_src  =  db.session.query(Tag.tag, db.func.count(Tag.tag).label('cnt')).filter(Tag.tag!=None).group_by(Tag.tag).order_by( desc('cnt')).all()
    tags_all=[f'{i[1]}-{i[0]}' for i in tags_all_src  if i[0]]
    # 有序字典 提取重复列表前n个
    tags_rec_src =[i[0] for i in db.session.query( Tag.tag  ).filter(Tag.tag!=None).order_by(Tag.utime.desc()).limit(15).all()]
    tags_rec = list_setitem(tags_rec_src,3)

    item=item_vis(item,app)
    dir=db.session.query(Dir).filter(Dir.path==item.dir).first()
    item.dirobj=dir
    return render_template('detail.html',post=item,form=tf,tags=tags_rec+tags_all)
     

@app.route('/play/<id>')
def func_name(id):
    return render_template('play.html',id=id)

def back_work(f):
    # 后台 在程序上下文执行
    def func( ):
        with app.app_context():
            f()
    a=Thread(target=func )
    a.daemon=True
    a.start()

@app.route('/add',methods=['GET', 'POST'])
def add_files( ):
    form=AddDirForm()
    message=''
    if form.validate_on_submit():
        d=form.path.data+','
        paths=[i.strip() for i in d.split(',') if i]
        
        def f( ):
            InitData().scan_dir(paths)
            create_small_file()
        back_work(f)
        flash('正在添加数据')
        return redirect('/add')
    return render_template('add.html',form=form,message=message)

def files_info(files):
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
    posts=[f(i) for i in files]
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
    files=get_files(r'C:\Users\Zin\Documents\testdata\upload')
    data={
        'now':datetime.now(),
        'form':form,
        'posts':files_info(files)
    }
   
    return render_template('share.html',**data)

def url_add_args(kw):
     # url添加参数 页码归一
    # 旧数据提取
    kwargs=url_args(request.referrer)
    kwargs.update(kw)
    kwargs['pn']=1
    url=url_for('index',**kwargs )
    return url

if __name__=='__main__':
    
    app.run(port=80,host='0.0.0.0',debug=False)
    InitData.scan_dir
    db_query_data
    item_vis
     