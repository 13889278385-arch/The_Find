// ============================================================
// search.js
// 作用：智能检索页逻辑。
// - 收集筛选条件
// - 调用 /api/items/search
// - 把结果列表渲染到页面
// ============================================================

function renderItemCard(item) {
    return `
        <div class="result-card">
            ${item.image_url ? `<img class="result-thumb" src="${item.image_url}" alt="${item.title}">` : `<div class="result-thumb"></div>`}
            <div>
                <div class="result-title">${item.title}（${item.item_type_label}）</div>
                <div class="result-meta">类别：${item.category} ｜ 地点：${item.location} ｜ 时间：${item.occurred_at}</div>
                <div class="result-meta">状态：${item.status_label}</div>
                <div class="result-desc">描述：${item.description || '暂无描述'}</div>
            </div>
        </div>
    `;
}

async function loadResults() {
    const keyword = document.getElementById('keyword')?.value.trim() || '';
    const type = document.getElementById('typeFilter')?.value || '';
    const status = document.getElementById('statusFilter')?.value || '';

    const params = new URLSearchParams();
    if (keyword) params.set('q', keyword);
    if (type) params.set('item_type', type);
    if (status) params.set('status', status);

    const resultCount = document.getElementById('resultCount');
    const resultList = document.getElementById('resultList');
    resultCount.textContent = '正在加载...';

    const res = await fetch(`/api/items/search?${params.toString()}`);
    const data = await res.json();

    if (!res.ok || !data.success) {
        throw new Error(data.message || '检索失败');
    }

    resultCount.textContent = `共找到 ${data.count} 条记录`;
    resultList.innerHTML = data.items.length
        ? data.items.map(renderItemCard).join('')
        : '<div class="result-empty">暂无符合条件的数据</div>';
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('searchBtn')?.addEventListener('click', loadResults);
    loadResults().catch(error => {
        document.getElementById('resultCount').textContent = `加载失败：${error.message}`;
    });
});
