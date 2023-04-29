from datetime import datetime, timedelta
from itertools import count
from tools import *
class DyOld:
    def __init__(self) -> None:
        p=r"D:\备份 万一\dy root\video\jpg"
        self.dst=Path(r"D:\备份 万一\dy root\video\view")
        dir_make(self.dst)
        self.ids={Path(i).stem:i for i in get_files(p)}

    def get_oldgif(self,id,type,p):
        t=Path(p).stem
        gif_file=self.ids.get(t)
        if gif_file:
            r=[gif_file,self.dst.joinpath(f'{id}.jpg')]
            os.link(*r)
            return r

def create_small_file( func='',max=2820):
        # 生成缺少的缩略图 函数自定义处理，返回真值掩盖默认操作 
        smallfile_path=r'C:\Users\Zin\Pictures\Saved Pictures\small file'
        db=Db_Mani('data_explorer.db')
        already_ids={Path(i).stem for i in get_files(smallfile_path)}
        current_datetime =  datetime.now()

        # 计算三天前的日期时间
        three_days_ago = current_datetime -  timedelta(days=3)
        data_db=db.query('select id,type,path from file where (type="video" or type="img") and utime>"{}" '.format(three_days_ago))
        data_db=[i for i in data_db if not i[0] in already_ids]
        cnt=count()
        def f(i):
            id,type,path=i
            if next(cnt)>max:
                return
            if func :
                r=func(id,type,path)
                if r:
                    return r
            if    type=='img':
                p=smallfile_path+'/{}.jpg'.format(id)
                SmallFile().thumbnail( path,p)
            elif type=='video':
                p=smallfile_path+'/{}.jpg'.format(id)
                SmallFile().shot_jpg( path,p ) 
              
        ret=multi_threadpool(func=f,args=data_db,desc='生成缩略图jpg gif',pool_size=1 )
        ret=[i for i in ret if i]
        return ret

if __name__=='__main__':
    p=r"C:\Users\Zin\Documents\testdata\mixdata\like hd -video\b.mp4"
    d=Path(p).with_name('1.jpg')
    t=r'D:\真子集\shuffle size-70 无码\千野核桃 17-02-24 HEYZO-1412 【血之核桃】陆续生中~秋叶系美女来袭!~.mp4'
    p='a.jpg' 
    # SmallFile().shot_jpg( t,p ) 
    # SmallFile().shot_jpg(p,d)
    create_small_file()
    # a=DyOld()
    # ren=create_small_file(a.get_oldgif)
   