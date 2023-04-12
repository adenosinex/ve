from flask import render_template,Blueprint
bp=Blueprint ('api_new',__name__)
bp.url_prefix='/new'
from models import *
from tools import *

p=Path(r'C:\Users\Zin\Documents\testdata\los')
dir_make(p)

@bp.route("/")  
def los_file( ):
    pn=1
    per_page=20
    r=File.query.paginate(page=pn,per_page=per_page)
    data={
        'posts':r.items
    }
    return  render_template('new/index.html',**data)

 