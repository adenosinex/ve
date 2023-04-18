
// import axios from 'js/axios.min.js'

  

// 设置媒体属性

// 获取id正则 获取下一个id
let ReId = /[A-Z\d]{40}/

let medias = [];
let tagAttr = {
    'video': { 'width': '100%', 'controls': 'true', 'autoplay': 'true' },
    'audio': { 'controls': 'true', 'loop': '' },
    // 'img': { 'width': '100%' }
}


for (let tag of Object.entries(tagAttr)) {
    console.log(tag)
    tags = document.querySelectorAll(tag[0])
    medias = medias.concat(tags)
    setAttr(tags, tag[1])
}
function setAttr(nodes, attr) {
    nodes.forEach((node, index) =>
        Array.from(Object.entries(attr)).forEach((key, index) => node.setAttribute(key[0], key[1]))
    )
}
// 滚轮放大图片
class ZoomableImage {
    constructor(selector) {
      // 获取图片元素
      this.imageEl = document.querySelector(selector);
      
      // 初始放大倍数，可根据实际需求调整
      this.scale = 1.0;
      
      // 箭头函数中使用当前 this 对象
      // 鼠标滚轮事件监听器
      this.imageEl.addEventListener('wheel', (e) => {
        e.preventDefault(); //禁止默认行为
        if (e.deltaY < 0) { // 滚轮向上滚动，放大图片
          this.zoomIn();
        } else { // 滚轮向下滚动，缩小图片
          this.zoomOut();
        }
      });
    }
  
    // 放大图片函数
    zoomIn() {
      this.scale += 0.1; // 调整缩放倍数
      this.imageEl.style.transform = `scale(${this.scale})`; // 设置 transform 属性来缩放图片
    }
  
    // 缩小图片函数
    zoomOut() {
      this.scale -= 0.1; // 调整缩放倍数
      this.imageEl.style.transform = `scale(${this.scale})`; // 设置 transform 属性来缩放图片
    }
  }
//   拖动图片
//   class DraggableImage {
//     constructor(selector) {
//       // 获取图片元素
//       this.imageEl = document.querySelector(selector);
  
//       // 鼠标监听状态标识
//       this.isDown = false;
    
//       // 初始偏移量和位置
//       this.offsetX = 0;
//       this.offsetY = 0;
//       this.positionX = 0;
//       this.positionY = 0;
  
//       // 监听鼠标按下事件
//       this.imageEl.addEventListener('mousedown', this.handleMouseDown.bind(this));
      
//       // 监听鼠标移动事件
//       this.imageEl.addEventListener('mousemove', this.handleMouseMove.bind(this));
  
//       // 监听鼠标松开事件，重置鼠标状态
//       this.imageEl.addEventListener('mouseup', this.handleMouseUp.bind(this)); 
//     }
  
//     // 监听鼠标按下事件的处理函数
//     handleMouseDown(e) {
//       e.preventDefault(); // 禁止默认行为
      
//       this.isDown = true; // 标记鼠标状态
//       this.offsetX = e.clientX - this.imageEl.offsetLeft; // 记录鼠标与图片的水平偏移量
//       this.offsetY = e.clientY - this.imageEl.offsetTop; // 记录鼠标与图片的垂直偏移量
//     }
    
//     // 监听鼠标移动事件的处理函数
//     handleMouseMove(e) {
//       // 如果鼠标没有被按下则返回
//       if (!this.isDown) return;
      
//       // 计算图片的新位置
//       this.positionX = e.clientX - this.offsetX;
//       this.positionY = e.clientY - this.offsetY;
      
//       // 设置 transform 属性来移动图片
//       this.imageEl.style.transform = `translate(${this.positionX}px, ${this.positionY}px)`;
//     }
    
//     // 监听鼠标松开事件的处理函数
//     handleMouseUp( ) {
         
//       this.isDown = false; // 重置鼠标状态
//       this.offsetX = 0;
//       this.offsetY = 0;
//     }
//   }
class DraggableImage {
    constructor(selector) {
      // 获取图片元素
      this.imageEl = document.querySelector(selector);
  
      // 鼠标监听状态标识
      this.isDown = false;
  
      // 初始偏移量和位置
      this.offsetX = 0;
      this.offsetY = 0;
      this.positionX = 0;
      this.positionY = 0;
  
      // 监听鼠标按下事件
      this.imageEl.addEventListener('mousedown', this.handleMouseDown.bind(this));
  
      // 监听鼠标松开事件，重置鼠标状态
      document.addEventListener('mouseup', this.handleMouseUp.bind(this));
      
      // 监听整个文档上的鼠标移动事件
      document.addEventListener('mousemove', this.handleMouseMove.bind(this));
      
      // 监听窗口大小变化事件，并更新最大可移动范围
      window.addEventListener('resize', this.updateMaxRange.bind(this));
      
      // 更新最大可移动范围
      this.updateMaxRange();
    }
  
    // 监听鼠标按下事件的处理函数
    handleMouseDown(e) {
      e.preventDefault(); // 禁止默认行为
  
      this.isDown = true; // 标记鼠标状态
      this.offsetX = e.clientX - this.imageEl.offsetLeft; // 记录鼠标与图片的水平偏移量
      this.offsetY = e.clientY - this.imageEl.offsetTop; // 记录鼠标与图片的垂直偏移量
    }
  
    // 监听鼠标松开事件的处理函数
    handleMouseUp() {
      this.isDown = false; // 重置鼠标状态
    }
    
    // 监听鼠标移动事件的处理函数
    handleMouseMove(e) {
      // 如果鼠标没有被按下则返回
      if (!this.isDown) return;
  
      // 计算图片的新位置
      this.positionX = e.clientX - this.offsetX;
      this.positionY = e.clientY - this.offsetY;
  
      // 判断图片是否还能继续向右移动
      if (this.positionX > this.maxX) {
        this.positionX = this.maxX;
      }
  
      // 判断图片是否还能继续向左移动
      if (this.positionX < 0) {
        this.positionX = 0;
      }
  
      // 判断图片是否还能继续向下移动
      if (this.positionY > this.maxY) {
        this.positionY = this.maxY;
      }
  
      // 判断图片是否还能继续向上移动
      if (this.positionY < 0) {
        this.positionY = 0;
      }
  
      // 设置 transform 属性来移动图片
      this.imageEl.style.transform = `translate(${this.positionX}px, ${this.positionY}px)`;
    }
    
    // 更新最大可移动范围
    updateMaxRange() {
      const bodyRect = document.body.getBoundingClientRect();
      const imageRect = this.imageEl.getBoundingClientRect();
      this.maxX = bodyRect.width - imageRect.width;
      this.maxY = bodyRect.height - imageRect.height;
    }
  }
 
 
  
// 弹出显示图片 需要占位
// <!-- 弹出图片 -->
/* <div id="fullscreen-container"   >
    <img id="fullscreen-image">
  </div> */
class showImg {
    constructor() {
        // this.container = document.getElementById('fullscreen-container');
        // this.image = document.getElementById('fullscreen-image');
        this.container = document.createElement('div')
        this.container.id = "fullscreen-container"
        this.image = document.createElement('img')
        this.image.id = "fullscreen-image"
        this.container.appendChild(this.image)
        document.body.appendChild(this.container)
          // 使用方式
        const imagez = new ZoomableImage('#fullscreen-image');
        // const image = new DraggableImage('#fullscreen-image');
       

    }
    showFullscreen(imageSrc) {
       
        // 将全屏容器设为显示状态，并设置图片资源地址和属性
        this.container.style.display = 'flex';
        this.image.setAttribute('src', imageSrc);
        this.image.style.opacity = 1;

        // 禁用滚动条、页面滑动等
        document.body.style.overflow = 'hidden';

        // 设置点击全屏图像退出全屏事件监听器
        let that = this
        this.container.addEventListener('click', function (e) {
            that.closeFullscreen();
            
        });

        // 设置 ESC 键退出全屏模式
        document.addEventListener('keyup', (event) => {
            if (event.key === 27)
                that.closeFullscreen();
                }
        );

        // 点击图片不管
        this.image.addEventListener('click', (e) => e.stopPropagation());
    }

    closeFullscreen() {
        // 隐藏全屏容器，并清除相应的事件监听器
        this.container.style.display = 'none';
        document.body.style.overflow = '';
        let that = this
        this.image.removeEventListener('click', function () {
            that.closeFullscreen();
        });
        document.removeEventListener('keyup', (event) => {
            if (event.key === 27)
                that.closeFullscreen();
                });
    }


}

  
// 预览节点 点击详情
let previews = document.querySelectorAll('.preview')
// 点击弹出查看图片查看
let imgshow = new showImg()
previews.forEach((node) => {
    // node.addEventListener('click', (event) => {
    let img = node.querySelector('img')
    if (img)
        img.addEventListener('click', function () {
            // 图片放大 视频查看详情
            if(img.src.includes('jpg'))
            imgshow.showFullscreen('/file/' + node.dataset.id);
            else
            location.href='/detail/'+ReId.exec(img.src)
        });
    // })


})




// // 本地存储预览id
let previewsList, previewsDict={} ,previewsDictName,previewsDictLink;
if (previews.length > 5) {
    // id api 字典
    previewsDictName = {};
    previewsDictLink = {};
    previewsList = new Array();
    previews.forEach (  (node) => {
        let id = node.dataset.id;
        previewsDictLink[id] = '/detail/' + id
        previewsDictName[id] = node.dataset.name
        previewsList.push(id)
    })
    previewsDict['index'] = previewsList
    previewsDict['name'] = previewsDictName
    previewsDict['link'] = previewsDictLink
    localStorage.setItem('preLink', JSON.stringify(previewsDict ))
}
else {
    previewsDict  = JSON.parse(localStorage.getItem('preLink'));
    if (previewsDict ){
        previewsList = previewsDict ['index']
        previewsDictName = previewsDict ['name']
        previewsDictLink = previewsDict ['link']
    }

}



// 详情页三击 下一页
nclickEvent(3, document, (e) => {
    let b = location.href.split('/')
    let id = b[b.length - 1]
    let index = previewsList.indexOf(id)

    if (id && location.pathname.includes('detail')) {
        let clickY = e.clientY
        let mediaY;
        let rect;
        for (let i = 0; i < medias.length; i++) {
            try {
                rect = medias[i][0].getBoundingClientRect()
                mediaY = rect.y
                break
            }
            catch {

            }
        }
        let plus
        let half = rect.height / 2
        if (clickY > mediaY + half)
            plus = -1
        else if (clickY < mediaY - half)
            plus = 1
        else
            return
        index = index + plus
        if (index === previewsList.length)
            index = 0
        else if (index === -1)
            index = previewsList.length - 1

        let url = previewsDictLink[previewsList[index]]
        let id = previewsList[index]
        window.location.href = url
    }
})


// 获取指定位置id 超范围自动循环
function previewsSecureId(index) {
    if (index === previewsList.length)
        index = 0
    else if (index === -1)
        index = previewsList.length - 1
    return previewsList[index]
}

// axios part
// a链接后台发送 变色 点击红 成功绿 失败白
function clickAWithColor(node, funcSuccess = (response) => true) {
    node.addEventListener('click', (event) => {
        event.preventDefault()
        event.stopPropagation()

        node.style.backgroundColor = 'red'
        axios.get(node.href)
            .then(function (response) {
                if (funcSuccess(response.data))
                    node.style.backgroundColor = 'green'
                else
                node.style.backgroundColor = 'white'
            })
            .catch(function (error) {
                node.style.backgroundColor = 'white'
            })
    }
    )
}
// 获取触摸滑动角度
class SwipeHandler {
    constructor() {
        this.startx = 0;
        this.starty = 0;
        this.stime = 0;
        this.nowr;

        document.addEventListener("touchstart", e => {
            this.handleTouchStart(e);
        }, false);

        document.addEventListener("touchend", e => {
            this.handleTouchEnd(e);
        }, false);
    }

    //获得角度
    getAngle(angx, angy) {
        return Math.atan2(angy, angx) * 180 / Math.PI;
    }

    //根据起点终点返回方向 1向上滑动 2向下滑动 3向左滑动 4向右滑动 0点击事件
    getDirection(startx, starty, endx, endy) {
        let angx = endx - startx;
        let angy = endy - starty;
        let result = 0;

        //如果滑动距离太短
        if (Math.abs(angx) < 2 && Math.abs(angy) < 2) {
            return result;
        }

        let angle = this.getAngle(angx, angy);
        if (angle >= -135 && angle <= -45) {
            // 下
            result = 'down';
        } else if (angle > 45 && angle < 135) {
            // 上
            result = 'up';
        } else if ((angle >= 135 && angle <= 180) || (angle >= -180 && angle < -135)) {
            // 左
            result = 3;
        } else if (angle >= -45 && angle <= 45) {
            // 右
            result = 4;

        }
        return result;
    }

    handleTouchStart(e) {
        this.startx = e.touches[0].pageX;
        this.starty = e.touches[0].pageY;
        this.stime = new Date().getTime();
    }

    handleTouchEnd(e) {
        let endx, endy, now;
        endx = e.changedTouches[0].pageX;
        endy = e.changedTouches[0].pageY;
        now = new Date().getTime();
        let direction = this.getDirection(this.startx, this.starty, endx, endy);

        let disY = Math.round(Math.abs(endy - this.starty))
        let sptime = now - this.stime
        // alert(disY+' time:'+sptime)

        if (sptime > 300 || disY < 150)
            this.nowr = ''
        else
            this.nowr = direction
        console.log(direction)
        return direction
    }

    now() {
        return this.nowr
    }
}
// 鼠标点击滑动
class MouseDragDirectionTracker {
  constructor() {
    this.startX = 0;
    this.startY = 0;
    this.endX = 0;
    this.endY = 0;

    // 监听整个文档上的鼠标按下事件
    document.addEventListener('mousedown', this.handleMouseDown.bind(this));
    // 监听整个文档上的鼠标移动事件
    document.addEventListener('mousemove', this.handleMouseMove.bind(this));
    // 监听整个文档上的鼠标松开事件
    document.addEventListener('mouseup', this.handleMouseUp.bind(this));
  }

  // 监听鼠标按下事件的处理函数
  handleMouseDown(e) {
    // 记录初始鼠标位置
    this.startX = e.clientX;
    this.startY = e.clientY;
  }

  // 监听鼠标移动事件的处理函数
  handleMouseMove(e) {
    if (this.startX === 0 && this.startY === 0) {
      return;
    }

    // 记录最终鼠标位置
    this.endX = e.clientX;
    this.endY = e.clientY;
    this.move=true
  }

  // 监听鼠标松开事件的处理函数
  handleMouseUp() {
    const deltaX = this.endX - this.startX;
    const deltaY = this.endY - this.startY;
    // 没有移动或者移动过短跳过
     if(!this.move||(Math.abs(deltaX)<5 &&Math.abs(deltaY)<5)){
        this.direction='no'
        this.restoreValue()
        this.move=false
         return 
        }
    this.move=false
    if (Math.abs(deltaX) > Math.abs(deltaY)) {    // 水平方向移动更大
      if (deltaX > 0) {
        console.log("向右滑动");
       
      } else {
        console.log("向左滑动");
      }
    } else {    // 垂直方向移动更大
      if (deltaY > 0) {
          console.log("向上滑动");
          this.direction='up'
        } else {
            console.log("向下滑动");
            this.direction='down'
        }
    }

   this.restoreValue()
  }
  restoreValue(){
     // 重置鼠标初始和最终位置信息
    this.startX = 0;
    this.startY = 0;
    this.endX = 0;
    this.endY = 0;
  }
  getDirection(){
    return  this.direction;
  }
}

// 收藏网址
let toplog=document.querySelector('.toplog')
if (toplog){
    clickAWithColor(toplog,(res)=>res.includes('success'))
    // 查看收藏状态
    toplog.click()
    toplog.click()
}


//   播放页滑动播放
if (location.pathname.includes('play')) {
    // 获取id
    // 获取文件自动播放 设置id
    let file = $('#play').children()[0]
    let tagname = file.tagName
    if (tagname === 'VIDEO' || tagname === 'AUDIO')
        file.play()
     // 高度为一屏幕
    file.height = window.innerHeight;

    let id = ReId.exec(file.src)[0]
    // 提供链接
    let target = document.createElement('a')
    target.href = '/detail/' + id
    let btn = document.createElement('button')
    btn.textContent = '详情'
    btn.className = "btn btn-large btn-primary"
    target.appendChild(btn)

    let insertObj = $('#play')[0]
    insertObj.insertBefore(target, insertObj.children[0])



    // 停止默认滑动效果
    document.body.addEventListener('touchmove', function (e) {
        e.preventDefault();
    }, { passive: false });

    // 选项决定切换
    function swithchhandler(direction){
        id = ReId.exec(file.src)[0]
        let index = previewsList.indexOf(id)
        pid = previewsSecureId(index - 1)
        nid = previewsSecureId(index + 1)

        switch (direction) {
            case 'down':
                id = nid
                break;
            case 'up':
                id = pid
                break;
            default:
                return
        }
        file.src = '/file/' + id
        file.scrollIntoView()
        target.href = '/detail/' + id
        newUrl = window.location.origin + '/play/' + id
        history.pushState('', '', newUrl);
        document.title= previewsDictName[previewsList[index]]
    }
    // 自动下一个
    file.addEventListener('ended', () => { swithchhandler('down') })
    // 点击播放
    // file.addEventListener('click',()=>{
    //     if(file.paused)
    //     file.play()
    //     else
    //     file.pause()
    // })
    //手指离开屏幕
    const swipeHandler = new SwipeHandler(); // 创建一个滑动事件处理类的实例对象
    document.addEventListener("touchend", function (e) {
        let direction = swipeHandler.now();
        swithchhandler(direction)

    }, false);
    // 滑动结束
    const mouseDragDirectionTracker = new MouseDragDirectionTracker();
     document.addEventListener('mouseup', ()=>{
        let direction=mouseDragDirectionTracker.getDirection()
        swithchhandler(direction)

     });

}
// 鼠标在视频上延迟隐藏
var timer;
var tagObj = $('video')
tagObj.mousemove(function () {
    tagObj.css({
        cursor: ''
    });
    timer = setTimeout(function () {

        tagObj.css({
            cursor: 'none'
        });
    }, 2000)
});
//   详情页设置添加下一个跳转
if (location.pathname.includes('detail')) {
    // 获取文件自动播放 设置id
    let file = $('.file').children()[0]
    let tagname = file.tagName
    if (tagname === 'VIDEO' || tagname === 'AUDIO')
        file.play()
    file.setAttribute('id', 'play')
    // 高度为一屏幕
    file.height = window.innerHeight;
    // 获取id
    let id = ReId.exec(location.href)[0]
    let index = previewsList.indexOf(id)

    // 链接
    pid = previewsSecureId(index - 1)
    nid = previewsSecureId(index + 1)
    nlink = '/detail/' + nid
    plink = '/detail/' + pid
    // 创建链接
    function createLink(text, link, class_add = '') {
        let next = document.createElement('a')
        next.href = link
        let btn = document.createElement('button')
        btn.textContent = text
        btn.className = "btn btn-large btn-primary " + class_add
        next.appendChild(btn)
        return next
    }
    // 链接嵌套按钮
    let container = document.createElement('div')
    let next = createLink('下一个', nlink,'next')

    // 播放完自动下一个
    if (tagname === 'VIDEO' || tagname === 'AUDIO')
        file.addEventListener('ended', () => { next.click() })

    let prev = createLink('上一个', plink, 'pull-right prev')

    let tip = document.createElement('span')
    tip.textContent = index

    let play = createLink('play', '/play/' + id)
    container.appendChild(tip)
    container.appendChild(next)
    container.appendChild(play)
    container.appendChild(prev)

    let insertObj = document.querySelector('.info')
    insertObj.insertBefore(container, insertObj.children[0])

    // 定位到文件
    let locida = document.createElement('a')
    locida.href = '#play'
    locida.click()


    // 键盘控制下一个
    document.addEventListener('keydown', (e) => {
        switch (e.key) {
            case 'ArrowLeft':
                prev.click()
                break;
            case 'ArrowRight':
                next.click()
        }
    })
    // 左右点击下一个
    // document.documentElement.clientWidth
   document.addEventListener('click', (e) => {
        let clickx = e.screenX
        if (clickx < 200 && pid)
        prev.click()
        if (clickx > 1300 && nid)
        next.click()
    })
    // 双击下一个
    nclickEvent(2, file, () => {
        next.click()
    })
    nclickEvent(2, file, () => {
        prev.click()
    })


    // 添加tag链接不跳转
    $('a.tag').each((index, node) => {
        clickAWithColor(node)
    })
    // 标题加索引
    document.title = index + 1 + ' ' + document.title
}


// 输入关键词跳转新搜索页面 当前链接后加参数 去旧参数
// 表单
let formInput = document.querySelector('#search');
if (formInput) {
    // 请求参数写入表单
    document.addEventListener('DOMContentLoaded', () => {
        let r = argsGet()
        if (r.kw) {
            formInput.value = r.kw
        }
    })
    // 打字结束自动到搜索搜索
    formInput.addEventListener("compositionend", () => location.href = '/?kw=' + formInput.value);
}


// 获取网址参数
function argsGet(url) {
    if (!url)
        url = location.search
    if (url.includes('?'))
        url = url.split('?')[1]
    const urlSearchParams = new URLSearchParams(url)
    const result = Object.fromEntries(urlSearchParams.entries())
    return result
}



// 按钮 喜欢操作 get请求
let likeELements = document.querySelectorAll(".sendLike");
clickAWithColor
likeELements.forEach((node) => {
    clickAWithColor(node)
})



//  导航链接激活高亮a 加active 如果href在当前url中
let pname = location.pathname
$('a.nav-link').each((index, node) => {
    if (pname === node.pathname)
        node.classList.add('active')
    else if (node.classList.contains('active'))
        node.classList.remove("active");
})



// 对象绑定 多击事件
function nclickEvent(n, dom, fn) {
    dom.removeEventListener('dblclick', null);
    var n = parseInt(n) < 1 ? 1 : parseInt(n),
        count = 0,
        lastTime = 0;//用于记录上次结束的时间
    var handler = function (event) {
        var currentTime = new Date().getTime();//获取本次点击的时间
        count = (currentTime - lastTime) < 300 ? count + 1 : 0;//如果本次点击的时间和上次结束时间相比大于300毫秒就把count置0
        lastTime = new Date().getTime();
        if (count >= n - 1) {
            fn(event);
            count = 0;
        }
    };
    dom.addEventListener('click', handler);
}


// url转换 局部
function urlGet(node) {
    // /media?page=2&type=video
    // /api/json/video
    let paras = argsGet(node.search)
    let url = '/api/json/' + paras.type;
    let t = 'type=' + paras.type
    url += node.search.replace(t, '')
    return url

}



// 音频链接
let musics = document.querySelectorAll('audio')
let musicSrcs = []
let musicSrcNode = {}
for (let i = 0; i < musics.length; i++) {
    musicSrcs[i] = musics[i].src
    musicSrcNode[musics[i].src] = musics[i]
}
// 添加音乐播放器
if (musics.length > 0) {
    let container = document.createElement('div')

    let display_audio = document.createElement('audio')
    display_audio.src = musics[0].src
    display_audio.setAttribute('controls', true)

    let playNext = document.createElement('button')
    playNext.textContent = '下一首'
    let downAll = document.createElement('button')
    downAll.textContent = '下载所有'

    let tipNow = document.createElement('span')
    tipNow.textContent = '1.正在播放 ' + musics[0].dataset.desc

    container.appendChild(display_audio)
    container.appendChild(playNext)
    container.appendChild(downAll)
    container.appendChild(tipNow)
    let insertObj = document.querySelector('.post-tabs')
    insertObj.insertBefore(container, insertObj.children[0])
    // row.insertBefore(audio,row.children[0])

    function PlayAudio(node) {
        display_audio.src = node.src
        let index = musicSrcs.indexOf(display_audio.src)
        tipNow.textContent = index + ':' + node.dataset.desc
        document.title = index + ':' + node.dataset.desc
        display_audio.play()
    }
    //   点击项目播放
    musics.forEach((node) => {
        $(node.parentNode).click(() => {
            PlayAudio(node)
        })
    })
    // 获取当前item
    function nowItem() {
        let index = musicSrcs.indexOf(display_audio.src)
        return musicSrcNode[musicSrcs[index]].parentElement.parentElement
    }
    //   播放下一首
    playNext.addEventListener('click', (e) => {
        let index = musicSrcs.indexOf(display_audio.src)
        index = index + 1
        if (index === musicSrcs.length)
            index = 0
        PlayAudio(musicSrcNode[musicSrcs[index]])

    })
    // 自动下一首
    display_audio.addEventListener('ended', () => {
        playNext.click()
    })
    // 点击定位元素
    tipNow.addEventListener('click', () => {
        let node = nowItem()
        node.scrollIntoView({ behavior: 'auto' })
        node.style.backgroundColor = 'red'
    })

    //   下载所有
    $(downAll).click(() => {
        alert('下载所有')
        musics.forEach((node) => {
            var name = node.dataset.desc
            var src = window.location.origin + node.getAttribute('src')
            downloadfile(src, name)
            //  this.downloadMp3('/api/musics?music_id=1',name);

        })
    })
}


function downloadfile(url, name) {
    fetch(url).then(res => res.blob()).then(blob => {
        const a = document.createElement('a');
        document.body.appendChild(a)
        a.style.display = 'none'
        const url = window.URL.createObjectURL(blob);
        a.href = url;
        a.download = name;
        a.click();
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url);
    });
}