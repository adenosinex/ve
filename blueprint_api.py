 
from flask import Blueprint,send_file ,current_app,Response,session,request,redirect,flash,url_for,jsonify,current_app,send_from_directory
 
api_bp=Blueprint ('api_bp',__name__)

from models import *
from tools import *

# 返回可跳转对象
def response_source(p):
    fileSize = os.path.getsize(p)
    f = open(p, 'rb')
    try:
        target_time=request.range.ranges[0][0]
        content_range_header=request.range.to_content_range_header(fileSize)
    except:
        target_time=0
        content_range_header=''
    f.seek(target_time)
    headers = {  
        'Accept-Range': 'bytes',
        'Content-Length': fileSize,
        'Content-Range': content_range_header
    }
    return (f, 206, headers)

def img_res(p):
    with open(p, 'rb') as f: 	
        image = f.read()
        return Response(image, mimetype="image/png")
# 文件
@api_bp.route("/share/<id>")  
def src_share_file(id):
    p=os.getenv('SAVE')+'/'+id
    if os.path.exists(p):
        return Response( open(p,'rb').read(),content_type='application/octet-stream')
    return abort(404)
    
# 预览数据
@api_bp.route("/thumb/<ids>")  
def previews_file(ids):
    r=app.config['preview_data'].get(ids)
    if r:
        with open(r, 'rb') as f: 	
            image = f.read()
            return Response(image, mimetype="image/png")
    
# 单个媒体数据 
@api_bp.route("/file/<id>")  
def src_file(id):
    # id接受查询
    item=File.query.filter_by(id=id).first()
    if not item:
        return 'error 不存在'
    # 分类返回对象
    p=item.path
    # 下载直接读取返回
    if request.args.get('down'):
        return send_file(p, as_attachment=True, attachment_filename=Path(p).name)

    if not os.path.exists(p):
        return 'not exists'
 
    if item.type=='video':
        args=response_source(p)
        return Response(*args,content_type='video/mp4')

    elif item.type=='music':
        args=response_source(p)
        return Response(*args,content_type='audio/mpeg')

    elif item.type=='img':
        with open(p, 'rb') as f: 	
            image = f.read()
            return Response(image, mimetype="image/png")


# 置顶网址 
@api_bp.route("/toplog")  
def log_web( ):
    url=request.referrer
    log=db.session.query(VisitedPages).filter_by(url=url).first()
    if log:
        if log.is_top:
            log.is_top=None
            mes='concel'
        else:
            log.is_top=True
            mes='success'
    else:
        log=VisitedPages(url=url,is_top=True)
        mes='success add'
    db.session.add(log)
    db.session.commit()
    return mes

# 标记文件 
@api_bp.route("/tag/<id>")  
def tag_file(id):
    # id标记文件
    tag=request.args.get('tag')
    try:
        pre=re.findall('\d+-',tag)[0]
        tag=tag.replace(pre,'')
    except:
        pass
    item=File.query.filter_by(id=id).first()
    if item:
        if tag=='like':
            r=item.set_like()
            if r:
                mes='success set'
            else:
                mes='success cancel'
            return jsonify({'status':mes})
        else:
            r=item.set_tag(tag)
            if tag=='del':
                db_query_data.cache_clear()
            if r:
                mes='success set'
            else:
                mes='success cancel'
            return jsonify({'status':mes})
           
    return redirect(request.referrer)

# 字幕srt->vtt返回
@api_bp.route('/subtitles/<id>')
def func_name(id):
    r=File.query.get(id)
    srt=Path(r.path ).with_suffix('.srt')
    if srt.exists():
        r=Response(srt2vtt(srt), mimetype='text/vtt')
        return r
    return 'null'


# 视频截图
@api_bp.route('/shotset/<id>')
def func_name213(id):
    # try:
    dst=dst=current_app.config.get('SHOTS')
    stime=request.args.get('time')
    video_path,img_path, time_start=get_video_shotset(id,stime,dst)
    # except:
    #     return jsonify({'status':'error'})
    if video_path.exists():
        st=time.time()
        r=VideoM().get_img2(video_path,img_path, time_start)
        if r:
            InitData().add_file(img_path)
            db.session.commit()
            Shot.add(img_path,id,time_start)
            print(img_path,spend_time(st))
            return jsonify({'status':'success set'})
    return jsonify({'status':'error video not exist'})

 
 

# 测试当前时间
@api_bp.route('/partHtml')
def api_part( ):
    if request.args.get('part') == 'dataInfo':
        num_data,num_shot,num_autoshot=File.query.count(),Shot.query.filter_by(is_auto=False).count(),Shot.query.filter_by(is_auto=True).count()
        s=f'全部数据：{num_data} 截图数：{num_shot} 预览图数：{num_autoshot}'
        num_deldata,num_notexist =File.query.join(Tag,File.id==Tag.id).filter(Tag.tag=='del').count(),File.query.filter(File.path.startswith('del')).count() 
        s2=f'\n标记删除：{num_deldata} 移除文件：{num_notexist}'
        return s+s2
    
# 测试当前时间
@api_bp.route('/now')
def api_now( ):
    r={
        'now':datetime.now()
    }
    return jsonify(r)