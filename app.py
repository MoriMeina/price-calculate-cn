from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import and_, or_

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


class Cost(db.Model):
    __tablename__ = 'cost'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255))
    payment = db.Column(db.String(255))
    commit_id = db.Column(db.String(255))
    unit = db.Column(db.String(255))
    second_unit = db.Column(db.String(255))
    service = db.Column(db.String(255))
    usingfor = db.Column(db.String(255))
    system = db.Column(db.String(255))
    ip = db.Column(db.String(255))
    eip = db.Column(db.String(255))
    start_time = db.Column(db.Date)
    start_bill_time = db.Column(db.Date)
    bill_subject = db.Column(db.String(255))
    ssd = db.Column(db.Integer)
    hdd = db.Column(db.Integer)
    rds_storage = db.Column(db.Integer)
    oss_storage = db.Column(db.Integer)
    sec_fee = db.Column(db.Boolean)
    add_fee = db.Column(db.String(255))
    visible = db.Column(db.Boolean)
    ischanged = db.Column(db.Boolean)
    ischangedtime = db.Column(db.DateTime)
    comment = db.Column(db.Text)


class Price(db.Model):
    __tablename__ = 'price'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), nullable=False)
    project = db.Column(db.String(255))
    billing = db.Column(db.String(255))
    format_name = db.Column(db.String(255))
    format = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer)
    price_with_elect = db.Column(db.Integer)
    version = db.Column(db.String(255), nullable=False)


class City(db.Model):
    __tablename__ = 'city'
    cities = db.Column(db.String(255), primary_key=True)
    with_elect = db.Column(db.Boolean)


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


@app.route('/DescribeCost', methods=['POST'])
def calculate_price():
    data = request.json

    # 获取请求的参数
    cost_month = data.get('cost_month')
    service = data.get('service')
    year_version = data.get('year_version')
    search = data.get('search')
    search_type = data.get('search_type')

    # 确保 cost_month 是一个包含两个日期字符串的列表
    if isinstance(cost_month, list) and len(cost_month) == 2:
        start_month = datetime.strptime(cost_month[0], '%Y-%m').date()
        end_month = datetime.strptime(cost_month[1], '%Y-%m').date()
    else:
        return jsonify({'error': 'Invalid cost_month format. It should be a list with two date strings.'}), 400

    # 基本查询过滤条件
    filters = [Cost.service.in_(service), Price.version == year_version]

    # 处理搜索类型和内容
    if search and search_type:
        if search_type == '资源名':
            filters.append(Cost.usingfor.contains(search))
        elif search_type == 'ip':
            filters.append(or_(Cost.ip.contains(search), Cost.eip.contains(search)))

    # 添加正确的 join 条件
    query = db.session.query(Cost, Price).join(Price, Price.format == Cost.bill_subject).filter(and_(*filters))

    # 获取所有符合条件的记录
    costs = query.all()

    # 准备返回数据的列表
    result = []

    # 处理每个cost项
    for cost, price in costs:
        # 获取计费规则
        city = City.query.filter_by(cities=cost.city).first()

        # 判断是否含电费
        base_price = price.price_with_elect if city.with_elect else price.price

        # 计算存储计费
        storage = []
        if cost.ssd > 0:
            storage.append(f"ECS_SSD:{cost.ssd}GB")
        if cost.hdd > 0:
            storage.append(f"ECS_高效云盘:{cost.hdd}GB")
        if cost.rds_storage > 0:
            storage.append(f"RDS_SSD:{cost.rds_storage}GB")
        if cost.oss_storage > 0:
            storage.append(f"OSS:{cost.oss_storage}GB")
        storage_str = ", ".join(storage)

        # 计算月费用
        monthly_price = base_price
        monthly_price += (cost.ssd / 100) * base_price
        monthly_price += (cost.hdd / 100) * base_price
        monthly_price += (cost.rds_storage / 100) * base_price
        monthly_price += (cost.oss_storage / 1000) * base_price

        # 计算总费用
        start_date = cost.start_bill_time

        # 处理计费逻辑
        if cost.ischangedtime:  # 忽略 changedtime 的记录
            is_changed_time = cost.ischangedtime
            is_changed_date_str = str(is_changed_time).split(' ')[0]  # 获取日期部分
            is_changed_date = datetime.strptime(is_changed_date_str, '%Y-%m-%d').date()

            if start_month <= is_changed_date <= end_month:
                if start_date < start_month:
                    month_difference = (is_changed_date - start_month).days // 30 + 1
                else:
                    month_difference = (is_changed_date - start_date).days // 30 + 1
            elif is_changed_date > end_month:
                month_difference = (end_month - start_date).days // 30 + 1
            else:
                month_difference = 0  # is_changed在请求范围之前
        else:  # 没有is_changed，使用原来的逻辑
            if start_month <= start_date <= end_month:
                month_difference = (end_month.year - start_date.year) * 12 + end_month.month - start_date.month + 1
            elif start_date < start_month:
                month_difference = (end_month.year - start_month.year) * 12 + end_month.month - start_month.month + 1
            else:
                month_difference = 0  # 不在请求时间段内

        # 计算总费用
        total_price = monthly_price * month_difference

        # 构建返回结果字典
        result.append({
            'key': cost.uuid,
            'resource_type': price.project,
            'city': cost.city,
            'payment': cost.payment,
            'commit_id': cost.commit_id,
            'unit': cost.unit,
            'second_unit': cost.second_unit,
            'service': cost.service,
            'usingfor': cost.usingfor,
            'subject': cost.bill_subject,
            'ip': cost.ip,
            'eip': cost.eip,
            'start_time': cost.start_time,
            'storage': storage_str,
            'comment': cost.comment,
            'visible': cost.visible,
            'monthly_price': monthly_price,
            'cost_month': month_difference,
            'all_price': total_price,
        })

    return jsonify(result)


if __name__ == '__main__':
    app.run()
