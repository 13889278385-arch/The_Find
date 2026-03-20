// LOADING文字淡入淡出动画
const loadingText = document.querySelector('.loading-text');
let opacity = 1;
let direction = -1;
let animationId;

// 流畅动画（替代setInterval）
function fadeAnimation() {
    opacity += direction * 0.02;
    if (opacity <= 0.3 || opacity >= 1) {
        direction *= -1;
    }
    loadingText.style.opacity = opacity;
    animationId = requestAnimationFrame(fadeAnimation);
}

// 页面加载完成后启动动画 + 3秒自动跳转到首页
window.addEventListener('load', () => {
    if (loadingText) {
        fadeAnimation();
        // 复用公共跳转函数，3秒后跳转到首页
        jumpToPage('home.html', 3000);
    }
});

// 性能优化：页面隐藏/卸载时停止动画
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        cancelAnimationFrame(animationId);
    } else if (loadingText) {
        fadeAnimation();
    }
});

window.addEventListener('beforeunload', () => {
    cancelAnimationFrame(animationId);
});

// 扩展公共跳转函数：支持延迟跳转
if (!window.jumpToPage) {
    window.jumpToPage = function(url, delay = 0) {
        if (delay > 0) {
            setTimeout(() => {
                window.location.href = url;
            }, delay);
        } else {
            window.location.href = url;
        }
    };
}