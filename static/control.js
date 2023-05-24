
// import axios from 'js/axios.min.js'



// 设置媒体属性

// 获取id正则 获取下一个id
let ReId = /[A-Z\d]{40}/
function getId(s){
    try {
        
        return ReId.exec(s)[0]
    } catch (error) {
        return 0
    }
}
let medias = [];
let tagAttr = {
    'video': { 'controls': 'true', 'autoplay': 'true' },
    'audio': { 'controls': 'true', 'loop': '' },
    // 'img': { 'width': '100%' }
}

// 设置属性
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
// 获取下一页链接
function getNextPageUrl() {
    return getOtherPageUrl((n)=>n+1)
}
// 获取上一页链接
function getPrevPageUrl() {
    return getOtherPageUrl((n)=>{
        if (n===1)
        return 1
        else
        return n-1
    })
}
// 获取其他页面链接
function getOtherPageUrl(calPn) {
    var urlParams = new URLSearchParams(window.location.search);
    var pn = parseInt(urlParams.get("pn")) || 1; // 如果没有 pn 参数，则默认为 1
    var nextPagePn = calPn(pn );
    var baseUrl = window.location.href.split("?")[0]; // 获取当前 URL 的基础部分（即问号之前的部分）
    var queryParams = new URLSearchParams(window.location.search); // 复制现有的查询参数
    queryParams.set("pn", nextPagePn); // 更新 pn 值
  
    return baseUrl + "?" + queryParams.toString();
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

// 点击查看图片
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
        // 定位上一个图片
        let imgs=document.querySelectorAll('img')
         this.indexImgs={}
        for(let i=0;i<  imgs.length;i++){
            let next= i+1<i.length?i+1:0;
            let prev=i-1>=0?i-1:imgs.length-1
    
            this.indexImgs[getId(imgs[i].src)]={
                'next':imgs[next],
                'prev':imgs[prev],
            }
        }


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
            if (event.key === "Escape")
                that.closeFullscreen();
        }
        );

        // 点击图片不管
        this.image.addEventListener('click', (e) => e.stopPropagation());
        this.image.addEventListener('keydown', (e) => {
            let id =getId(e.target.src)
            switch (e.key) {
                case '1':
                    let pre=this.indexImgs[id].prev
                    pre.click()
                    break;
                case '2':
                    let next=this.indexImgs[id].next
                    next.click()
                   
                    break;
                }
            })
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

        node.style.backgroundColor = colorWait
        axios.get(node.href)
            .then(function (response) {
                if (funcSuccess(response.data))
                    node.style.backgroundColor = colorSet
                else
                    node.style.backgroundColor = colorConcel
            })
            .catch(function (error) {
                node.style.backgroundColor = colorError
            })
    }
    )
}
// 状态判断链接成功
function clickAWithColorstatus(node){
    function fs(data){
        if(data.status.includes('set'))
        return true
        else
        return false
    }
    clickAWithColor(node,fs)
}
// 获取触摸滑动角度
class SwipeHandler {
    constructor(func) {
        this.startx = 0;
        this.starty = 0;
        this.stime = 0;
        this.nowr;
        this.func=func
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
        if (Math.abs(angx) < 20  && Math.abs(angy) < 20 ) {
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
            result = 'left';
        } else if (angle >= -45 && angle <= 45) {
            // 右
            result = 'right';

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
        this.func(direction)
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
        this.move = true
    }

    // 监听鼠标松开事件的处理函数
    handleMouseUp() {
        const deltaX = this.endX - this.startX;
        const deltaY = this.endY - this.startY;
        // 没有移动或者移动过短跳过
        if (!this.move || (Math.abs(deltaX) < 5 && Math.abs(deltaY) < 5)) {
            this.direction = 'no'
            this.restoreValue()
            this.move = false
            return
        }
        this.move = false
        if (Math.abs(deltaX) > Math.abs(deltaY)) {    // 水平方向移动更大
            if (deltaX > 0) {
                console.log("向右滑动");

            } else {
                console.log("向左滑动");
            }
        } else {    // 垂直方向移动更大
            if (deltaY > 0) {
                console.log("向上滑动");
                this.direction = 'up'
            } else {
                console.log("向下滑动");
                this.direction = 'down'
            }
        }

        this.restoreValue()
    }
    restoreValue() {
        // 重置鼠标初始和最终位置信息
        this.startX = 0;
        this.startY = 0;
        this.endX = 0;
        this.endY = 0;
    }
    getDirection() {
        return this.direction;
    }
}


function mouseAutoDisappear() {
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
        }, 500)
    });

}
mouseAutoDisappear()


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
let colorSet='green',colorConcel='black',colorError='red',colorWait='gray'
// 后台get请求
let likeELements = document.querySelectorAll(".ajaxLink");
likeELements.forEach((node) => {
    clickAWithColor(node)
})
document.querySelectorAll(".ajaxLink-status").forEach((node) => {
    clickAWithColorstatus(node)
})
// 设置背景
document.querySelectorAll(".colorSet").forEach((node) => {
    node.style.backgroundColor=colorSet
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
// 对象绑定 连续触摸事件
function ntouchEvent(n, dom, fn) {
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
    dom.addEventListener('touchstart', handler);
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

// 添加功能
function tabAddItem(item) {
    let container = document.querySelector('.functionContainer')
    container.appendChild(item)

}

function setTitle(index,length) {
    // 标题加索引
    let perc = (((index + 1) / (length)) * 100)
    let pre = `${Math.round(perc)}% ${index + 1}/${length}`
    document.title = pre + ' ' + document.title
}

function downloadfile(url, name) {
    // 下载文件
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
function clickVirtualA(url) {
    // 点击url
    const a = document.createElement('a');
    document.body.appendChild(a)
    a.style.display = 'none'
    a.href = url;
    a.click();
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url);

}