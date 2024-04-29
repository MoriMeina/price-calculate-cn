from datetime import datetime

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import or_

app = Flask(__name__)
CORS(app)

user = 'root'
password = 'Meina9758'
database = 'price-calculate-cn'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@10.1.0.110:3306/%s' % (user, password, database)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)


class Cost(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(255), primary_key=True)  # uuid
    city = db.Column(db.String(255))  # 区县
    commit_id = db.Column(db.String(255))  # 申请单号
    second_unit = db.Column(db.String(255))  # 二级单位
    unit = db.Column(db.String(255))  # 单位
    service = db.Column(db.String(255))  # 项目名称
    usingfor = db.Column(db.String(255))  # 主机用途
    system = db.Column(db.String(255))  # 主机系统
    ip = db.Column(db.String(255))  # IP地址
    eip = db.Column(db.String(255))  # 弹性IP
    start_time = db.Column(db.DateTime)  # 开始时间
    start_bill_time = db.Column(db.DateTime, nullable=False)  # 计费时间
    bill_subject = db.Column(db.String(255), nullable=False)  # 计费项目
    ssd = db.Column(db.Integer)  # ssd
    hdd = db.Column(db.Integer)  # 高效云盘
    rds_storage = db.Column(db.Integer)  # RDS存储
    oss_storage = db.Column(db.Integer)  # OSS存储
    sec_fee = db.Column(db.Boolean, nullable=False, default=True)  # 默认安全费用
    middleware = db.Column(db.Integer)  # 信创中间件计数
    database_cn = db.Column(db.Integer)  # 信创数据库计数
    dameng = db.Column(db.Integer)  # 达梦数据库
    renda = db.Column(db.Integer)  # 人大金仓数据库
    dongfang = db.Column(db.Integer)  # 东方通中间件
    kingbase = db.Column(db.Integer)  # 金蝶中间件
    price_all = db.Column(db.Integer)  # 所有价格
    bf_changed_price = db.Column(db.Integer)  # 变配前价格
    months = db.Column(db.String(255))  # 总计月份
    visible = db.Column(db.Boolean, nullable=False, default=True)  # 是否可见
    client = db.Column(db.String(255))  # 客户姓名
    client_phone = db.Column(db.String(255))  # 客户手机号
    ischanged = db.Column(db.Boolean)  # 记录变配/注销
    comment = db.Column(db.String(255))  # 备注


class Price(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(255), primary_key=True)
    project = db.Column(db.String(255))
    billing = db.Column(db.String(255))
    format_name = db.Column(db.String(255))
    format = db.Column(db.String(255), unique=True)
    price_with_noelect = db.Column(db.Integer)
    price = db.Column(db.Integer)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(255), primary_key=True)
    city = db.Column(db.String(255))
    unit = db.Column(db.String(255))
    second_unit = db.Column(db.String(255))
    service = db.Column(db.String(255))
    client = db.Column(db.String(255))
    client_phone = db.Column(db.String(255))


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cities = db.Column(db.String(255))
    with_elect = db.Column(db.Boolean, default=False)
    uuid = db.Column(db.String(255), primary_key=True)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(255), primary_key=True)
    product = db.Column(db.String(255))


class System(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(255), primary_key=True)
    system = db.Column(db.String(255))


@app.route('/get_cost', methods=['POST'])
def get_cost():
    data = request.get_json()
    uuid = data.get('uuid')
    cities = data.get('city')
    commit_id = data.get('commit_id')
    second_unit = data.get('second_unit')
    units = data.get('units')
    service = data.get('service')
    usingfor = data.get('usingfor')
    ip = data.get('ip')
    bill_subjects = data.get('type')
    systems = data.get('system')

    query = Cost.query

    if uuid:
        query = query.filter(Cost.uuid == uuid)

    if commit_id:
        if isinstance(commit_id, list):
            commit_id_filters = [Cost.commit_id.like(f"%{cid}%") for cid in commit_id]
            query = query.filter(or_(*commit_id_filters))
        else:
            query = query.filter(Cost.commit_id.like(f"%{commit_id}%"))

    if units:
        if isinstance(units, list):
            unit_filters = [Cost.unit.like(f"%{unit}%") for unit in units]
            query = query.filter(or_(*unit_filters))
        else:
            query = query.filter(Cost.unit.like(f"%{units}%"))

    if second_unit:
        if isinstance(second_unit, list):
            second_unit_filters = [Cost.second_unit.like(f"%{unit}%") for unit in second_unit]
            query = query.filter(or_(*second_unit_filters))
        else:
            query = query.filter(Cost.second_unit.like(f"%{second_unit}%"))

    if service:
        if isinstance(service, list):
            service_filters = [Cost.service.like(f"%{s}%") for s in service]
            query = query.filter(or_(*service_filters))
        else:
            query = query.filter(Cost.service.like(f"%{service}%"))

    if usingfor:
        if isinstance(usingfor, list):
            usingfor_filters = [Cost.usingfor.like(f"%{uf}%") for uf in usingfor]
            query = query.filter(or_(*usingfor_filters))
        else:
            query = query.filter(Cost.usingfor.like(f"%{usingfor}%"))

    if ip:
        if isinstance(ip, list):
            ip_filters = [or_(Cost.ip.like(f"%{ip}%"), Cost.eip.like(f"%{ip}%")) for ip in ip]
            query = query.filter(or_(*ip_filters))
        else:
            query = query.filter(or_(Cost.ip.like(f"%{ip}%"), Cost.eip.like(f"%{ip}%")))

    if bill_subjects:
        if isinstance(bill_subjects, list):
            bill_subject_filters = [Cost.bill_subject.like(f"%{bs}%") for bs in bill_subjects]
            query = query.filter(or_(*bill_subject_filters))
        else:
            query = query.filter(Cost.bill_subject.like(f"%{bill_subjects}%"))

    if systems:
        if isinstance(systems, list):
            system_filters = [getattr(Cost, system_field).like(f"%{sys}%") for sys in systems for system_field in
                              systems]
            query = query.filter(or_(*system_filters))
        else:
            system_filters = [getattr(Cost, system_field).like(f"%{systems}%") for system_field in systems]
            query = query.filter(or_(*system_filters))

    if not (cities or units or second_unit or bill_subjects or systems):
        costs = query.all()
    else:
        costs = query.all()

    cost_data = []
    for cost in costs:
        if cost.renda is not None or cost.dameng is not None or cost.dongfang is not None or cost.kingbase is not None:
            renda = cost.renda if cost.renda is not None else 0
            dameng = cost.dameng if cost.dameng is not None else 0
            dongfang = cost.dongfang if cost.dongfang is not None else 0
            kingbase = cost.kingbase if cost.kingbase is not None else 0
            # Check if the values are not zero
            if renda != 0 or dameng != 0 or dongfang != 0 or kingbase != 0:
                # Get prices for database_cn and middleware
                database_cn_price = get_price('database_cn', cost.city, 'price')
                middleware_price = get_price('middleware', cost.city, 'price')

                # Calculate database_cn_price and middleware_price based on values of renda, dameng, dongfang, and kingbase
                database_cn_price *= (renda + dameng)
                middleware_price *= (dongfang + kingbase)
            else:
                database_cn_price = 0
                middleware_price = 0
        else:
            database_cn_price = 0
            middleware_price = 0

        # Other calculations remain the same
        city_data = City.query.filter_by(cities=cost.city).first()
        if city_data:
            with_elect = city_data.with_elect
        else:
            with_elect = False

        if not with_elect:
            price = get_price(cost.bill_subject, cost.city, 'price_with_noelect')
        else:
            price = get_price(cost.bill_subject, cost.city, 'price')

        cloud_storage_price = 0
        if cost.ssd:
            ssd_price = get_price('ssd', cost.city, 'price')
            cloud_storage_price += (cost.ssd / 100) * ssd_price
        if cost.hdd:
            hdd_price = get_price('hdd', cost.city, 'price')
            cloud_storage_price += (cost.hdd / 100) * hdd_price
        if cost.rds_storage:
            rds_price = get_price('rds_storage', cost.city, 'price')
            cloud_storage_price += (cost.rds_storage / 100) * rds_price
        if cost.oss_storage:
            oss_price = get_price('oss', cost.city, 'price')
            # oss_price = 0  # 如果计费项目为 'oss'，直接返回 0
            cloud_storage_price += (cost.oss_storage / 1000) * oss_price

        sec_fee_value = get_sec_fee_value(cost.sec_fee)

        sec_fee = bool(cost.sec_fee)
        visible = bool(cost.visible)
        ischanged = bool(cost.ischanged)

        client_phone = cost.client_phone.decode('utf-8') if isinstance(cost.client_phone, bytes) else cost.client_phone

        ssd = cost.ssd if cost.ssd is not None else 0
        hdd = cost.hdd if cost.hdd is not None else 0
        rds_storage = cost.rds_storage if cost.rds_storage is not None else 0
        oss_storage = cost.oss_storage if cost.oss_storage is not None else 0

        # 检查中间件和数据库的值是否大于零，大于零表示存在，应返回对应的价格，否则返回0
        middleware_price = middleware_price if middleware_price > 0 else 0
        database_cn_price = database_cn_price if database_cn_price > 0 else 0

        dameng = cost.dameng if cost.dameng is not None else 0
        renda = cost.renda if cost.renda is not None else 0
        dongfang = cost.dongfang if cost.dongfang is not None else 0
        kingbase = cost.kingbase if cost.kingbase is not None else 0

        cost_data.append({
            'key': cost.uuid,
            'city': cost.city,
            'commit_id': cost.commit_id,
            'second_unit': cost.second_unit,
            'unit': cost.unit,
            'service': cost.service,
            'usingfor': cost.usingfor,
            'system': cost.system,
            'ip': cost.ip,
            'eip': cost.eip,
            'start_time': cost.start_time,
            'start_bill_time': cost.start_bill_time,
            'bill_subject': cost.bill_subject,
            'ssd': ssd,
            'hdd': hdd,
            'rds_storage': rds_storage,
            'oss_storage': oss_storage,
            'sec_fee': sec_fee,
            'ItemPrice': price if cost.bill_subject != 'oss' else 0,  # 如果计费项目为 'oss'，直接返回 0
            'cloudStoragePrice': cloud_storage_price,
            'middleware_price': middleware_price,
            'database_cn_price': database_cn_price,
            'bf_changed_price': cost.bf_changed_price,
            'months': cost.months,
            'visible': visible,
            'client': cost.client,
            'client_phone': client_phone,
            'ischanged': ischanged,
            'comment': cost.comment,
            'sec_fee_value': sec_fee_value,
            'dameng': dameng,
            'renda': renda,
            'dongfang': dongfang,
            'kingbase': kingbase,
            'remark': cost.comment
        })

    return jsonify(cost_data)


def get_price(bill_subject, city, price_field):
    price_entry = Price.query.filter_by(format=bill_subject).first()  # 正确使用 format 字段进行查询
    if price_entry:
        city_data = City.query.filter_by(cities=city).first()
        if city_data:
            with_elect = city_data.with_elect
            if not with_elect:
                return getattr(price_entry, price_field)
            else:
                return getattr(price_entry, price_field)
    return 0  # 如果找不到价格信息，默认返回0


def get_sec_fee_value(sec_fee):
    if sec_fee:
        return Price.query.filter_by(format='sec_fee').first().price
    else:
        return 0


@app.route('/add_cost', methods=['POST'])
def add_cost():
    # 从前端请求中获取数据
    data = request.json

    # 解析数据
    service_name = data.get('service')

    # 查询Service表获取相关信息
    service_info = Service.query.filter_by(service=service_name).first()

    # 如果查询结果为空，返回错误信息
    if service_info is None:
        return jsonify({'error': 'Service not found'}), 404

    # 解析Service表中的相关信息
    unit = service_info.unit
    second_unit = service_info.second_unit
    client = service_info.client
    client_phone = service_info.client_phone
    city = service_info.city  # 获取城市信息

    # 解析其他字段
    commit_id = data.get('commit_id')
    usingfor = data.get('usingfor')
    ip = data.get('ip')
    eip = data.get('eip')
    start_time = datetime.strptime(data.get('start_time'), '%Y-%m-%d')
    start_bill_time = datetime.strptime(data.get('start_bill_time'), '%Y-%m-%d')
    ssd = data.get('ssd')
    hdd = data.get('hdd')
    rds_storage = data.get('rds_storage')
    oss_storage = data.get('oss_storage')
    comment = data.get('comment')
    bill_subject = data.get('bill_subject')  # 解析 bill_subject 字段

    # 创建 Cost 对象并保存到数据库
    cost = Cost(city=city, commit_id=commit_id, unit=unit, second_unit=second_unit,
                service=service_name, usingfor=usingfor, ip=ip, eip=eip,
                start_time=start_time, start_bill_time=start_bill_time,
                ssd=ssd, hdd=hdd, rds_storage=rds_storage, oss_storage=oss_storage,
                client=client, client_phone=client_phone, comment=comment,
                bill_subject=bill_subject)  # 将解析的 bill_subject 传递给 Cost 对象

    # 保存到数据库
    db.session.add(cost)
    db.session.commit()

    # 返回成功消息
    return jsonify({'message': 'Cost added successfully'})


# 查询价格（用于修改价格页面）#TODO
@app.route('/get_prices', methods=['GET'])
def get_prices():
    prices = Price.query.all()

    price_data = []
    for price in prices:
        price_data.append({
            'format': price.format,
            'price_with_noelect': price.price_with_noelect,
            'price': price.price
        })

    return jsonify(price_data)


@app.route('/city_filter', methods=['GET'])
def city_filter():
    cities = City.query.all()
    city_data = []
    for city in cities:
        city_data.append({
            'text': city.cities,
            'value': city.cities
        })
    return jsonify(city_data)


@app.route('/subject_filter', methods=['GET'])
def subject_filter():
    prices = Price.query.filter(Price.format != 'sec_fee', Price.format != 'middleware',
                                Price.format != 'database_cn').all()
    price_data = [{
        'text': price.format,
        'value': price.format
    } for price in prices]
    return jsonify(price_data)


@app.route('/city_choose', methods=['GET'])
def city_choose():
    cities = City.query.all()
    city_data = []
    for city in cities:
        city_data.append({
            'label': city.cities,
            'value': city.cities
        })
    return jsonify(city_data)


@app.route('/get_product', methods=['GET'])
def get_product():
    products = Product.query.all()
    product_data = []
    for product in products:
        product_data.append({
            'label': product.product,
            'value': product.product
        })
    return jsonify(product_data)


@app.route('/get_ecs', methods=['GET'])
def get_ecs():
    ecses = Price.query.filter_by(project='ECS')
    ecs_data = []
    for ecs in ecses:
        ecs_data.append({
            'label': ecs.format,
            'value': ecs.format
        })
    return jsonify(ecs_data)


@app.route('/get_rds', methods=['GET'])
def get_rds():
    rdses = Price.query.filter_by(project='RDS')
    rds_data = []
    for rds in rdses:
        rds_data.append({
            'label': rds.format,
            'value': rds.format
        })
    return jsonify(rds_data)


@app.route('/get_system', methods=['GET'])
def get_system():
    systems = System.query.all()
    system_data = []
    for system in systems:
        system_data.append({
            'label': system.system,
            'value': system.system
        })
    return jsonify(system_data)


@app.route('/get_service', methods=['POST'])
def get_service():
    data = request.get_json()
    cities = data.get('city')

    # 使用city来过滤Service表中的内容
    filtered_services = Service.query.filter_by(city=cities).all()

    # 将过滤后的结果转换为字典列表
    service_data = []
    for service in filtered_services:
        service_data.append({
            'city': service.city,
            'unit': service.unit,
            'second_unit': service.second_unit,
            'service': service.service
        })

    # 构建树状结构
    tree_structure = {}

    for entry in service_data:
        unit = entry["unit"]
        second_unit = entry["second_unit"]
        service = entry["service"]

        if unit not in tree_structure:
            tree_structure[unit] = {"title": unit, "value": unit, "children": []}

        if second_unit is None:
            tree_structure[unit]["children"].append({"title": service, "value": service})
        else:
            if second_unit not in tree_structure[unit]["children"]:
                tree_structure[unit]["children"][second_unit] = {"title": second_unit, "value": second_unit,
                                                                 "children": []}

            tree_structure[unit]["children"][second_unit]["children"].append({"title": service, "value": service})

    # 返回符合条件的Service表中的内容给前端
    return jsonify(list(tree_structure.values()))


if __name__ == '__main__':
    app.run()
