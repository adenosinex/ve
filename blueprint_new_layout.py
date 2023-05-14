from flask import render_template,Blueprint,request,current_app
bp=Blueprint ('api_new',__name__)
bp.url_prefix='/new'
from models import *
from tools import *
 
p=Path(r'C:\Users\Zin\Documents\testdata\los')
dir_make(p)

@bp.route("/")  
def los_file( ):
    pn=int(request.args.get('pn',1))
    per_page=20
    r=File.query.filter(File.ctime!=None).paginate(page=pn,per_page=per_page)
    r.items=items_vis(r.items)
    kwargs_page=dict()
    data={ 
        'endpoint':'api_new.los_file',
        'kwargs_page':kwargs_page,
        'posts':r.items,  
        'pagination':r
    }
    return  render_template('new/index.html',**data)

def item_vis(item):
    # 数据数据添加列 更直观
    item.vsize=f'{item.size//1024**2}MiB'
    # 特定文件指定缩略图名
    if item.type=='video' or item.type=='img':
        # c=dbm.session.query(IdPath).filter_by(id=item.id).first()
        c=current_app.config['data'].get(item.id)
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
