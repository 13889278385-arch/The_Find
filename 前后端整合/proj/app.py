"""
拾光 FIND 项目后端主程序
============================================================
这个文件是整个项目的后端入口，负责完成以下工作：
1. 创建并配置 Flask 应用。
2. 初始化 SQLite 数据库。
3. 提供用户注册、登录、退出、获取当前登录用户等认证接口。
4. 提供失物/招领信息的新增、查询、详情、统计等接口。
5. 提供公告读取接口。
6. 提供前端静态页面和上传图片的访问能力。

因为这个项目是“前端 + 后端一体化”的课程项目，所以这里把：
- Web 服务器
- 数据库存取
- 会话登录
- 文件上传
- JSON 接口
都集中写在一个文件中，便于老师验收和同学阅读。
"""

# ------------------------------
# 标准库导入区域
# ------------------------------
# os:      用来读取环境变量等系统信息。
# sqlite3: Python 自带的轻量级数据库模块，本项目用它实现开箱即用的本地数据库。
# uuid:    用来生成唯一文件名，避免不同用户上传同名图片时互相覆盖。
from datetime import datetime  # 生成记录创建时间、公告时间等时间戳。
from pathlib import Path       # 更安全、更清晰地处理文件路径。
import os
import sqlite3
import uuid

# ------------------------------
# 第三方库导入区域
# ------------------------------
# Flask                : Web 框架本体。
# jsonify              : 把 Python 字典自动转成 JSON 响应。
# request              : 读取浏览器提交的数据（表单、JSON、文件）。
# send_from_directory  : 用于返回前端页面和上传图片。
# session              : 用于保存当前登录用户状态。
from flask import Flask, jsonify, request, send_from_directory, session

# werkzeug 是 Flask 底层常用工具库：
# check_password_hash / generate_password_hash：安全处理密码，避免明文保存。
# secure_filename：清理上传文件名，防止出现危险路径或非法字符。
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


# ============================================================
# 一、项目目录相关配置
# ============================================================
# __file__ 表示“当前这个 app.py 文件自己的路径”。
# resolve().parent 表示先转成绝对路径，再取所在文件夹。
# 这样无论你从哪个目录启动 python app.py，这些路径都不会错。
BASE_DIR = Path(__file__).resolve().parent

# 前端页面所在目录。
# 里面存放了 html、css、js、img 等静态资源。
FRONTEND_DIR = BASE_DIR / 'find'

# 数据目录。
# 这里用来存放 SQLite 数据库文件。
DATA_DIR = BASE_DIR / 'data'

# 上传目录。
# 用户上传的物品图片会保存在这里。
UPLOAD_DIR = BASE_DIR / 'uploads'

# 数据库文件的完整路径。
DB_PATH = DATA_DIR / 'find.db'

# 如果 data / uploads 目录不存在，就自动创建。
# exist_ok=True 表示：如果已经存在，不要报错。
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)


# ============================================================
# 二、Flask 应用初始化
# ============================================================
# static_folder 指定静态资源目录，这里直接指向前端目录 find。
# static_url_path='' 表示把静态资源直接挂在根路径下。
# 这样访问 /home.html、/css/common.css、/js/common.js 都能直接拿到文件。
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path='')

# SECRET_KEY 用于 Flask session 的加密签名。
# 正式项目应该放到环境变量里，这里为了演示给了默认值。
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'find-demo-secret-key')

# 限制最大上传大小为 10MB，防止上传超大文件导致服务异常。
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# 告诉 Flask 上传文件保存到哪个目录。
app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)


# ============================================================
# 三、数据库工具函数
# ============================================================
def get_db():
    """
    创建并返回一个 SQLite 数据库连接。

    这里做了两件关键事情：
    1. 连接数据库文件 DB_PATH。
    2. 设置 row_factory = sqlite3.Row。
       这样查询出来的每一行不仅能通过 row[0] 访问，
       也能通过 row['username'] 这种“列名方式”访问，更直观。
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    初始化数据库表结构。

    项目第一次启动时，如果数据库文件存在但没有表，
    或者数据库文件根本不存在，这个函数都会自动建表。

    本项目一共建立三张表：
    1. users   : 用户表
    2. items   : 失物 / 招领信息表
    3. notices : 公告表
    """
    conn = get_db()
    cur = conn.cursor()

    # executescript 适合执行多条 SQL。
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            student_no TEXT,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL CHECK(item_type IN ('lost', 'found')),
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            description TEXT,
            image_path TEXT,
            status TEXT NOT NULL,
            publisher_id INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (publisher_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )

    # 提交事务，让建表操作真正写入数据库。
    conn.commit()
    conn.close()


def seed_data():
    """
    写入演示数据。

    课程项目验收时，如果系统第一次打开就是空白页面，效果会比较差。
    所以这里做了“仅首次插入”的初始化：
    - 如果 notices 表是空的，就插入几条公告。
    - 如果 items 表是空的，就插入几条失物招领示例数据。

    注意：这个函数不会无限重复插入。
    因为它会先查询表里的记录数，只有在“当前表为空”时才插入。
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db()
    cur = conn.cursor()

    # ---------- 初始化公告数据 ----------
    cur.execute('SELECT COUNT(*) AS c FROM notices')
    if cur.fetchone()['c'] == 0:
        notices = [
            ('平台功能更新公告', '本次新增了智能检索、图片上传、动态公示页与个人发布记录模块。', '2026-04-01 09:00:00'),
            ('温馨提示', '请在图书馆、教学楼和食堂妥善保管校园卡、钥匙、耳机等随身物品。', '2026-03-28 10:00:00'),
            ('系统维护完成', '平台后端已接入数据库，支持真实提交与查询。', now),
        ]
        cur.executemany('INSERT INTO notices(title, content, created_at) VALUES (?, ?, ?)', notices)

    # ---------- 初始化失物 / 招领数据 ----------
    cur.execute('SELECT COUNT(*) AS c FROM items')
    if cur.fetchone()['c'] == 0:
        items = [
            ('found', '校园卡', '证件卡片', '一号教学楼', '2026-03-15T10:30', '蓝色挂绳校园卡，已放到值班室。', None, 'claim_open', '2026-03-15 12:00:00'),
            ('lost', '无线耳机', '电子产品', '食堂二楼', '2026-03-15T12:10', '白色耳机盒，右耳机有轻微磨损。', None, 'searching', '2026-03-15 13:20:00'),
            ('found', '钥匙串', '钥匙', '图书馆', '2026-03-14T18:40', '钥匙串上有一个小熊挂件。', None, 'claim_open', '2026-03-14 19:00:00'),
            ('lost', '保温杯', '其他', '生命A实验室', '2026-03-14T08:20', '银灰色保温杯，杯底有姓名缩写。', None, 'searching', '2026-03-14 09:00:00'),
            ('found', '黑色充电宝', '电子产品', '图书馆一层大厅', '2026-03-13T17:30', '已联系失主，归还完成。', None, 'returned', '2026-03-13 18:30:00'),
            ('lost', '学生卡', '证件卡片', '信息学馆B区走廊', '2026-03-12T15:00', '已在平台帮助下找回。', None, 'returned', '2026-03-12 16:10:00'),
        ]
        cur.executemany(
            """
            INSERT INTO items(
                item_type, title, category, location, occurred_at, description,
                image_path, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            items,
        )

    conn.commit()
    conn.close()


# ============================================================
# 四、通用辅助函数
# ============================================================
def json_error(message, code=400):
    """
    统一返回错误 JSON。

    参数：
    - message: 要返回给前端/浏览器的错误提示。
    - code   : HTTP 状态码，默认 400（客户端请求错误）。

    返回格式统一为：
    {
        "success": false,
        "message": "具体错误说明"
    }
    """
    return jsonify({'success': False, 'message': message}), code


def status_label(status):
    """
    把数据库中的英文状态码转换成中文展示文案。

    数据库存的是：
    - claim_open
    - searching
    - returned

    页面更适合显示：
    - 招领中
    - 寻物中
    - 已归还
    """
    mapping = {
        'claim_open': '招领中',
        'searching': '寻物中',
        'returned': '已归还',
    }
    return mapping.get(status, '处理中')


def item_type_label(item_type):
    """
    把物品类型字段转成中文。

    数据库存：
    - found -> 招领
    - lost  -> 寻物
    """
    return '招领' if item_type == 'found' else '寻物'


def row_to_item(row):
    """
    把数据库的一行记录转换成更适合前端使用的字典。

    额外补充三个字段：
    - status_label    : 中文状态
    - item_type_label : 中文类型
    - image_url       : 图片访问地址（如果没有图片则为 None）
    """
    data = dict(row)
    data['status_label'] = status_label(data['status'])
    data['item_type_label'] = item_type_label(data['item_type'])
    data['image_url'] = f"/uploads/{data['image_path']}" if data.get('image_path') else None
    return data


# ============================================================
# 五、静态页面与静态资源路由
# ============================================================
@app.route('/')
def index():
    """
    网站根路径。

    当用户访问 http://127.0.0.1:5000/ 时，
    直接返回前端启动页 index.html。
    """
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """
    访问上传图片。

    前端在显示用户上传图片时，会请求类似：
    /uploads/xxxxxx.png
    这个接口就负责把 uploads 目录中的图片返回给浏览器。
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ============================================================
# 六、系统状态检查接口
# ============================================================
@app.route('/api/health')
def api_health():
    """
    健康检查接口。

    常用于快速判断后端服务是否已经启动成功。
    浏览器或接口工具访问它时，如果返回 success=true，
    说明 Flask 服务正常运行。
    """
    return jsonify({'success': True, 'message': 'backend is running'})


# ============================================================
# 七、用户认证接口
# ============================================================
@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    用户注册接口。

    前端既可能用 JSON 方式提交，也可能用 form 表单方式提交，
    所以这里同时兼容两种读取方式：
    request.get_json(...) or request.form
    """
    payload = request.get_json(silent=True) or request.form
    username = (payload.get('username') or '').strip()
    student_no = (payload.get('student_no') or '').strip()
    password = payload.get('password') or ''

    # ---------- 基础校验 ----------
    if len(username) < 2:
        return json_error('用户名至少 2 个字符。')
    if len(password) < 6:
        return json_error('密码至少 6 位。')

    conn = get_db()
    cur = conn.cursor()

    # ---------- 检查用户名是否已存在 ----------
    cur.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cur.fetchone():
        conn.close()
        return json_error('用户名已存在，请更换。')

    # ---------- 写入新用户 ----------
    # 注意：密码不是明文保存，而是经过 generate_password_hash 加密后再保存。
    cur.execute(
        'INSERT INTO users(username, student_no, password_hash, created_at) VALUES (?, ?, ?, ?)',
        (username, student_no, generate_password_hash(password), datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()

    # ---------- 注册成功后自动登录 ----------
    session['user_id'] = user_id
    session['username'] = username

    return jsonify({
        'success': True,
        'message': '注册成功。',
        'user': {
            'id': user_id,
            'username': username,
            'student_no': student_no,
        }
    })


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    用户登录接口。

    登录流程：
    1. 根据用户名查询数据库。
    2. 用 check_password_hash 校验密码是否正确。
    3. 正确则把用户信息写入 session，表示已登录。
    """
    payload = request.get_json(silent=True) or request.form
    username = (payload.get('username') or '').strip()
    password = payload.get('password') or ''

    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    conn.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return json_error('用户名或密码错误。', 401)

    # 登录成功后，把用户标识保存进 session。
    session['user_id'] = user['id']
    session['username'] = user['username']

    return jsonify({
        'success': True,
        'message': '登录成功。',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'student_no': user['student_no'],
        }
    })


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """
    退出登录接口。

    session.clear() 会清空当前会话中的所有登录信息。
    之后浏览器再访问“我的发布”等需要登录的接口时，就会被认为未登录。
    """
    session.clear()
    return jsonify({'success': True, 'message': '已退出登录。'})


@app.route('/api/auth/me')
def me():
    """
    获取当前登录用户信息。

    这个接口非常适合前端页面初始化时调用：
    - 如果返回 logged_in = True，说明用户已经登录。
    - 如果返回 logged_in = False，说明用户未登录。
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': True, 'logged_in': False, 'user': None})

    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username, student_no, created_at FROM users WHERE id = ?', (user_id,))
    user = cur.fetchone()
    conn.close()

    # 如果 session 里记着 user_id，但数据库已经没有这个用户，
    # 说明会话状态失效，此时清空 session，返回未登录。
    if not user:
        session.clear()
        return jsonify({'success': True, 'logged_in': False, 'user': None})

    return jsonify({'success': True, 'logged_in': True, 'user': dict(user)})


# ============================================================
# 八、物品发布与查询接口
# ============================================================
@app.route('/api/items', methods=['POST'])
def create_item():
    """
    新增失物/招领记录。

    该接口由前端 claim.html（我要招领）和 lost.html（我要寻物）共用。
    数据通过 multipart/form-data 提交，因为它可能带图片文件。
    """
    title = (request.form.get('title') or '').strip()
    category = (request.form.get('category') or '').strip()
    location = (request.form.get('location') or '').strip()
    occurred_at = (request.form.get('occurred_at') or '').strip()
    description = (request.form.get('description') or '').strip()
    item_type = (request.form.get('item_type') or '').strip()

    # ---------- 参数校验 ----------
    if item_type not in {'lost', 'found'}:
        return json_error('item_type 必须是 lost 或 found。')
    if not title:
        return json_error('请填写物品名称。')
    if not category:
        return json_error('请填写物品类别。')
    if not location:
        return json_error('请填写地点。')
    if not occurred_at:
        return json_error('请填写时间。')

    # ---------- 处理图片上传 ----------
    image_path = None
    image = request.files.get('image')
    if image and image.filename:
        # secure_filename 会去除危险字符，但为了避免重名覆盖，
        # 真正保存时还是重新生成 uuid 文件名。
        ext = Path(secure_filename(image.filename)).suffix.lower()

        # 只允许常见图片格式，避免上传可执行脚本等危险文件。
        if ext not in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}:
            return json_error('只支持 jpg、png、gif、webp 图片。')

        image_path = f"{uuid.uuid4().hex}{ext}"
        image.save(UPLOAD_DIR / image_path)

    # ---------- 根据类型自动设置初始状态 ----------
    # 招领(found) 初始状态 -> claim_open
    # 寻物(lost)  初始状态 -> searching
    status = 'claim_open' if item_type == 'found' else 'searching'

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO items(
            item_type, title, category, location, occurred_at, description,
            image_path, status, publisher_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item_type,
            title,
            category,
            location,
            occurred_at,
            description,
            image_path,
            status,
            session.get('user_id'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    )
    item_id = cur.lastrowid
    conn.commit()

    # 插入后再查一遍，返回完整记录给前端。
    cur.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = row_to_item(cur.fetchone())
    conn.close()

    return jsonify({'success': True, 'message': '提交成功。', 'item': item})


@app.route('/api/items/latest')
def latest_items():
    """
    获取最新发布的若干条记录。

    limit 参数由前端决定，但为了防止一次性查太多，
    这里用 max/min 把它限制在 1~50 之间。
    """
    limit = max(1, min(int(request.args.get('limit', 10)), 50))
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM items ORDER BY datetime(created_at) DESC LIMIT ?', (limit,))
    items = [row_to_item(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({'success': True, 'items': items})


@app.route('/api/items/returned')
def returned_items():
    """
    获取“已归还”状态的记录，用于公示页展示温暖归还案例。
    """
    limit = max(1, min(int(request.args.get('limit', 10)), 50))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE status = 'returned' ORDER BY datetime(created_at) DESC LIMIT ?", (limit,))
    items = [row_to_item(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({'success': True, 'items': items})


@app.route('/api/items/search')
def search_items():
    """
    智能检索接口。

    支持三个检索维度：
    1. q         : 关键词（会匹配标题、类别、地点、描述）
    2. item_type : lost / found
    3. status    : claim_open / searching / returned

    这里采用“动态拼接 SQL 条件”的方式：
    - 用户传了什么条件，就拼接什么条件。
    - 用户没传，就不加该条件。
    这样查询非常灵活。
    """
    q = (request.args.get('q') or '').strip()
    item_type = (request.args.get('item_type') or '').strip()
    status = (request.args.get('status') or '').strip()

    conditions = []
    params = []

    # ---------- 关键词模糊匹配 ----------
    if q:
        conditions.append('(title LIKE ? OR category LIKE ? OR location LIKE ? OR description LIKE ?)')
        wildcard = f'%{q}%'
        params.extend([wildcard] * 4)

    # ---------- 类型过滤 ----------
    if item_type in {'lost', 'found'}:
        conditions.append('item_type = ?')
        params.append(item_type)

    # ---------- 状态过滤 ----------
    if status in {'claim_open', 'searching', 'returned'}:
        conditions.append('status = ?')
        params.append(status)

    # ---------- 动态构建 SQL ----------
    sql = 'SELECT * FROM items'
    if conditions:
        sql += ' WHERE ' + ' AND '.join(conditions)
    sql += ' ORDER BY datetime(created_at) DESC, id DESC LIMIT 100'

    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, params)
    items = [row_to_item(row) for row in cur.fetchall()]
    conn.close()

    return jsonify({'success': True, 'count': len(items), 'items': items})


@app.route('/api/items/<int:item_id>')
def item_detail(item_id):
    """
    根据记录 id 获取单条物品详情。
    
    <int:item_id> 是 Flask 的路由参数语法，表示这里只接受整数。
    例如：/api/items/5
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return json_error('未找到对应记录。', 404)

    return jsonify({'success': True, 'item': row_to_item(row)})


# ============================================================
# 九、统计与公告接口
# ============================================================
@app.route('/api/stats/hotspots')
def hotspots():
    """
    高频地点统计接口。

    通过 SQL 的 GROUP BY + COUNT(*) 统计每个地点出现了多少次，
    然后按次数从高到低排序，返回前 10 个热点地点。
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT location, COUNT(*) AS total
        FROM items
        GROUP BY location
        ORDER BY total DESC, location ASC
        LIMIT 10
        """
    )
    data = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({'success': True, 'hotspots': data})


@app.route('/api/notices')
def notices():
    """
    获取公告列表。

    返回最近 20 条公告，按时间倒序排列。
    如果时间相同，再按 id 倒序，保证最新插入的在前面。
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM notices ORDER BY datetime(created_at) DESC, id DESC LIMIT 20')
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({'success': True, 'notices': rows})


@app.route('/api/my/items')
def my_items():
    """
    获取“当前登录用户自己发布过的记录”。

    使用场景：
    - 我的页面 my.html 中展示“我的发布”列表。

    安全逻辑：
    - 如果用户未登录，直接返回 401，提示先登录。
    - 如果已登录，只查询 publisher_id 等于当前用户 id 的记录。
    """
    user_id = session.get('user_id')
    if not user_id:
        return json_error('请先登录。', 401)

    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM items WHERE publisher_id = ? ORDER BY datetime(created_at) DESC, id DESC', (user_id,))
    rows = [row_to_item(row) for row in cur.fetchall()]
    conn.close()

    return jsonify({'success': True, 'items': rows})


# ============================================================
# 十、程序启动前的初始化动作
# ============================================================
# 这两句会在 Flask 服务真正启动前先执行。
# 目的：确保数据库表存在、演示数据存在。
init_db()
seed_data()


# ============================================================
# 十一、程序入口
# ============================================================
if __name__ == '__main__':
    """
    只有当你直接运行 python app.py 时，这里的代码才会执行。
    如果是被其他模块 import，则不会自动启动服务器。

    参数说明：
    - host='127.0.0.1'：仅允许本机访问。
    - port=5000       ：访问端口。
    - debug=True      ：开启调试模式，开发阶段更方便定位问题。
    """
    app.run(host='127.0.0.1', port=5000, debug=True)
