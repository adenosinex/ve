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


if __name__=='__main__':
 
    create_small_file()
    index_file=r"C:\Users\Zin\Pictures\Saved Pictures\small file\index.cache"
    if os.path.exists(index_file):
        os.remove(index_file)
    # a=DyOld()
    # ren=create_small_file(a.get_oldgif)
    
   