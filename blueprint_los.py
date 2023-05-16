from flask import Blueprint ,current_app,Response,session,request,redirect,flash,url_for,jsonify,current_app,send_from_directory
bp=Blueprint ('api_los',__name__)
bp.url_prefix='/los'
from models import *
from tools import *
# 测试 对象存储
file=Path(r'C:\Users\Zin\Documents\testdata\los')
dir_make(file)

@bp.route("/<path:path_param>")  
def los_file(path_param):
    file=file.joinpath(path_param)
    if file.exists():
        return Response( open(file,'rb').read(),content_type='application/octet-stream')
    return ''


@bp.route('/list' )
def list( ):
    l=len(str(file))
    def f(i):
        data={
            'key':Path(i).name,
            'abs':i[l+1:].replace('\\','/')
        }
        return data
    items=[f(i) for i in get_files(file)]
    return jsonify({'keys':items})
    
@bp.route('/up',methods=[ 'POST'])
@bp.route('/up/<path:path_param>',methods=[ 'POST'])
def up_los(path_param='' ):
    file = request.files['file']
    
    if path_param:
        dst=file.joinpath(path_param,file.filename)
        dir_make(dst.parent)
    else:
        dst=file.joinpath(file.filename)
    file.save(dst)
    return jsonify({'op':'add'})