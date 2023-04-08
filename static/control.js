
// 单个视频页面限制高度满屏
let allVideos = document.querySelectorAll('video')
 
  if (allVideos.length===1){
    let fullHeight = window.innerHeight;
        allVideos[0].height = fullHeight;
        console.log('set height'+fullHeight)
  
  }

  // 测试添加链接
// let a=document.createElement('audio')
// a.src='/file/762C0E1413006A091A1FF0B653DE1683C3DC5D9A'
// a.setAttribute('controls',true)

// let row=document.querySelector('.post-tabs')
// row.insertBefore(a,row.children[0])
// 属性
// 所有媒体元素
let medias = [];
let tagAttr = {
    'video': { 'width': '100%', 'controls': 'true', 'autoplay': 'true' },
    'audio': { 'controls': 'true','loop':'' },
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
 

 

//    索引链接
let divs = document.querySelectorAll('.col')
let links_page = Array.from(document.querySelectorAll('a')).filter((node) => { return node.href.includes('pn') })
 

// 预览节点 点击详情
let previews = document.querySelectorAll('.preview')
// 点击查看
previews.forEach((node) => {
    node.addEventListener('click', (e) => {
        // e.preventDefault()
        let id = e.target.dataset.id;
        window.location.href = '/detail/'+id
    })
})

// // 本地存储
let previewsList, previewsDict;
if (previews.length > 5) {
    // id api 字典
    previewsDict = {};
    previewsList = new Array();
    [].forEach.call(previews, (node) => {
        let id = node.dataset.id;
        previewsDict[id] = '/detail/'+id
        previewsList.push(id)
    })
    previewsDict['index'] = previewsList
    localStorage.setItem('preLink', JSON.stringify(previewsDict))
}
else {
    previewsDict = JSON.parse(localStorage.getItem('preLink'));
    if (previewsDict)
        previewsList = previewsDict['index']

}

 
 
// 详情页三击 下一页
nclickEvent(3, document, (e)=> {
  let b=location.href.split('/')
  let id=b[b.length-1]
  let index = previewsList.indexOf(id)

  if (id && location.pathname.includes('detail')) {
      let clickY = e.clientY
      let mediaY;
      let rect;
      for (let i = 0; i < medias.length; i++) {
          try {
               rect= medias[i][0].getBoundingClientRect()
               mediaY=rect.y
              break
          }
          catch {

          }
      }
      let plus 
      let half=rect.height/2
      if (clickY > mediaY+half)
          plus = -1
      else if (clickY < mediaY-half)
          plus = 1
      else
        return
      index=index + plus
      if (index === previewsList.length)
          index = 0
      else if (index === -1)
          index=previewsList.length-1

      let url = previewsDict[previewsList[index]]
      let id =  previewsList[index] 
      window.location.href =  url
  }
})
// 获取id正则 获取下一个id
let ReId=/[A-Z\d]{40}/

// 获取指定位置id 超范围自动循环
function secureId(index){
    if (index === previewsList.length)
        index = 0
    else if (index === -1)
    index=previewsList.length-1
    return previewsList[index]
}

//   播放页 自动播放
// if (location.pathname.includes('play')){
     
//     nclickEvent(1, document, (e)=> {
//     let b=location.href.split('/')
//     let id=b[b.length-1]
//     let index = previewsList.indexOf(id)
  
//     if (id && location.pathname.includes('detail')) {
//         let clickY = e.clientY
//         let mediaY;
//         let rect;
//         for (let i = 0; i < medias.length; i++) {
//             try {
//                  rect= medias[i][0].getBoundingClientRect()
//                  mediaY=rect.y
//                 break
//             }
//             catch {
  
//             }
//         }
//         let plus 
//         let half=rect.height/2
//         if (clickY > mediaY+half)
//             plus = -1
//         else if (clickY < mediaY-half)
//             plus = 1
//         else
//           return
//         index=index + plus
//         if (index === previewsList.length)
//             index = 0
//         else if (index === -1)
//             index=previewsList.length-1
  
//         let url = previewsDict[previewsList[index]]
//         let id =  previewsList[index] 
//         window.location.href =  url
//     }
//   })
// }
//   播放页滑动播放
if (location.pathname.includes('play')){
      // 获取id
     // 获取文件自动播放 设置id
     let file=$('#play').children()[0]
     let tagname=file.tagName
     if (tagname==='VIDEO' ||tagname==='AUDIO')
     file.play()

    
    let id=ReId.exec(file.src)[0]

    let target=document.createElement('a')
    target.href='/detail/'+id
    let btn=document.createElement('button')
    btn.textContent='详情'
    btn.className="btn btn-large btn-primary"
    target.appendChild(btn)
    
    let insertObj=$('#play')[0]
    insertObj.insertBefore(target,insertObj.children[0])

    
    var startx, starty;
    let stime;
    
    //获得角度
    function getAngle(angx, angy) {
        return Math.atan2(angy, angx) * 180 / Math.PI;
    };
    
    //根据起点终点返回方向 1向上滑动 2向下滑动 3向左滑动 4向右滑动 0点击事件
    function getDirection(startx, starty, endx, endy) {
        var angx = endx - startx;
        var angy = endy - starty;
        var result = 0;
    
        //如果滑动距离太短
        if (Math.abs(angx) < 2 && Math.abs(angy) < 2) {
            return result;
        }
    
        var angle = getAngle(angx, angy);
        if (angle >= -135 && angle <= -45) {
            result = 1;
        } else if (angle > 45 && angle < 135) {
            result = 2;
        } else if ((angle >= 135 && angle <= 180) || (angle >= -180 && angle < -135)) {
            result = 3;
        } else if (angle >= -45 && angle <= 45) {
            result = 4;
        }
        return result;
    }
    
    //手指接触屏幕
    document.addEventListener("touchstart", function(e){
        startx = e.touches[0].pageX;
        starty = e.touches[0].pageY;
        stime=  new Date().getTime();
    }, false);
    
    //手指离开屏幕
    document.addEventListener("touchend", function(e) {
        var endx, endy,now;
        endx = e.changedTouches[0].pageX;
        endy = e.changedTouches[0].pageY;
        now=new Date().getTime();
        // alert(now-stime)
        let disY=Math.abs(endy-starty)
        let sptime=now-stime
        alert(disY+' '+sptime)
        
        if(sptime>300 && disY<150)
        return
        var direction = getDirection(startx, starty, endx, endy);

         
      id=ReId.exec(file.src)[0]
      let index = previewsList.indexOf(id)
      pid=secureId(index-1)
      nid=secureId(index+1)
        
      nlink='/file/'+nid
      plink='/file/'+pid

        switch (direction) {
            // case 0:
            //     alert("点击！");
            //     break;
            case 1:
                file.src=plink
                break;
            case 2:
                file.src=nlink
                break;
            // case 3:
            //     alert("向左！");
            //     break;
            // case 4:
            //     alert("向右！");
            //     break;
            // default:
            //     alert("点击！");
            //     break;
            }
    }, false);
    // vnode.play()
    target.href='/detail/'+ReId.exec(file.src)[0]

}
//   详情页添加下一个跳转
if (location.pathname.includes('detail')){
    // 获取文件自动播放 设置id
    let file=$('.file').children()[0]
    let tagname=file.tagName
    if (tagname==='VIDEO' ||tagname==='AUDIO')
    file.play()
    
    file.setAttribute('id','play')
    // 获取id
    let id=ReId.exec(location.href)[0]
    let index = previewsList.indexOf(id)

    pid=secureId(index-1)
    nid=secureId(index+1)
    nlink='/detail/'+nid
    plink='/detail/'+pid
    // 链接嵌套按钮
    let container=document.createElement('div')
    let next=document.createElement('a')
    next.href=nlink
    let btn=document.createElement('button')
    btn.textContent='下一个'
    btn.className="btn btn-large btn-primary"
    next.appendChild(btn)
    // 播放完自动下一个
    if (tagname==='VIDEO' ||tagname==='AUDIO')
        file.addEventListener('ended',()=>{next.click()})

    let prev=document.createElement('a')
    prev.href=plink
    btn=document.createElement('button')
     btn.textContent='上一个'
     btn.className="btn btn-large btn-primary pull-right"
     prev.appendChild(btn)

     let tip=document.createElement('span')
     tip.textContent=index

    container.appendChild(tip)
    container.appendChild(next)
    container.appendChild(prev)

    let insertObj=document.querySelector('.info')
    insertObj.insertBefore(container,insertObj.children[0])

    // 定位到文件
    let locida=document.createElement('a')
    locida.href='#play'
    locida.click()

      
    // 键盘控制下一个
    window.addEventListener('keydown',(e)=>{
        switch(e.key){
            case 'ArrowLeft':
            prev.click()
            break;
            case 'ArrowRight':
            next.click()
        }
    })
    // 左右点击下一个
    // document.documentElement.clientWidth
    $('body').click((e)=>{
        let clickx=e.screenX
         if (clickx<200 &&pid)
         prev.click()
         if (clickx>1300 &&nid)
         next.click()
    })
     
}

// 按钮 所有查看源文件
let src_button=document.querySelectorAll('button.src')
if (src_button[0]){
  src_button.forEach((ele)=>{
    ele.addEventListener('click',()=>location.href=ele.dataset.link)
  }
  )
   
}
// 按钮 所有查看源文件
let play_button=document.querySelectorAll('button.play')
if (play_button[0]){
  play_button.forEach((node)=>{
    node.addEventListener('click',( )=>{
        let t=location.origin+ node.dataset.link
        window.location.href=t
    })
  }
  )
   
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
  formInput.addEventListener("compositionend", ()=>location.href = '/?kw=' + formInput.value);
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
let buttnons = document.querySelectorAll("button.like");
buttnons.forEach((node) => {

    if (node.dataset.like)
     node.style.backgroundColor = 'red'
    node.addEventListener('click', (e) => {
        e.stopPropagation()
        let tag=e.target
        let id = tag.dataset.id
        tag.style.backgroundColor = 'blue'
        if (!id)
            return
        let url = '/tag/' + id+'?tag=like'
        fetch(url)
            .then(response => response.json())
            .then(result => {
                // 返回值处理 变色链接
                let rtext = JSON.stringify(result);
                if (rtext.includes('删除'))
                    tag.style.backgroundColor = 'white'
                else
                    tag.style.backgroundColor = 'red'
            })
       
    })
})

//  导航链接激活高亮a 加active 如果href在当前url中
let links = document.querySelectorAll("a");
[].forEach.call(links, function (link) {
    let url = location.pathname + location.search
    let href = link.pathname + link.search
    if (url.includes(href)) {
        if (href === '/' && url === href)
            link.classList.add("active");
        else if (href !== '/')
            link.classList.add("active");
    }
    else {
        let t = link.classList.contains('activate')
        if (t);
        link.classList.remove("active");
    }
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


// 局部更新内容
function update(data) {
    let posts = data.posts
    for (let i = 0; i < divs.length; i++) {
        // 框架不变替换id
        let oldId = divs[i].dataset.id
        let newId = posts[i].id
        let ihtml = divs[i].innerHTML.replace(oldId, newId)

        let t = divs[i].dataset.name
        let t2 = posts[i].name
        ihtml = ihtml.replace(t, t2)
        divs[i].innerHTML = ihtml
    }
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



  // 音频链接
let musics = document.querySelectorAll('audio')
let musicSrcs=[]
let musicSrcNode={}
for (let i=0;i<musics.length;i++){
    musicSrcs[i]=musics[i].src
    musicSrcNode[musics[i].src]=musics[i]
}
// 添加音乐播放器
if (musics.length>0){
  let container=document.createElement('div')

  let display_audio=document.createElement('audio')
  display_audio.src=musics[0].src
  display_audio.setAttribute('controls',true)

  let playNext=document.createElement('button')
  playNext.textContent='下一首'
  let downAll=document.createElement('button')
  downAll.textContent='下载所有'

  let tipNow=document.createElement('span')
  tipNow.textContent='1.正在播放 '+musics[0].dataset.desc

  container.appendChild(display_audio)
  container.appendChild(playNext)
  container.appendChild(downAll)
  container.appendChild(tipNow)
  let insertObj=document.querySelector('.post-tabs')
  insertObj.insertBefore(container,insertObj.children[0])
  // row.insertBefore(audio,row.children[0])

  function PlayAudio(node){
      display_audio.src=node.src
      let index=musicSrcs.indexOf(display_audio.src)
    tipNow.textContent=index+':'+node.dataset.desc 
    display_audio.play()
  }
//   点击项目播放
  musics.forEach((node) =>   {
    $(node.parentNode).click(()=>{
        PlayAudio(node)
    })
  })
//   播放下一首
  playNext.addEventListener('click',(e)=>{
    let index=musicSrcs.indexOf(display_audio.src)
    index=index+1
    if (index===musicSrcs.length)
    index=0
    PlayAudio(musicSrcNode[musicSrcs[index]])
   
  })

//   下载所有
  $(downAll).click(()=>{
    alert('下载所有')
    musics.forEach((node) =>   {
        var name = node.dataset.desc
        var src = window.location.origin + node.getAttribute('src')  
        downloadfile(src, name)
        //  this.downloadMp3('/api/musics?music_id=1',name);
  
      })
  })
}

// 检测到音频触发
// if (audios[0]) {
//   let btnNext = document.querySelector('#next')
//   let btnPreview = document.querySelector('#pre')
//   let btnAcc = document.querySelector('#acc')
//   let musicTipJunmp = document.querySelector('#tip')
//   let containerAudios = audios[0].parentNode.parentNode
//   let btnStop = document.querySelector('#stop')

//   let lastPausePlay;
//   let lastPlay;

//   if (audios.length>1){
//     // 播放停止其他 显示当前播放
//     audios.forEach((i) => {
//       i.addEventListener("play", pauseAllOther);
//       i.addEventListener('play', showTips);
  
//       i.addEventListener('pause', (e) => lastPausePlay = e.target);
//     })
//     // 功能按钮
//     btnNext.addEventListener('click', nextPlay.bind(1))
//     btnPreview.addEventListener('click', nextPlay.bind(2))
//     btnAcc.addEventListener('click', nextPlay.bind(3))
//     btnStop.addEventListener('click', pauseAll.bind(true))

//   }


//   // 将audios中其他的audio全部暂停
//   function pauseAllOther() {
//     var self = this;
//     audios.forEach((i) => i !== self && i.pause())
//   }
//   // 全部暂停 记录当前播放对象备播放
//   function pauseAll() {
//     var flag = self;
//     audios.forEach((i) => {
//       if (!i.paused) {
//         lastPausePlay = i
//         i.pause()
//         flag = false
//       }
//     })
//     if (flag)
//       lastPausePlay.play()
//   }
//   // 提示当前播放信息 audio父节点前置
//   function showTips(e) {
//     let node = e.target;
//     audios.forEach((i) => {

//       if (!i.paused) {

//         if (lastPlay) {
//           // 重复播放无操作
//           if (lastPlay === node.parentNode)
//             return
//           containerAudios.appendChild(lastPlay)
//           lastPlay = node.parentNode
//           musicTipJunmp.appendChild(lastPlay)
//           // musicTipJunmp.replaceChild(lastPlay,node.parentNode.cloneNode(true)) 
//         }
//         else {
//           lastPlay = node.parentNode
//           musicTipJunmp.appendChild(lastPlay)

//         }



//       }
//     })
//   }



//   // 顺序播放 前后
//   function nextPlay() {
//     let choice = this.valueOf()
//     let flag = 1
//     for (let i = 0; i < audios.length; i++) {
//       if (!audios[i].paused) {
//         let nextIndex = i
//         if (choice === 3) {
//           audios[i].currentTime = audios[i].currentTime + 3
//           break
//         }
//         else if (choice === 1) {
//           nextIndex++
//         }
//         else
//           nextIndex--

//         if (nextIndex === audios.length)
//           nextIndex = 0
//         else if (nextIndex === -1)
//           nextIndex = audios.length - 1

//         audios[nextIndex].play()
//         flag = 0
//         break
//       }
//     }
//     if (flag && choice === 2)
//       audios[audios.length - 1].play()
//     else if (flag && choice === 1)
//       audios[0].play()



//   }
// }

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