from flask import render_template,Blueprint,request
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
    
    kwargs_page=dict()
    data={
        'endpoint':'api_new.los_file',
        'kwargs_page':kwargs_page,
        'posts':r.items,
        'pagination':r
    }
    return  render_template('new/index.html',**data)

 