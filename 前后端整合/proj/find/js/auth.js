// ============================================================
// auth.js
// 作用：处理“登录”和“注册”两个页面的前端交互逻辑。
// ============================================================

/**
 * 通用认证请求函数。
 *
 * 为什么单独封装？
 * 因为登录和注册本质上都是：
 * 1. 向后端发送 POST 请求
 * 2. 接收 JSON 结果
 * 3. 判断是否成功
 * 4. 失败则抛出错误给外层捕获
 */
async function handleAuth(endpoint, payload) {
    const res = await fetch(endpoint, {
        method: 'POST',

        // 告诉后端：本次请求体是 JSON。
        headers: { 'Content-Type': 'application/json' },

        // 把 JavaScript 对象转换成 JSON 字符串。
        body: JSON.stringify(payload),
    });

    const data = await res.json();

    // 只要 HTTP 状态码不正常，或者后端 success=false，
    // 就统一抛出异常，让调用方进入 catch 分支。
    if (!res.ok || !data.success) {
        throw new Error(data.message || '操作失败');
    }

    return data;
}

// 等页面 DOM 结构全部加载完成后再绑定事件，
// 避免一开始就找不到表单节点。
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    // ------------------------------
    // 登录表单提交事件
    // ------------------------------
    loginForm?.addEventListener('submit', async (e) => {
        e.preventDefault(); // 阻止浏览器默认提交，改为 Ajax 提交。

        const username = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value;

        try {
            await handleAuth('/api/auth/login', { username, password });
            alert('登录成功');

            // 登录成功后跳转到首页。
            window.location.href = 'home.html';
        } catch (error) {
            alert(error.message);
        }
    });

    // ------------------------------
    // 注册表单提交事件
    // ------------------------------
    registerForm?.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('registerUsername').value.trim();
        const studentNo = document.getElementById('registerStudentNo').value.trim();
        const password = document.getElementById('registerPassword').value;

        try {
            // 注意：后端字段名是 student_no，所以这里显式映射。
            await handleAuth('/api/auth/register', { username, student_no: studentNo, password });
            alert('注册成功，已自动登录');
            window.location.href = 'home.html';
        } catch (error) {
            alert(error.message);
        }
    });
});
