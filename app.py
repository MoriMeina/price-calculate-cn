from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import and_, or_
import json

app = Flask(__name__)
CORS(app)

user = 'aurora'
password = 'srwtxb16saj9ncg'
database = 'price-calculate-cn'
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@10.11.203.118:3306/{database}?connect_timeout=50'
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
    add_fee = db.Column(db.String(255))
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


class AddFee(db.Model):
    __tablename__ = 'add_fee'
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(255))
    price = db.Column(db.Float)  # 使用浮点数来表示价格


class YearVersion(db.Model):
    __tablename__ = 'year_version'
    id = db.Column(db.Integer, primary_key=True)
    year_version = db.Column(db.String(255), primary_key=True)


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
            key_value = f"{city}"
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


@app.route('/getAllService', methods=['GET'])
def get_all_usingFor():
    usingFor = db.session.query(Service.service).distinct().all()
    # 将查询结果转换为单一列表
    using_for_list = [uf[0] for uf in usingFor]
    return jsonify(using_for_list)


@app.route('/DescribeCost', methods=['POST'])
def calculate_price():
    data = request.json
    cost_month = data.get('cost_month')
    service = data.get('service')
    year_version = data.get('year_version')
    search = data.get('search')
    search_type = data.get('search_type')

    if isinstance(cost_month, list) and len(cost_month) == 2:
        start_month = datetime.strptime(cost_month[0], '%Y-%m').date()
        end_month = datetime.strptime(cost_month[1], '%Y-%m').date()
    else:
        return jsonify({'error': 'Invalid cost_month format. It should be a list with two date strings.'}), 400

    filters = [Cost.service.in_(service), Price.version == year_version]

    if search and search_type:
        if search_type == '资源名':
            filters.append(Cost.usingfor.contains(search))
        elif search_type == 'ip':
            filters.append(or_(Cost.ip.contains(search), Cost.eip.contains(search)))

    query = db.session.query(Cost, Price, Service).join(Price, Price.format == Cost.bill_subject) \
        .join(Service, Service.service == Cost.service).filter(and_(*filters))
    costs = query.all()

    result = []

    for cost, price, service in costs:
        city = City.query.filter_by(cities=cost.city).first()
        base_price = price.price_with_elect if city.with_elect else price.price

        monthly_price = base_price

        # 获取每个存储类型的价格时，根据城市判断使用带电费或不带电费的价格

        # 计算 SSD 的价格
        if cost.ssd > 0:
            ssd_price_entry = Price.query.filter_by(format='ssd', version=year_version).first()
            ssd_price = ssd_price_entry.price_with_elect if city.with_elect else ssd_price_entry.price
            monthly_price += (cost.ssd / 100) * ssd_price

        # 计算 HDD 的价格
        if cost.hdd > 0:
            hdd_price_entry = Price.query.filter_by(format='hdd', version=year_version).first()
            hdd_price = hdd_price_entry.price_with_elect if city.with_elect else hdd_price_entry.price
            monthly_price += (cost.hdd / 100) * hdd_price

        # 计算 RDS 存储的价格
        if cost.rds_storage > 0:
            rds_price_entry = Price.query.filter_by(format='rds', version=year_version).first()
            rds_price = rds_price_entry.price_with_elect if city.with_elect else rds_price_entry.price
            monthly_price += (cost.rds_storage / 100) * rds_price

        # 计算 OSS 存储的价格
        if cost.oss_storage > 0:
            oss_price_entry = Price.query.filter_by(format='oss', version=year_version).first()
            oss_price = oss_price_entry.price_with_elect if city.with_elect else oss_price_entry.price
            monthly_price += (cost.oss_storage / 1000) * oss_price

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

        add_fee_product_list = []
        if cost.add_fee:
            add_fees = json.loads(cost.add_fee).get('add_fee', [])
            for fee in add_fees:
                for fee_id, quantity in fee.items():
                    add_fee_entry = AddFee.query.get(fee_id)
                    if add_fee_entry:
                        monthly_price += add_fee_entry.price * quantity
                        add_fee_product_list.append(f"{add_fee_entry.product}: {quantity}")

        add_fee_products = ", ".join(add_fee_product_list)

        start_date = cost.start_bill_time

        if cost.ischangedtime:
            is_changed_time = cost.ischangedtime
            is_changed_date_str = str(is_changed_time).split(' ')[0]
            is_changed_date = datetime.strptime(is_changed_date_str, '%Y-%m-%d').date()

            if start_month <= is_changed_date <= end_month:
                if start_date < start_month:
                    month_difference = (is_changed_date - start_month).days // 30 + 1
                else:
                    month_difference = (is_changed_date - start_date).days // 30 + 1
            elif is_changed_date > end_month:
                month_difference = (end_month - start_date).days // 30 + 1
            else:
                month_difference = 0
        else:
            if start_month <= start_date <= end_month:
                month_difference = (end_month.year - start_date.year) * 12 + end_month.month - start_date.month + 1
            elif start_date < start_month:
                month_difference = (end_month.year - start_month.year) * 12 + end_month.month - start_month.month + 1
            else:
                month_difference = 0

        total_price = monthly_price * month_difference

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
            'system': cost.system,
            'start_time': str(cost.start_time),
            'storage': storage_str,
            'comment': cost.comment,
            'ischanged': cost.ischanged,
            'monthly_price': monthly_price,
            'cost_month': month_difference,
            'all_price': total_price,
            'add_fee': add_fee_products,
            'client': service.client,
            'client_phone': service.client_phone,
        })

    return jsonify(result)


@app.route('/GetYearVersion', methods=['GET'])
def get_year_version():
    year_versions = YearVersion.query.all()
    result = [{'value': yv.year_version, 'label': yv.year_version} for yv in year_versions]
    return jsonify(result)


@app.route('/getFormatsByProduct', methods=['GET'])
def get_formats_by_product():
    product = request.args.get('product')

    if not product:
        return jsonify([]), 200

    # 查询 Price 表中 format 字段与传入的 product 匹配的记录
    formats = db.session.query(Price.format).filter_by(project=product).distinct().all()

    # 将查询结果格式化为 [{'value': format, 'label': format}] 格式
    result = [{'value': fmt[0], 'label': fmt[0]} for fmt in formats]

    return jsonify(result)


@app.route('/GetAddFee', methods=['GET'])
def get_Add_Fee():
    add_fee_list = AddFee.query.all()
    result = [{'key': af.id, 'value': af.id, 'label': af.product} for af in add_fee_list]
    return jsonify(result)


@app.route('/CreateCost', methods=['POST'])
def create_cost():
    data = request.json

    # 拆分 service_unit 字段
    service_unit = data.get("service_unit", "")
    service_unit_parts = service_unit.split("-")
    city = service_unit_parts[0] if len(service_unit_parts) > 0 else None
    unit = service_unit_parts[1] if len(service_unit_parts) > 1 else None
    second_unit = service_unit_parts[2] if len(service_unit_parts) > 2 else None

    # 获取其他字段
    service_name = data.get("service")
    usingfor = data.get("usingfor")
    commit_id = data.get("commit_id")
    payment = data.get("payment")
    client = data.get("client")
    client_phone = data.get("client_phone")
    system = data.get("system")
    ip = data.get("ip")
    eip = data.get("eip")
    start_time = data.get("start_time")
    start_time = datetime.fromisoformat(start_time[:-1]) if start_time else None
    bill_subject = data.get("bill_subject")
    ssd = data.get("ssd")
    hdd = data.get("hdd")
    rds_storage = data.get("rds_storage")
    oss_storage = data.get("oss_storage")
    add_fee = data.get("addFee")

    # 查询 Service 表以检查 service 是否存在
    service_exists = db.session.query(Service).filter_by(service=service_name).first()

    if not service_exists:
        # 如果 service 不存在，则检查 city 是否存在于 City 表中
        city_exists = db.session.query(City).filter_by(cities=city).first()
        if not city_exists:
            # 如果 city 不存在于 City 表中，则插入 city
            new_city = City(cities=city, with_elect=False)  # 你可以根据需求设置 with_elect 字段的值
            db.session.add(new_city)
            db.session.commit()

        # 插入 service 到 Service 表中
        new_service = Service(
            city=city,
            unit=unit,
            second_unit=second_unit,
            service=service_name,
            client=client,
            client_phone=client_phone
        )
        db.session.add(new_service)
        db.session.commit()

    # 处理 add_fee 字段，将其包装为字典并转换为 JSON 字符串
    add_fee_json = json.dumps({"add_fee": add_fee}) if add_fee else None

    # 无论 service 是否已存在，现在将数据插入 Cost 表中
    cost = Cost(
        city=city,
        payment=payment,
        commit_id=commit_id,
        unit=unit,
        second_unit=second_unit,
        service=service_name,
        usingfor=usingfor,
        system=system,
        ip=ip,
        eip=eip,
        start_time=start_time,
        bill_subject=bill_subject,
        ssd=ssd if ssd else 0,
        hdd=hdd if hdd else 0,
        rds_storage=rds_storage if rds_storage else 0,
        oss_storage=oss_storage if oss_storage else 0,
        add_fee=add_fee_json,
        ischanged=None,
        ischangedtime=None,
        comment=None
    )

    # 将 Cost 实例添加到数据库会话
    db.session.add(cost)
    db.session.commit()

    return jsonify({"message": "Data processed and saved successfully."}), 201


if __name__ == '__main__':
    app.run(debug=True)
