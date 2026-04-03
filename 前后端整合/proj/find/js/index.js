// ============================================================
// index.js
// 作用：控制启动页（LOADING 页）的动画与自动跳转。
// ============================================================

// 获取 loading 文字节点。
const loadingText = document.querySelector('.loading-text');

// 当前透明度，1 表示完全不透明。
let opacity = 1;

// 方向变量：
// -1 表示逐渐变淡
//  1 表示逐渐变亮
let direction = -1;

// 保存 requestAnimationFrame 返回的动画编号，方便停止动画。
let animationId;

/**
 * 使用 requestAnimationFrame 实现文字淡入淡出。
 *
 * 相比 setInterval：
 * - 更平滑
 * - 更省性能
 * - 更适合浏览器渲染节奏
 */
function fadeAnimation() {
    opacity += direction * 0.02;

    // 当透明度达到上下边界时，反转方向，形成来回呼吸效果。
    if (opacity <= 0.3 || opacity >= 1) {
        direction *= -1;
    }

    loadingText.style.opacity = opacity;
    animationId = requestAnimationFrame(fadeAnimation);
}

// 页面完全加载后：
// 1. 启动淡入淡出动画
// 2. 3 秒后自动跳转到首页 home.html
window.addEventListener('load', () => {
    if (loadingText) {
        fadeAnimation();
        jumpToPage('home.html', 3000);
    }
});

// 当浏览器标签页切到后台时，暂停动画，节省性能。
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        cancelAnimationFrame(animationId);
    } else if (loadingText) {
        fadeAnimation();
    }
});

// 页面离开前主动停止动画，防止无意义的渲染任务继续占用资源。
window.addEventListener('beforeunload', () => {
    cancelAnimationFrame(animationId);
});

// 防御性写法：如果 common.js 没有提前定义 jumpToPage，
// 这里就补一个简化版，避免报错。
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
