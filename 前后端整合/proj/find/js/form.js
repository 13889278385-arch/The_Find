// ============================================================
// form.js
// 作用：处理“我要招领”和“我要寻物”两个表单页的交互逻辑。
// 共用原因：这两个页面结构几乎一致，只是 item_type 不同。
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    // 先缓存页面中要频繁使用的 DOM 节点，避免重复查询。
    const uploadArea = document.getElementById('uploadArea');
    let fileInput = document.getElementById('fileInput');
    const goodsTypeSelect = document.getElementById('goodsTypeSelect');
    const otherTypeInput = document.getElementById('otherTypeInput');
    const pickPlaceSelect = document.getElementById('pickPlaceSelect');
    const otherPlaceInput = document.getElementById('otherPlaceInput');
    const submitBtn = document.getElementById('submitBtn');

    // 通过当前页面路径判断：
    // - claim.html -> 招领 found
    // - 其他（这里主要是 lost.html）-> 寻物 lost
    const pathname = window.location.pathname;
    const itemType = pathname.includes('claim.html') ? 'found' : 'lost';

    /**
     * 重置上传区域为初始状态。
     *
     * 为什么要封装成函数？
     * 因为提交成功后、重新选择图片前，都可能要恢复“上传图片”的初始界面。
     */
    function resetUploadArea() {
        if (!uploadArea) return;

        uploadArea.innerHTML = `
            <div class="plus">+</div>
            <div class="text">上传图片</div>
            <input type="file" id="fileInput" accept="image/*" hidden>
        `;

        // innerHTML 重绘后，旧的 input 节点已经失效，
        // 所以这里必须重新获取一次新的 fileInput。
        fileInput = document.getElementById('fileInput');

        // 点击整个上传区域时，自动触发隐藏文件输入框。
        uploadArea.onclick = () => fileInput?.click();

        // 监听用户重新选择文件。
        fileInput?.addEventListener('change', handleFileChange);
    }

    /**
     * 文件选择后，使用 FileReader 在前端做本地预览。
     *
     * 优点：
     * - 用户能马上看到自己选了哪张图
     * - 不需要先上传到服务器再预览
     */
    function handleFileChange(e) {
        if (!e.target.files?.[0]) return;

        const reader = new FileReader();
        reader.onload = (ev) => {
            uploadArea.innerHTML = `<img src="${ev.target.result}" style="width:100%;height:100%;object-fit:cover;border-radius:18px;">`;
        };
        reader.readAsDataURL(e.target.files[0]);
    }

    // 页面一进入就先把上传区初始化好。
    resetUploadArea();

    // ------------------------------
    // “物品类别”下拉框联动：选择“其他”时显示补充输入框
    // ------------------------------
    goodsTypeSelect?.addEventListener('change', function() {
        if (this.value === 'other') {
            otherTypeInput.style.display = 'block';
            otherTypeInput.required = true;
        } else {
            otherTypeInput.style.display = 'none';
            otherTypeInput.required = false;
            otherTypeInput.value = '';
        }
    });

    // ------------------------------
    // “地点”下拉框联动：选择“其他”时显示补充输入框
    // ------------------------------
    pickPlaceSelect?.addEventListener('change', function() {
        if (this.value === 'other') {
            otherPlaceInput.style.display = 'block';
            otherPlaceInput.required = true;
        } else {
            otherPlaceInput.style.display = 'none';
            otherPlaceInput.required = false;
            otherPlaceInput.value = '';
        }
    });

    // ------------------------------
    // 点击提交按钮：做表单校验 + 发送到后端
    // ------------------------------
    submitBtn?.addEventListener('click', async () => {
        const inputs = document.querySelectorAll('.form-input');
        const goodsName = inputs[0]?.value.trim();
        const dateTime = inputs[inputs.length - 1]?.value;
        const goodsType = goodsTypeSelect.value;
        const otherType = otherTypeInput.value.trim();
        const pickPlace = pickPlaceSelect.value;
        const otherPlace = otherPlaceInput.value.trim();
        const description = document.querySelector('.form-textarea')?.value.trim() || '';

        // ---------- 前端基础校验 ----------
        if (!goodsName) return alert('请填写物品名称！');
        if (!goodsType) return alert('请选择物品类别！');
        if (goodsType === 'other' && !otherType) return alert('请输入具体物品类型！');
        if (!pickPlace) return alert(itemType === 'found' ? '请选择捡到地点！' : '请选择丢失地点！');
        if (pickPlace === 'other' && !otherPlace) return alert('请输入具体地点！');
        if (!dateTime) return alert(itemType === 'found' ? '请选择捡到时间！' : '请选择丢失时间！');

        // 如果下拉框选的是“其他”，则使用用户补充输入的文字；
        // 否则使用当前选项本身显示给用户看的文本。
        const finalGoodsType = goodsType === 'other'
            ? otherType
            : goodsTypeSelect.options[goodsTypeSelect.selectedIndex].text;

        const finalPlace = pickPlace === 'other'
            ? otherPlace
            : pickPlaceSelect.options[pickPlaceSelect.selectedIndex].text;

        // 因为要上传图片，所以这里必须使用 FormData，
        // 不能用普通 JSON。
        const formData = new FormData();
        formData.append('item_type', itemType);
        formData.append('title', goodsName);
        formData.append('category', finalGoodsType);
        formData.append('location', finalPlace);
        formData.append('occurred_at', dateTime);
        formData.append('description', description);

        if (fileInput?.files?.[0]) {
            formData.append('image', fileInput.files[0]);
        }

        // 提交期间把按钮置灰，避免用户连续点很多次造成重复提交。
        submitBtn.disabled = true;
        submitBtn.textContent = '提交中...';

        try {
            const res = await fetch('/api/items', {
                method: 'POST',
                body: formData,
            });

            const data = await res.json();
            if (!res.ok || !data.success) {
                throw new Error(data.message || '提交失败');
            }

            alert(`${itemType === 'found' ? '招领' : '寻物'}信息提交成功！
记录编号：${data.item.id}`);

            // ---------- 提交成功后清空表单 ----------
            document.querySelectorAll('.form-input').forEach(i => i.value = '');
            document.querySelectorAll('.form-select').forEach(s => s.value = '');
            const textarea = document.querySelector('.form-textarea');
            if (textarea) textarea.value = '';
            otherTypeInput.style.display = 'none';
            otherPlaceInput.style.display = 'none';
            resetUploadArea();
        } catch (error) {
            alert(error.message || '提交失败，请稍后重试');
        } finally {
            // 无论成功还是失败，都恢复按钮状态。
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<img src="img/submit.png" alt="提交图标">提交';
        }
    });
});
