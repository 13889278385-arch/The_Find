// ============================================================
// public.js
// 作用：驱动“最新公示”相关页面的数据渲染。
// 包括：失物/招领列表、高频地点、已归还公示、公告。
// ============================================================

/**
 * 通用获取 JSON 的小工具。
 */
async function getJson(url) {
    const res = await fetch(url);
    const data = await res.json();
    if (!res.ok || !data.success) {
        throw new Error(data.message || '加载失败');
    }
    return data;
}

/**
 * 把普通数组渲染成 <li> 列表。
 */
function renderList(container, items) {
    if (!container) return;
    container.innerHTML = items.map(item => `<li>${item}</li>`).join('');
}

// 页面加载后，根据当前页面文件名决定请求哪个接口、渲染哪类数据。
document.addEventListener('DOMContentLoaded', async () => {
    const page = location.pathname.split('/').pop();
    const list = document.querySelector('.content-list');

    try {
        if (page === 'find.html') {
            const data = await getJson('/api/items/latest?limit=10');
            renderList(list, data.items.map(item => `${item.title} | ${item.location} | ${item.occurred_at} | ${item.status_label}`));
        } else if (page === 'place.html') {
            const data = await getJson('/api/stats/hotspots');
            renderList(list, data.hotspots.map(item => `${item.location}（${item.total}次）`));
        } else if (page === 'returned.html') {
            const data = await getJson('/api/items/returned?limit=10');
            renderList(list, data.items.map(item => `${item.title} | ${item.status_label} | ${item.occurred_at}`));
        } else if (page === 'notice.html') {
            const data = await getJson('/api/notices');
            const desc = document.querySelector('.content-desc');
            if (desc) {
                desc.innerHTML = data.notices.map(n => `【${n.created_at}】${n.title}：${n.content}`).join('<br><br>');
            }
        }
    } catch (error) {
        if (list) {
            list.innerHTML = `<li>数据加载失败：${error.message}</li>`;
        }
        const desc = document.querySelector('.content-desc');
        if (desc) {
            desc.textContent = `数据加载失败：${error.message}`;
        }
    }
});
