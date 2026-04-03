// ============================================================
// common.js
// 作用：放所有页面都能复用的公共逻辑。
// 例如：
// - 页面跳转
// - 顶部导航高亮
// - 用户区域（已登录 / 未登录）的初始化
// ============================================================

/**
 * 公共跳转函数。
 *
 * @param {string} url   要跳转的目标页面地址
 * @param {number} delay 延迟毫秒数，默认 0 表示立刻跳转
 */
window.jumpToPage = function(url, delay = 0) {
    if (delay > 0) {
        setTimeout(() => {
            window.location.href = url;
        }, delay);
    } else {
        window.location.href = url;
    }
};

/**
 * 给顶部导航栏自动加“当前页高亮”。
 *
 * 实现思路：
 * 1. 拿到当前地址栏中的文件名，例如 home.html。
 * 2. 遍历导航栏里的每个 a 标签。
 * 3. 如果链接指向的页面和当前页面相同，就加上 active 类。
 */
function bindNavActive() {
    const navLinks = document.querySelectorAll('.nav-menu a');
    if (!navLinks.length) return;

    const currentPath = window.location.pathname.split('/').pop() || 'index.html';

    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href').split('/').pop();
        if (linkPath === currentPath) {
            link.classList.add('active');
        }
    });
}

/**
 * 初始化右上角用户区域。
 *
 * 功能：
 * - 如果用户已登录：显示用户名 + 退出按钮
 * - 如果用户未登录：显示“我的 / 注册 / 登录”入口
 */
async function initUserArea() {
    const userArea = document.querySelector('.user-area');
    if (!userArea) return;

    try {
        const res = await fetch('/api/auth/me');
        const data = await res.json();

        if (data.logged_in && data.user) {
            userArea.innerHTML = `
                <img src="img/me.png" alt="用户图标" class="user-icon">
                <a href="my.html">${data.user.username}</a>
                <span class="divider">/</span>
                <a href="#" id="logoutLink">退出</a>
            `;

            const logoutLink = document.getElementById('logoutLink');
            logoutLink?.addEventListener('click', async (e) => {
                e.preventDefault();
                await fetch('/api/auth/logout', { method: 'POST' });
                alert('已退出登录');
                window.location.reload();
            });
        } else {
            userArea.innerHTML = `
                <img src="img/me.png" alt="用户图标" class="user-icon">
                <a href="my.html">我的</a>
                <a href="register.html">注册</a>
                <span class="divider">/</span>
                <a href="login.html">登录</a>
            `;
        }
    } catch (error) {
        console.error('初始化用户区失败:', error);
    }
}

// 所有页面加载完成后，统一做公共初始化。
document.addEventListener('DOMContentLoaded', () => {
    bindNavActive();
    initUserArea();
});
