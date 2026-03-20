// 表单页面通用交互（支持两个下拉框的其他自定义输入）
document.addEventListener('DOMContentLoaded', function() {
    // 1. 图片上传预览（不变）
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    uploadArea?.addEventListener('click', () => fileInput?.click());
    
    fileInput?.addEventListener('change', (e) => {
        if (e.target.files?.[0]) {
            const reader = new FileReader();
            reader.onload = (ev) => {
                uploadArea.innerHTML = `<img src="${ev.target.result}" style="width:100%;height:100%;object-fit:cover;border-radius:18px;">`;
            };
            reader.readAsDataURL(e.target.files[0]);
        }
    });

    // 2. 物品类别下拉框监听
    const goodsTypeSelect = document.getElementById('goodsTypeSelect');
    const otherTypeInput = document.getElementById('otherTypeInput');
    
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

    // 3. 捡到地点下拉框监听
    const pickPlaceSelect = document.getElementById('pickPlaceSelect');
    const otherPlaceInput = document.getElementById('otherPlaceInput');
    
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

    // 4. 提交按钮逻辑（完整验证）
    const submitBtn = document.getElementById('submitBtn');
    submitBtn?.addEventListener('click', () => {
        // 获取表单数据
        const goodsName = document.querySelectorAll('.form-input')[0].value;
        const goodsType = goodsTypeSelect.value;
        const otherType = otherTypeInput.value;
        const pickPlace = pickPlaceSelect.value;
        const otherPlace = otherPlaceInput.value;
        
        // 1. 验证物品名称
        if (!goodsName) {
            alert('请填写物品名称！');
            return;
        }

        // 2. 验证物品类别
        if (!goodsType) {
            alert('请选择物品类别！');
            return;
        }
        if (goodsType === 'other' && !otherType) {
            alert('请输入具体的物品类型！');
            otherTypeInput.focus();
            return;
        }

        // 3. 验证捡到地点
        if (!pickPlace) {
            alert('请选择捡到地点！');
            return;
        }
        if (pickPlace === 'other' && !otherPlace) {
            alert('请输入具体的捡到地点！');
            otherPlaceInput.focus();
            return;
        }

        // 组装最终提交数据
        let finalGoodsType = goodsType === 'other' ? otherType : goodsType;
        let finalPickPlace = pickPlace === 'other' ? otherPlace : pickPlace;

        // 提交成功提示
        alert(`提交成功！
物品名称：${goodsName}
物品类型：${finalGoodsType}
捡到地点：${finalPickPlace}`);
        
        // 重置表单
        document.querySelectorAll('.form-input').forEach(i => i.value = '');
        document.querySelectorAll('.form-select').forEach(s => s.value = '');
        document.querySelector('.form-textarea').value = '';
        uploadArea.innerHTML = `
            <div class="plus">+</div>
            <div class="text">上传图片</div>
            <input type="file" id="fileInput" accept="image/*" hidden>
        `;
        // 隐藏所有其他输入框
        otherTypeInput.style.display = 'none';
        otherPlaceInput.style.display = 'none';
    });
});