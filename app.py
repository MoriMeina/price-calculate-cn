from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

user = 'root'
password = 'Meina9758'
database = 'price-calculate-cn'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@10.1.0.110:3306/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)


class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255))
    unit = db.Column(db.String(255))
    second_unit = db.Column(db.String(255))
    service = db.Column(db.String(255))
    client = db.Column(db.String(255))
    client_phone = db.Column(db.String(255))


def build_tree_data(services):
    tree_data = []
    city_map = {}
    unit_map = {}
    second_unit_map = {}

    for service in services:
        # 使用城市名作为父节点
        city = service.city or "未知城市"
        unit = service.unit or "未知单位"
        second_unit = service.second_unit or "未知二级单位"
        service_name = service.service or "未知服务"

        # 创建城市节点
        if city not in city_map:
            Top = "top"
            key_value = f"{city}-{Top}"
            city_node = {
                'title': city,
                'value': key_value,  # 使用城市名作为 value
                'key': key_value,  # 使用城市名作为 key
                'children': []
            }
            city_map[city] = city_node
            tree_data.append(city_node)
        else:
            city_node = city_map[city]

        # 创建单位节点
        unit_key = f"{city}-{unit}"  # 使用单位名和 UUID 组合
        if unit_key not in unit_map:
            unit_node = {
                'title': unit,
                'value': unit_key,
                'key': unit_key,  # 保持 key 和 value 一致
                'children': []
            }
            unit_map[unit_key] = unit_node
            city_node['children'].append(unit_node)
        else:
            unit_node = unit_map[unit_key]

        # 创建二级单位节点
        second_unit_key = f"{city}-{unit}-{second_unit}"  # 使用二级单位名和 UUID 组合
        if second_unit_key not in second_unit_map:
            second_unit_node = {
                'title': second_unit,
                'value': second_unit_key,  # 保持 key 和 value 一致
                'key': second_unit_key,  # 保持 key 和 value 一致
                'children': []
            }
            second_unit_map[second_unit_key] = second_unit_node
            unit_node['children'].append(second_unit_node)
        else:
            second_unit_node = second_unit_map[second_unit_key]

        # 创建服务节点，title 使用服务名称
        service_node = {
            'title': service_name,
            'value': service_name,  # 使用 UUID 作为 value
            'key': service_name,  # 使用 UUID 作为 key
        }

        # 在二级单位节点下添加服务节点
        second_unit_node['children'].append(service_node)

    return tree_data


@app.route('/getServiceByTree', methods=['GET'])
def get_tree_data():
    services = Service.query.all()
    tree_data = build_tree_data(services)
    return jsonify(tree_data)


##千万别动

if __name__ == '__main__':
    app.run()
