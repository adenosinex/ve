function fullScreenVideoOnClick(  videoUrl) {
    const img = document.querySelector('img');
    const video = document.createElement('video');

    // 监听视频元素加载完成事件
    video.addEventListener('canplay', () => {
      // 调整视频元素样式，确保填满屏幕
      const rect = img.getBoundingClientRect();
      const videoRatio = video.videoWidth / video.videoHeight;
      const windowRatio = window.innerWidth / window.innerHeight;
  
      if (videoRatio > windowRatio) {
        video.style.width = '100%';
        video.style.height = 'auto';
      } else {
        video.style.width = 'auto';
        video.style.height = '100%';
      }
  
      // 进入全屏模式并播放视频
      video.requestFullscreen();
      video.play();
    });
  
    // 监听视频元素出错事件
    video.addEventListener('error', (e) => {
      console.error(`Failed to load video: ${e.target.src}`);
      document.exitFullscreen();  // 退出全屏模式
      video.remove();             // 移除视频元素
    });
  
    // 初始化视频元素
    video.src = videoUrl;
    video.controls = true;        // 显示视频控制栏
  
    // 点击图片时开始播放视频
    img.addEventListener('click', () => {
      img.style.display = 'none';  // 隐藏图片元素
      document.body.appendChild(video);  // 加入视频元素到文档中
    });
  
    return video;  // 返回视频元素，便于退出全屏后继续操作
  }
  
  fullScreenVideoOnClick('http://pcc.xin-ade.icu/file/33B9062D7C32F713F0E7AC023C63F9574DF5D84E')

  document.querySelector('video').addEventListener('click',(e)=>e.target.requestFullscreen())


const video = document.querySelector('video');
const container = document.querySelector('.image-container');

function toggleFullScreen() {
  if (!document.fullscreenElement) {
    // 进入全屏模式
    if (container.requestFullscreen) {
      container.requestFullscreen();
    } else if (container.mozRequestFullScreen) {
      /* Firefox */
      container.mozRequestFullScreen();
    } else if (container.webkitRequestFullscreen) {
      /* Chrome, Safari and Opera */
      container.webkitRequestFullscreen();
    } else if (container.msRequestFullscreen) {
      /* IE/Edge */
      container.msRequestFullscreen();
    }
    // 设置长宽
    const width = window.innerWidth;
    const height = window.innerHeight;
    video.style.width = `${width}px`;
    video.style.height = `${height}px`;
  } else {
    // 退出全屏模式
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.mozCancelFullScreen) {
      /* Firefox */
      document.mozCancelFullScreen();
    } else if (document.webkitExitFullscreen) {
      /* Chrome, Safari and Opera */
      document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) {
      /* IE/Edge */
      document.msExitFullscreen();
    }
    // 还原尺寸
    video.style.width = '';
    video.style.height = '';
  }
}

video.addEventListener('click', toggleFullScreen);
