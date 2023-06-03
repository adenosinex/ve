
from collections import OrderedDict
from itertools import count
import time


from factory import *
from forms import *
from models import *
from tools import *

app = creat_app('pro')
# flask run --port 80 --host 0.0.0.0
per_page = 100


def back_work(f ):
    # 后台 在程序上下文执行
    def func():
        with app.app_context():
            f()
    a = Thread(target=func)
    a.daemon = True
    a.start()


def back_work_scandir(paths):
    def f():
        InitData().scan_dir(paths)
        create_small_file()
    back_work(f)

def tags_get():
    # 获取tag标签
    all_tags =','.join ([ i.tag for i in  Tag.query.filter(Tag.tag!=None).all()])
    count_tag=Counter(all_tags.split(',')).most_common()
    all_tag = [f'{i[1]}-{i[0]}' for i in count_tag if i[0]]
    # 有序字典 提取重复列表前n个
    rec_tags =  [ i.tag for i in  db.session.query((Tag )).filter(Tag.tag!=None,Tag.tag!='del').order_by(Tag.utime.desc()).limit(10).all()] 
    rec_tags=','.join(rec_tags).split(',')
    unique_dict = OrderedDict.fromkeys(rec_tags)
    tags_rec = list(unique_dict.keys())[:5]
    
    return all_tag,tags_rec

 
# 常规任务
with app.app_context():
    def f():
        
        pass
    f()
    app.config['data'] = thumbnail_index(app.config.get('SMALL_FILE_PATH'))
    app.config['preview_data'] = thumbnail_index(
        r'X:\库\索引\videoshot_preview', lambda i, p: i)
    DailyTask().run()
    Tag.del_empty()
    back_work(f=create_small_file)
   

 
def collect_file(url):
    # 收集文件 放在磁盘目录 url参数筛选 后台程序
    if 'sort:random' in url:
        db_query_data.cache_clear()
    data = db_query_data(tuple(url_args(url).items()), -1, -1)
    files_path = [i.path for i in data]
    dst_dir = FilesUni().files_dst_dir(files_path)
    flash(f'正在收集:{dst_dir}')

    def f():
        FilesUni().run(files_path)
    Thread(target=f).run()


def file_getkw(items):
    # 文件对象信息组合 获取关键词
    relation_text = ''
    for i in items:
        t = f'{i.name} {i.path} {i.kw} {i.tag.tag if i.tag else 0} '
        relation_text += t
    return Txt_Ana().topn(relation_text, getn=20, least_repeat=2)


db_query_data
items_vis

@app.route('/', methods=['GET', 'POST'])
def index():
    VisitedPages.log_url(request.full_path)

    search_form = SearchForm()
    filter_form = FilterForm()
    sort_form = SortForm()
    # 表单数据转发get
    if search_form.validate_on_submit():
        search_kw = search_form.search.data.strip() if search_form.search.data else ''
        kwargs_page = dict(request.args)
        kwargs_page['pn'] = 1
        if search_kw:
            kwargs_page['kw'] = search_kw
        return redirect(url_for('index', **kwargs_page))
    else:
        # 旧数据提取
        kwargs_page = url_args(request.url)
        # 文件收集 断点
        if kwargs_page.get('collect'):
            collect_file(request.referrer)
            return redirect(request.referrer)  # 文件收集

        # 表单预填充
        # if kwargs_page.get('type'):
        filter_form.media_type.data = kwargs_page.get('type', '')
        sort_form.media_type.data = kwargs_page.get(
            'sort', '').replace(' desc', '').replace(' asc', '')
        search_form.search.data = kwargs_page.get('kw', '')
        # 默认页码1
        pn = int(request.args.get('pn', 1))
    # 数据获取处理
    start_time = time.time()
    pgn, dirs_data = db_query_data(tuple(kwargs_page.items()), pn, per_page)
    pgn.items = items_vis(pgn.items, app)
    # 搜索词的相关词
    kws = file_getkw(pgn.items)
    # 获取元数据与数据
    data = dict()
    data['form'] = search_form
    data['filter_form'] = filter_form
    data['sort_form'] = sort_form
    data['pagination'] = pgn
    data['dirs_data'] = dirs_data
    data.update({
        'pages': f'页码:{pgn.page}/{pgn.pages}({pgn.per_page}) 个数:{pgn.total}',
        'spend_time': spend_time(start_time),
        'type': kwargs_page.get('type'),
        'kws': kws
    })

    # 目录链接去除指派目录
    kwargs_link = kwargs_page.copy()
    if 'dir_num' in kwargs_link:
        kwargs_link.pop('dir_num')
    if 'pn' in kwargs_link:
        kwargs_link.pop('pn')
    if 'pn' in kwargs_page:
        kwargs_page.pop('pn')

    return render_template('index.html', endpoint='index', kwargs_link=kwargs_link, kwargs_page=kwargs_page, **data)

@app.route('/detail/<id>', methods=['GET', 'POST'])
def detail(id ):
    # 详情页 文件对象。接受表单设置tag 返回所有tag，文件所在目录
    if log_last_play(id):
        return log_last_play(id)
    tf = TagForm()
    start_time = time.time()
    item = db.session.query(File).filter_by(id=id).first()
    # 文件信息
    infos = orm_dict(item)
    infos['db耗时'] = f'{spend_time(start_time)}'
    infos['size'] = convert_size(infos['size'])
    if item.video:
        infos.update(orm_dict(item.video))
        infos['duration'] = convert_time(infos['duration']//10**3)
        infos['bit_rate'] = convert_size(infos['bit_rate'] )

    item.infos = infos

    if tf.validate_on_submit():
        tag = tf.tag.data
        item.set_tag(tag)
        return redirect(request.referrer)
      # 部分网页 相关作品
    if request.args.get('part') == 'rels':
        item = rel_data(item)
        item.spend_time = spend_time(start_time)
        return render_template("part_rel.html", post=item)
    # 截图时间信息转化信息
    for i in item.shot:
        i.vtime = format_second_time(i.stime)
    if item.shot:
        item.shots = list(filter(lambda x: x.is_auto == 0, item.shot))
        item.pshots = list(filter(lambda x: x.is_auto == 1, item.shot))
        item.pshots.sort(key=lambda x: x.stime)
    # 部分网页 截图
    if request.args.get('part') == 'shots':
        return render_template("part_shots.html", posts=item.shots)
    # 部分网页 截图
    if request.args.get('part') == 'previews':
        return render_template("part_shots.html", posts=item.pshots)

    
    tags_all,tags_rec=tags_get()
    item = item_vis(item, app)

    # 目录
    dir = db.session.query(Dir).filter(Dir.path == item.dir).first()
    item.dirobj = dir
    # 抖音链接
    id = Path(item.path).stem
    if len(id) == 19 and re.findall('\d{19}', id):
        item.dylink = 'https://www.douyin.com/video/'+id
    
    data = {
        'form': tf,
        'tagsRec': tags_rec,
        'tagsTop':tags_all,
    }
    if item.tag and item.tag.tag:
        item.tag.vtags=[i for i in item.tag.tag.split(',') if i]
    

    return render_template('detail.html', post=item, **data)


@app.route('/media/<value>', methods=['GET', 'POST'])
def media(value):
    # 文件类型筛选
    url = currenturl_add_args({'type': value})
    return redirect(url)


@app.route('/kw/<value>', methods=['GET', 'POST'])
def kwfunc(value):
    # 关键字筛选
    url = currenturl_add_args({'kw': value})
    url = url_remove_args(url, 'dir_num')
    return redirect(url)


@app.route('/sort/<value>', methods=['GET', 'POST'])
def sort(value):
    # 文件排序
    url = currenturl_add_args({'sort': value})
    return redirect(url)


@app.route('/log/<string:op>')
@app.route('/log/<int:id>/<string:op>')
def logs(op, id=''):
    # 置顶/删除记录 删除所有/除指定
    if id:
        log = db.session.query(VisitedPages).filter_by(id=id).first()
        if op == 'top':
            log.utime = datetime.utcnow()
            if log.is_top:
                log.is_top = False
            else:
                log.is_top = True
        else:
            db.session.delete(log)
    elif op == 'delall':
        logs = db.session.query(VisitedPages).all()
        [db.session.delete(i)for i in logs]
    elif op == 'del':
        logs = db.session.query(VisitedPages).filter(
            or_(VisitedPages.is_top == None, VisitedPages.is_top == False)).all()
        [db.session.delete(i)for i in logs]
    db.session.commit()
    return redirect(request.referrer)


@app.route('/log')
def show_logs():
    # 历史记录
    logs = db.session.query(VisitedPages).order_by(
        VisitedPages.is_top.desc(), VisitedPages.utime.desc()).all()
    index = count(1)
    # log拓展信息 相对时间-索引排序-参数名

    def f(i):
        i.vtime = get_relative_time(i.utime.timestamp())
        i.index = next(index)
        args = url_args(i.url)
        name = ''
        dir_num = args.get('dir_num')
        if dir_num:
            dir_obj = Dir.query.get(dir_num)
            if dir_obj:
                name = Path(dir_obj.path).name
                name = '路径:'+name
            elif dir_num == '-1':
                name = '路径:all'
        pn = args.get('pn')
        if pn and not pn == '1':
            name += 'pn:'+pn
        if args.get('kw'):
            name += ' 关键词:'+args.get('kw')
        i.name = name
        return i
    logs = [f(i) for i in logs]
    return render_template('logs.html', logs=logs)


@app.route('/keep')
def old_page():
    # 继续浏览
    last_url = db.session.query(VisitedPages).order_by(
        VisitedPages.utime.desc()).first()
    if last_url:
        return redirect(last_url.url)
    else:
        return redirect(request.referrer)


@app.route('/vue')
def func_vue():
    return render_template('vue.html', now=datetime.now())


last_play_id = '685CFDD4A467A5931585CB6CAF02CF414F76D34A'


def log_last_play(id):
    global last_play_id
    if id == '-1':
        return redirect('/detail/'+last_play_id)
    last_play_id = id
    return False


def rel_data(item):
    # 相关作品
    rel_num = 5
    all_files = []
    # 路径
    files = db.session.query(File).filter(File.dir == item.dir).order_by(
        func.random()).limit(rel_num).all()
    
    item.rel_items_path = items_vis(files, app)
    all_files += files
    # 同类型文件
    # max_file=File.query.order_by(File.size.desc()).limit(1).first()
    # # 最小为最大文件0.5
    # files= File.query.filter(File.type==item.type,File.size>max_file.size*0.5).order_by(func.random()).limit(rel_num).all()
    # # 最大为最大文件0.1
    # files+= File.query.filter(File.type==item.type,File.size<max_file.size*0.1).order_by(func.random()).limit(rel_num).all()
    type_base=File.query.filter(File.type == item.type)
    # 随机
    files = type_base.order_by(
        func.random()).limit(rel_num).all()
     
    item.rel_items_type = items_vis(files, app)
    all_files += files
    # 大小10%以内,5个
    ratio = 0.1
    for i in range(1, 10):
        ratio = i/10
        files = type_base.filter(File.size.between(
            item.size*(1-ratio), item.size*(1+ratio))).order_by(func.random()).limit(rel_num).all()
        if len(files) >= rel_num:
            break
    item.rel_items_size = items_vis(files, app)
    all_files += files
    item.rel_num = rel_num
    item.ratio = ratio

    item.kws = file_getkw(all_files)
    item.num = len(all_files)
    return item


@app.route('/shots', methods=['GET', 'POST'])
def shots():
    # 截图预览跳转
    per_page=int(request.args.get('num',10))
    pn=int(request.args.get('pn',1))
    start=per_page*(pn-1)
    ids = db.session.query(Shot.pid).filter_by(is_auto=0).group_by(Shot.pid).order_by(desc(func.max(Shot.ctime))).all()
    ids=[i.pid for i in ids[start:start+per_page]]
    files=File.query.join(Shot).filter(File.id.in_(ids)).order_by(case(value=File.id, whens={i: n for n, i in enumerate(ids)})).all()
   
     
    for file in files:
        for shot in file.shot:
            shot.vtime = format_second_time(shot.stime)
  
    files = items_vis(files, app)
    files.sort(key=lambda x: x.shot[0].ctime, reverse=True)
    cnt=count(start+1)
    for item in files:
        # 相对时间
        item.shots=list(filter(lambda x:x.is_auto==0,item.shot))
        item.vtime = get_relative_time(item.shots[0].ctime.timestamp())
        # 截图排序
        item.shots.sort(key=lambda x: x.stime)
        item.length = len(item.shots)
        # 项目索引
        item.index=next(cnt)

    if  request.args.get('part',False):
        return render_template('part_videoshots.html', posts=files)
    
    return render_template('shots.html', posts=files)


@app.route('/play/<id>')
def func_name(id):
    post = File.query.get(id)
    post = item_vis(post, app)
    return render_template('play.html', post=post)


@app.route('/add', methods=['GET', 'POST'])
@app.route('/add/<id>', methods=['GET', 'POST'])
def add_files(id=''):
    addform = AddDirForm()
    if id :
        if request.args.get('op')=='del':
            def f():
                r = InitData().scan_dir_isdel(id=id)
            back_work(f)
            flash('正在核对删除')
        if request.args.get('op')=='add':
            def f():
                InitData().scan_dir(id=id)
                create_small_file()
            back_work(f)
            flash('正在添加数据')
    
    if addform.validate_on_submit():
        if addform.isdelpath.data:
            def f():
                r = InitData().scan_dir_isdel(addform.isdelpath.data)
                print(f'标记删除:{r}')
            back_work(f)
            flash('正在核对删除')
        elif addform.addpath.data:
            d = addform.addpath.data+','
            paths = [i.strip() for i in d.split(',') if i]

            def f():
                InitData().scan_dir(paths)
                create_small_file()
            back_work(f)
            flash('正在添加数据')
    dirs=Dir.query.filter(Dir.add==True).all()
    return render_template('add.html', form=addform ,posts=dirs)


def files_info(files):
    # 遍历文件信息
    class DbDate:
        pass
    cnt = count(1)

    def f(i):
        t = DbDate()
        t.index = next(cnt)
        t.name = Path(i).name
        t.size = os.path.getsize(i)
        t.vsize = f'{t.size//1024**2}MB'
        return t
    posts = [f(i) for i in files]
    return posts


@app.route('/share', methods=['GET', 'POST'])
def share():
    form = UpFile()
    p = app.config.get('SAVE')
    dir_make(p)
    if form.validate_on_submit():
        # 获取所有file
        files = request.files.getlist('file')
        for file in files:
            file.save('{}/{}'.format(p, file.filename))

        return redirect(request.referrer)
    # 展示文件
    files = get_files(r'C:\Users\Zin\Documents\testdata\upload')
    data = {
        'now': datetime.now(),
        'form': form,
        'posts': files_info(files)
    }

    return render_template('share.html', **data)


def url_remove_args(url, kw):
    # url添加参数 页码归一
    # 旧数据提取
    kwargs = url_args(url)
    if kwargs.get(kw):
        kwargs.pop(kw)
    url = url_for('index', **kwargs)
    return url


def currenturl_add_args(kw):
    # url添加参数 页码归一
    # 旧数据提取
    kwargs = url_args(request.referrer)
    kwargs.update(kw)
    kwargs['pn'] = 1
    url = url_for('index', **kwargs)
    return url


if __name__ == '__main__':

    app.run(port=80, host='0.0.0.0', debug=False)
