 
from itertools import count
import re
import time

from factory import *
from forms import *
from models import *
from tools import *
app=creat_app('pro')
# flask run --port 80 --host 0.0.0.0
per_page=100
 
with app.app_context():
        # who.reindex()
          
        db.create_all()  
        File
        # InitData().ana_dyname()
        # InitData().scan_dir(r'X:\库\视频\dy like',app)
 
 
        
 
with app.test_request_context('/' ):
        assert request.path == '/'

class DbDate:
    pass
 
@app.route('/log/<string:op>')
@app.route('/log/<int:id>/<string:op>')
@app.route('/log')
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
        redirect(request.referrer) 
    # 历史记录
    logs=db.session.query(Log).filter(or_(Log.is_top==None,Log.is_top==False)).order_by(Log.utime.desc()).all()
    toplogs=db.session.query(Log).filter_by(is_top=True).order_by(Log.utime.desc()).all()
    logs=toplogs+logs 
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
        last_url=last_url.url
    if last_url:
        return redirect(last_url)
    else:
        return redirect(request.referrer)

@app.route('/vue')
def func_vue( ):
    return render_template('vue.html',now=datetime.now())

def filter_data(like='',dir_num='',type='',kw=''):
    base=File.query 
    # 目录筛选
    dirs=''
    
    # 喜欢
    if like:  
        base=base.filter(File.tag!=None )
        base.join(Tag,File.tag).order_by(Tag.tag)

    # 路径模式
    dirs_data=[]
    if dir_num  :  
        dir_num=int(dir_num)
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
    if   type and type!='all':
        base=base.filter(File.type==type) 
    # 关键词筛选
    if   kw:
        # base=base.filter(multi_ruledb(search_kw))
        t=kw if len(kw)>2 else kw+' '+kw
        multi_ruledb
        # base=base.filter(File.path.like('%{}%'.format(search_kw)))
        base=base.whooshee_search(t)
    return base,dirs_data
 


@app.route('/',methods=['GET', 'POST'])
def index( ):
    # 记录url
    if not request.full_path in {'/', '/?','/keep' }:
        # '/?pn=2'
        last_url=request.url
        db.session.add(Log(url=last_url ))
        db.session.commit()
        print('log: '+last_url)
    
    
    
    sf=SearchForm()
    if sf.validate_on_submit():
        search_kw=sf.search.data.strip() if sf.search.data else ''
        search_type=sf.select.data
        is_dir=sf.dir.data
        like=sf.like.data
        # 表单数据转发get
        kwargs_page=dict()
        kwargs_page['pn']=1
        if search_type!='none':
            kwargs_page['type']=search_type
        if search_kw:
            kwargs_page['kw']=search_kw
        if is_dir:
            kwargs_page['dir_num']=-1
        if like:
            kwargs_page['like']=True
        # 保留get参数
        kwargs_page.update(dict(request.args))

        return redirect( url_for('index',**kwargs_page ))
    else:
        search_kw=request.args.get('kw')
        search_type=request.args.get('type')
        dir_num=request.args.get('dir_num')
        like=request.args.get('like')
         # 传递页码关键词
        kwargs_page=dict()  
        if search_type: 
            sf.select.data=search_type
            kwargs_page['type']=search_type
        if search_kw:
            sf.search.data=search_kw
            kwargs_page['kw']=search_kw
        if   dir_num:  
            sf.dir.data=True
            kwargs_page['dir_num']=dir_num
        if like:
            sf.like.data=True
            kwargs_page['like']=True
        pn=int(request.args.get('pn',1))
    # 数据获取处理
    start_time=time.time()
    base,dirs_data=filter_data(**kwargs_page)
    base=base.order_by(File.num)
    base=base.order_by(File.ctime.desc())
    pgn=base.paginate(page=pn,per_page=per_page)
    pgn.items=[item_vis(i) for i in pgn.items]
    # 获取元数据与数据
    data=dict()
    data['form']=sf
    data['pagination']=pgn
    data['dirs_data']=dirs_data
    data.update({
    'pages':f'{pgn.per_page}/{pgn.total}',
    'spend_time':'{:.3f}毫秒'.format( (time.time()-start_time)*1000),
    'type':search_type
    })
 
  
    # 目录链接去除指派目录
    kwargs_link=kwargs_page.copy()
    if 'dir_num' in kwargs_link:
       kwargs_link.pop('dir_num')

    # print(kwargs_page,kwargs_link)
    return render_template('index.html',endpoint='index',kwargs_link =kwargs_link,kwargs_page=kwargs_page,**data)
    
     
  
def item_vis(item):
    # 数据查看 更直观
    item.vsize=f'{item.size//1024**2}MiB'
    # 特定文件指定缩略图类型后缀
    if '水果派' in item.path:
        item.suffix='img'
    if item.tag and item.tag.like:
        item.like=True

    return item

@app.route('/detail/<id>',methods=['GET', 'POST'])
def detail(id):
    item=db.session.query(File).filter_by(id=id).first()
    tags=[i[0] for i in db.session.query(distinct(Tag.tag) ).filter(Tag.tag!=None).order_by(Tag.utime.desc()).all()]
    tf=TagForm()
    if item:
        item=item_vis(item)
        if tf.validate_on_submit():
            tag=tf.tag.data
            item.set_tag(tag)

        return render_template('detail.html',post=item,form=tf,tags=tags)
    return abort(404)

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
        a=Thread(target=InitData().scan_dir,args=(paths,app))
        a.daemon=True
        a.start()
        # r=InitData().scan_dir(paths)
        # flash(r)
        flash('正在添加数据')
        return redirect('/add')
    return render_template('add.html',form=form,message=message)

@app.route('/share',methods=['GET', 'POST'])
def share( ):
    form=UpFile()
    p=os.getenv('SAVE')
    dir_make(p)
    if form.validate_on_submit():
        # 获取所有file
        files=request.files.getlist('file')
        for file in files:
            file.save('{}/{}'.format(p,file.filename))
       
        return redirect(request.referrer)
    cnt=count(1)
    def f(i):
        t=DbDate()
        t.index=next(cnt)
        t.name=Path(i).name
        t.size=os.path.getsize(i)
        t.vsize=f'{t.size//1024**2}MB'
        return t
    posts=[f(i) for i in get_files(p)]
    data={
        'now':datetime.now(),
        'form':form,
        'posts':posts
    }
   
    return render_template('share.html',**data)
    
if __name__=='__main__':
    app.run(port=80,host='0.0.0.0',debug=False)