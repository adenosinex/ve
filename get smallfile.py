from tools import *
def create_small_file( ):
        # 生成缺少的缩略图
        rp=r'C:\Users\Zin\Pictures\Saved Pictures\small file'
        db=Db_Mani('data_explorer.db')
        ids={Path(i).stem for i in get_files(rp)}
        r=db.query('select id,type,path from file where type="video" or type="img"')
        r=[i for i in r if not i[0] in ids]
        def f(i):
            id,type,path=i
            if type=='video':
                p=rp+'/{}.gif'.format(id)
                SmallFile().shot_gif( path,p )
            elif type=='img':
                p=rp+'/{}.jpg'.format(id)
                SmallFile().thumbnail( path,p)
              
        multi_threadpool(func=f,args=r,desc='生成缩略图jpg gif',pool_size=4 )

if __name__=='__main__':
    create_small_file()