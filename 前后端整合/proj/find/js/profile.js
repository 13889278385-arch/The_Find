// ============================================================
// profile.js
// 作用：我的页面逻辑，显示当前登录用户信息和“我的发布”列表。
// ============================================================

function renderMine(item) {
    return `
        <div class="result-card">
            ${item.image_url ? `<img class="result-thumb" src="${item.image_url}" alt="${item.title}">` : `<div class="result-thumb"></div>`}
            <div>
                <div class="result-title">${item.title}</div>
                <div class="result-meta">类型：${item.item_type_label} ｜ 状态：${item.status_label}</div>
                <div class="result-meta">类别：${item.category} ｜ 地点：${item.location} ｜ 时间：${item.occurred_at}</div>
                <div class="result-desc">描述：${item.description || '暂无描述'}</div>
            </div>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', async () => {
    const profileUser = document.getElementById('profileUser');
    const myList = document.getElementById('myList');

    try {
        const meRes = await fetch('/api/auth/me');
        const meData = await meRes.json();
        if (!meData.logged_in || !meData.user) {
            profileUser.textContent = '当前未登录，请先登录后查看我的发布。';
            myList.innerHTML = '<div class="result-empty">未登录，暂无可展示内容</div>';
            return;
        }

        profileUser.textContent = `当前用户：${meData.user.username} ${meData.user.student_no ? '｜ 学号：' + meData.user.student_no : ''}`;

        const res = await fetch('/api/my/items');
        const data = await res.json();
        if (!res.ok || !data.success) throw new Error(data.message || '加载失败');

        myList.innerHTML = data.items.length
            ? data.items.map(renderMine).join('')
            : '<div class="result-empty">你还没有发布过记录</div>';
    } catch (error) {
        profileUser.textContent = `加载失败：${error.message}`;
        myList.innerHTML = '<div class="result-empty">数据加载失败</div>';
    }
});
