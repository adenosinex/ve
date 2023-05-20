 
from flask import Blueprint ,current_app,Response,session,request,redirect,flash,url_for,jsonify,current_app,send_from_directory
 
api_bp=Blueprint ('api_bp',__name__)

from models import *
from tools import *

# 返回可跳转对象
def response_source(p):
    fileSize = os.path.getsize(p)
    f = open(p, 'rb')
    # try:
    target_time=request.range.ranges[0][0]
    content_range_header=request.range.to_content_range_header(fileSize)
    # except:
    #     target_time=0
    #     content_range_header=''
    f.seek(target_time)
    headers = {  
        'Accept-Range': 'bytes',
        'Content-Length': fileSize,
        'Content-Range': content_range_header
    }
    return (f, 206, headers)
# 文件
@api_bp.route("/share/<id>")  
def src_share_file(id):
    p=os.getenv('SAVE')+'/'+id
    if os.path.exists(p):
        return Response( open(p,'rb').read(),content_type='application/octet-stream')
    
# 单个媒体数据 
@api_bp.route("/file/<id>")  
def src_file(id):
    # id接受查询
    item=File.query.filter_by(id=id).first()
    if not item:
        return 'error'
    # 分类返回对象
    p=item.path

    if app.config.get('IS_PRO'):
        if item.file2:
            p=item.file2.path
        else:
            return 'not exists'
    if not os.path.exists(p):
        return 'not exists'
    # 下载直接读取返回
    if request.args.get('down'):
        return Response( open(p,'rb').read(),content_type='application/octet-stream')

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
            return jsonify({'status':'ok'})
        else:
            r=item.set_tag(tag)
            if tag=='del':
                db_query_data.cache_clear()
            return jsonify({'status':'ok'})
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

# 测试当前时间
@api_bp.route('/now')
def api_now( ):
    r={
        'now':datetime.now()
    }
    return jsonify(r)