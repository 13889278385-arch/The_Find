# 拾光 FIND 前后端整合项目（详注释版）

## 1. 项目简介
这是一个校园失物招领系统示例项目，包含：
- 前端页面（HTML + CSS + JavaScript）
- 后端服务（Flask）
- 本地数据库（SQLite）
- 图片上传功能
- 注册、登录、检索、个人发布、公示页面等模块

这份版本额外特点：
- 所有核心代码都加了更详细的中文注释
- 更适合作为课程答辩、老师检查、同学复盘时阅读

## 2. 目录说明
- `app.py`：后端主程序，负责接口、数据库、登录、上传等功能
- `find/`：前端页面目录，包含 html / css / js / img
- `data/find.db`：SQLite 数据库文件
- `uploads/`：用户上传图片保存目录
- `requirements.txt`：Python 依赖清单
- `run.bat`：Windows 一键运行脚本
- `run.sh`：Linux/macOS 一键运行脚本

## 3. 运行方法（推荐 venv）
```bash
python -m venv venv
# Windows PowerShell 激活： .\venv\Scripts\Activate.ps1
# Windows CMD 激活：        venv\Scripts\activate.bat
# Linux / macOS 激活：      source venv/bin/activate

pip install -r requirements.txt
python app.py
```

启动后访问：
`http://127.0.0.1:5000/`

## 4. 默认能力
- 用户注册 / 登录 / 退出
- 我要招领 / 我要寻物表单提交
- 图片上传
- 最新公示
- 智能检索
- 高频丢失地点统计
- 已成功归还公示
- 我的发布记录

## 5. 数据库说明
项目使用 SQLite，不需要额外安装 MySQL。
第一次启动时会自动创建数据表，并自动写入部分演示数据。
