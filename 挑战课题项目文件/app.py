from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'lost_and_found.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 数据库模型
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 初始化数据库
with app.app_context():
    db.create_all()

@app.route('/api/items', methods=['GET'])
def get_items():
    items = Item.query.order_by(Item.created_at.desc()).all()
    # 同时返回 location 和 info 字段，确保前端怎么读都不会错
    return jsonify([{
        "id": i.id, 
        "name": i.name, 
        "location": i.location,
        "info": i.location  # 兼容前端可能使用的 info 字段
    } for i in items])

@app.route('/api/items', methods=['POST'])
def add_item():
    data = request.json
    name = data.get('name')
    # 兼容前端传来的 info 或 location
    location = data.get('info') or data.get('location')
    
    if not name or not location:
        return jsonify({"error": "数据不完整"}), 400
    
    new_item = Item(name=name, location=location)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "发布成功", "id": new_item.id}), 201

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "删除成功"}), 200
    return jsonify({"error": "未找到记录"}), 404

if __name__ == '__main__':
    app.run(debug=True)