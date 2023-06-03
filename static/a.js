let nowPn=2
let nextPn=3
window.addEventListener('scroll', function() {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
      // 当用户滚动到页面底部时
      // 发送网络请求
      function updateshots(url) {
        fetch(url)  // 发送 GET 请求到 /greeting 路径
            .then(response => response.text())  // 将响应转换成纯文本格式
            .then(text => {
                document.querySelector('#shots').innerHTML+= text
                nextPn+=1
            })  // 更新 <p> 元素的文本内容
            .catch(error => nowPn-=1);  // 处理请求错误
    }
    let url="/shots?pn="+nowPn
    if(nowPn!==nextPn){
        nowPn=nextPn
        updateshots(url)
        console(nowPn)
        }
    }
  });
  