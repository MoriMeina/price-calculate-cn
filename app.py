from datetime import datetime
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import and_, or_
import json

from sqlalchemy.exc import IntegrityError

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
    id = db.Column(db.Integer, primary_key=True)
    cities = db.Column(db.String(255))
    with_elect = db.Column(db.Boolean)
    uuid = db.Column(db.String(255))


class AddFee(db.Model):
    __tablename__ = 'add_fee'
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(255))
    price = db.Column(db.Float)
    version = db.Column(db.String(255))


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


#
#
#
# 树状返回区县、单位、二级单位、服务信息
#
#
#


@app.route('/getServiceByTree', methods=['GET'])
def get_tree_data():
    services = Service.query.all()
    tree_data = build_tree_data(services)
    return jsonify(tree_data)


#
#
#
# 获取全部IRS系统接口
#
#
#

@app.route('/getAllService', methods=['GET'])
def get_all_usingFor():
    usingFor = db.session.query(Service.service).distinct().all()
    # 将查询结果转换为单一列表
    using_for_list = [uf[0] for uf in usingFor]
    return jsonify(using_for_list)


#
#
#
# 计费变配接口
#
#
#
@app.route('/ModifyCost', methods=['POST'])
def modify_cost():
    data = request.get_json()

    uuid = data.get('uuid')
    commit_id = data.get('commit_id')
    system = data.get('system')
    ip = data.get('ip')
    eip = data.get('eip')
    changed_time = data.get('changed_time')
    bill_subject = data.get('bill_subject')
    ssd = data.get('ssd')
    hdd = data.get('hdd')
    rds_storage = data.get('rds_storage')
    oss_storage = data.get('oss_storage')
    get_addFee = data.get('addFee')
    comment = data.get('comment')

    # 查找现有记录
    existing_cost = Cost.query.filter_by(uuid=uuid).first()

    if not existing_cost:
        return jsonify({"message": "No cost record found with the provided UUID"}), 404

    # 更新现有记录的ischanged和ischangedtime字段
    existing_cost.ischanged = True
    existing_cost.comment = comment
    existing_cost.ischangedtime = datetime.strptime(changed_time, '%Y-%m-%d %H:%M:%S')

    add_fee_json = json.dumps({"add_fee": get_addFee}) if get_addFee else None

    # 复制现有记录，创建一个新的Cost记录
    new_cost = Cost(
        uuid=existing_cost.uuid,
        city=existing_cost.city,
        payment=existing_cost.payment,
        commit_id=commit_id,
        unit=existing_cost.unit,
        second_unit=existing_cost.second_unit,
        service=existing_cost.service,
        usingfor=existing_cost.usingfor,
        system=system,
        ip=ip,
        eip=eip,
        start_time=changed_time,
        start_bill_time=existing_cost.start_bill_time,
        bill_subject=bill_subject,
        ssd=ssd if ssd else 0,
        hdd=hdd if hdd else 0,
        rds_storage=rds_storage if rds_storage else 0,
        oss_storage=oss_storage if oss_storage else 0,
        add_fee=add_fee_json,  # 存储为字符串
        ischanged=None,
        ischangedtime=None,
    )

    db.session.add(new_cost)
    db.session.commit()

    return jsonify({"message": "Cost record updated successfully"}), 200


#
#
#
# 注销计费接口
#
#
#
@app.route('/CancelCost', methods=['POST'])
def cancel_cost():
    try:
        # 获取前端传递的数据
        data = request.get_json()
        uuid = data.get('uuid')
        cancel_time = data.get('cancel_time')
        comment = data.get('comment')

        # 检查是否传递了必要的参数
        if not uuid or not cancel_time:
            return jsonify({"error": "UUID and cancel_time are required"}), 400

        # 查找匹配的cost记录
        cost_record = Cost.query.filter_by(uuid=uuid).first()

        if not cost_record:
            return jsonify({"error": "No record found for the provided UUID"}), 404

        # 更新记录
        cost_record.ischanged = 0
        cost_record.ischangedtime = datetime.strptime(cancel_time, '%Y-%m-%d %H:%M:%S')
        cost_record.comment = comment

        # 提交更改到数据库
        db.session.commit()

        return jsonify({"message": "Cost record updated successfully"}), 200

    except Exception as e:
        db.session.rollback()  # 回滚数据库事务以防止数据不一致
        return jsonify({"error": str(e)}), 500


#
#
#
# 计费表读取接口
#
#
#

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
        .join(Service, Service.service == Cost.service).filter(and_(*filters)) \
        .order_by(Cost.id.desc())
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

        # 计算附加费用时加入 year_version 过滤
        add_fee_product_list = []
        if cost.add_fee:
            add_fees = json.loads(cost.add_fee).get('add_fee', [])
            for fee in add_fees:
                for fee_id, quantity in fee.items():
                    add_fee_entry = AddFee.query.filter_by(id=fee_id,
                                                           version=year_version).first()  # 加入 year_version 过滤
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


#
#
#
# 获取计费版本接口（从year_version表中获取）
#
#
#
@app.route('/GetYearVersion', methods=['GET'])
def get_year_version():
    year_versions = YearVersion.query.all()
    result = [{'value': yv.year_version, 'label': yv.year_version} for yv in year_versions]
    return jsonify(result)


#
#
#
# 根据计费版本获取产品列表接口（从price表中获取）
#
#
#
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


#
#
#
# 根据计费版本获取产品列表接口（从addFee表中获取）
#
#
#

@app.route('/GetAddFee', methods=['GET'])
def get_Add_Fee():
    version = request.args.get('addVersion')
    add_fee_list = AddFee.query.filter_by(version=version)
    result = [{'key': af.id, 'value': af.id, 'label': af.product} for af in add_fee_list]
    return jsonify(result)


#
#
#
# 新增计费接口
#
#
#
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
    get_addFee = data.get("addFee")

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
    add_fee_json = json.dumps({"add_fee": get_addFee}) if get_addFee else None

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


#
#
#
# 通过UUID获取Cost表中的记录（给前端变配、注销用）
#
#
#
@app.route('/getCostByKey', methods=['GET'])
def get_cost_by_key():
    key = request.args.get('key')
    if key:
        cost = Cost.query.filter_by(uuid=key).first()
        if cost:
            # 根据 bill_subject 从 price 表中查询 project
            price = Price.query.filter_by(format=cost.bill_subject).first()
            resource_type = price.project if price else None

            result = {
                'key': cost.uuid,
                'resource_type': resource_type,
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
                'ssd': cost.ssd,
                'hdd': cost.hdd,
                'rds_storage': cost.rds_storage,
                'oss_storage': cost.oss_storage,
                'add_fee': cost.add_fee,
                'comment': cost.comment,
            }
            return jsonify(result)
        else:
            return jsonify({"error": "Cost not found."}), 404
    else:
        return jsonify({"error": "Key parameter is required."}), 400


#
#
#
# 从City表获取所有城市接口
#
#
#
@app.route('/DescribeCity', methods=['GET'])
def describe_city():
    result = []
    city_list = City.query.all()
    # result = [{'key': city.uuid, 'value': city.cities, 'label': city.cities} for city in city_list]
    for city in city_list:
        result.append(
            {
                'key': city.uuid,
                'city': city.cities,
                'with_elect': city.with_elect,
            }
        )

    return jsonify(result)


#
#
#
# City修改接口
#
#
#
@app.route('/UpdateCity/<uuid>', methods=['PUT'])
def update_city(uuid):
    data = request.get_json()

    # 查找要更新的记录
    city = City.query.filter_by(uuid=uuid).first()

    if not city:
        return jsonify({'message': 'City not found'}), 404

    # 更新字段
    if 'city' in data:
        city.cities = data['city']
    if 'with_elect' in data:
        city.with_elect = data['with_elect']

    try:
        db.session.commit()
        return jsonify({'message': 'City updated successfully'})
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'message': 'Failed to update city'}), 500


#
#
#
# City修改接口
#
#
#
@app.route('/AddCity', methods=['POST'])
def add_city():
    data = request.json
    city_name = data.get('city')
    with_elect = data.get('with_elect')

    # 检查是否已有相同的城市记录
    existing_city = City.query.filter_by(cities=city_name).first()
    if existing_city:
        return jsonify({'success': False, 'error': '城市已存在'}), 400

    # 创建新的 City 实例
    new_city = City(cities=city_name, with_elect=with_elect)

    try:
        db.session.add(new_city)
        db.session.commit()

        # 返回新生成的 UUID
        return jsonify({'success': True, 'uuid': new_city.uuid}), 201
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'success': False, 'error': str(e)}), 400


#
#
#
# City删除接口
#
#
#
@app.route('/DeleteCity/<string:key>', methods=['DELETE'])
def delete_city(key):
    city = City.query.filter_by(uuid=key).first()
    if city:
        try:
            db.session.delete(city)
            db.session.commit()
            return jsonify({'success': True}), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Cannot delete city due to foreign key constraints'}), 400
        except Exception as e:
            db.session.rollback()
            print(e)
            return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False, 'error': 'City not found'}), 404


#
#
#
# Price表获取接口
#
#
#
@app.route('/DescribePrice', methods=['GET'])
def describe_price():
    result = []
    price_list = Price.query.all()
    for price in price_list:
        result.append({
            'key': price.uuid,
            'project': price.project,
            'billing': price.billing,
            'format_name': price.format_name,
            'format': price.format,
            'price': price.price,
            'price_with_elect': price.price_with_elect,
            'version': price.version,
        })
    return jsonify(result)


#
#
#
# Price修改取接口
#
#
#
@app.route('/UpdatePrice/<string:key>', methods=['PUT'])
def update_price(key):
    data = request.json
    price_record = Price.query.filter_by(uuid=key).first()

    if price_record:
        try:
            price_record.project = data.get('project')
            price_record.billing = data.get('billing')
            price_record.format_name = data.get('format_name')
            price_record.format = data.get('format')
            price_record.price = data.get('price')
            price_record.price_with_elect = data.get('price_with_elect')
            price_record.version = data.get('version')

            db.session.commit()
            return jsonify({'success': True}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400

    return jsonify({'success': False, 'error': 'Price record not found'}), 404


#
#
#
# Price表添加接口
#
#
#
@app.route('/AddPrice', methods=['POST'])
def add_price():
    data = request.json
    project = data.get('project')
    billing = data.get('billing')
    format_name = data.get('format_name')
    Price_format = data.get('format')
    price = data.get('price')
    price_with_elect = data.get('price_with_elect')
    version = data.get('version')

    # Create a new Price instance without UUID
    new_price = Price(
        project=project,
        billing=billing,
        format_name=format_name,
        format=Price_format,
        price=price,
        price_with_elect=price_with_elect,
        version=version
    )

    try:
        db.session.add(new_price)
        db.session.commit()

        # Return the newly created record including UUID
        return jsonify({
            'success': True,
            'data': {
                'project': new_price.project,
                'billing': new_price.billing,
                'format_name': new_price.format_name,
                'format': new_price.format,
                'price': new_price.price,
                'price_with_elect': new_price.price_with_elect,
                'version': new_price.version,
                'uuid': new_price.uuid
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'success': False, 'error': str(e)}), 400


#
#
#
# Price表删除接口
#
#
#
@app.route('/DeletePrice/<string:key>', methods=['DELETE'])
def delete_price(key):
    price = Price.query.filter_by(uuid=key).first()
    if price:
        try:
            db.session.delete(price)
            db.session.commit()
            return jsonify({'success': True}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False, 'error': 'Price record not found'}), 404


#
#
#
# 返回addFee表
#
#
#
@app.route('/DescribeAddFee', methods=['GET'])
def describe_add_fee():
    try:
        fees = AddFee.query.all()
        result = [{'id': fee.id, 'product': fee.product, 'price': fee.price, 'version': fee.version}
                  for fee in fees]
        return jsonify(result), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Unable to fetch data'}), 500


#
#
#
# AddFee表添加接口
#
#
#
@app.route('/AddAddFee', methods=['POST'])
def add_fee():
    data = request.json
    product = data.get('product')
    price = data.get('price')
    version = data.get('version')

    new_fee = AddFee(
        product=product,
        price=price,
        version=version
    )

    try:
        db.session.add(new_fee)
        db.session.commit()

        # 返回新创建的记录，包括自动生成的 UUID
        return jsonify({
            'success': True,
            'data': {
                'id': new_fee.id,
                'product': new_fee.product,
                'price': new_fee.price,
                'version': new_fee.version,
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({'success': False, 'error': str(e)}), 400


#
#
#
# AddFee表修改接口
#
#
#
@app.route('/UpdateAddFee/<string:request_id>', methods=['PUT'])
def update_fee(request_id):
    data = request.json
    product = data.get('product')
    price = data.get('price')
    version = data.get('version')

    fee = AddFee.query.filter_by(id=request_id).first()
    if fee:
        try:
            fee.product = product
            fee.price = price
            fee.version = version

            db.session.commit()

            return jsonify({
                'success': True,
                'data': {
                    'id': fee.id,
                    'product': fee.product,
                    'price': fee.price,
                    'version': fee.version,
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            print(e)
            return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False, 'error': 'Fee not found'}), 404


#
#
#
# AddFee表删除接口
#
#
#
@app.route('/DeleteAddFee/<string:request_id>', methods=['DELETE'])
def delete_fee(request_id):
    fee = AddFee.query.filter_by(id=request_id).first()
    if fee:
        try:
            db.session.delete(fee)
            db.session.commit()
            return jsonify({'success': True}), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({'success': False, 'error': 'Cannot delete fee due to foreign key constraints'}), 400
        except Exception as e:
            db.session.rollback()
            print(e)
            return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify({'success': False, 'error': 'Fee not found'}), 404


#
#
#
# Service表添加接口
#
#
#
@app.route('/addService', methods=['POST'])
def add_service():
    data = request.json
    city = data.get('city')
    unit = data.get('unit')
    second_unit = data.get('second_unit')
    service = data.get('service')
    client = data.get('client')
    client_phone = data.get('client_phone')

    # 检查是否存在相同的 service
    existing_service = Service.query.filter_by(service=service).first()
    if existing_service:
        return jsonify({'success': False, 'error': 'Service already exists'}), 409

    new_service = Service(
        city=city,
        unit=unit,
        second_unit=second_unit,
        service=service,
        client=client,
        client_phone=client_phone
    )

    try:
        db.session.add(new_service)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': {
                'uuid': new_service.uuid,
                'city': new_service.city,
                'unit': new_service.unit,
                'second_unit': new_service.second_unit,
                'service': new_service.service,
                'client': new_service.client,
                'client_phone': new_service.client_phone
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400



#
#
#
# Service表查询接口
#
#
#
@app.route('/getService', methods=['GET'])
def get_services():
    services = Service.query.all()
    result = [{
        'uuid': service.uuid,
        'city': service.city,
        'unit': service.unit,
        'second_unit': service.second_unit,
        'service': service.service,
        'client': service.client,
        'client_phone': service.client_phone
    } for service in services]
    return jsonify(result)


#
#
#
# Service表更新接口
#
#
#
@app.route('/updateService/<string:uuid>', methods=['PUT'])
def update_service(uuid):
    data = request.json
    service = Service.query.filter_by(uuid=uuid).first()

    if not service:
        return jsonify({'success': False, 'error': 'Service not found'}), 404

    service.city = data.get('city', service.city)
    service.unit = data.get('unit', service.unit)
    service.second_unit = data.get('second_unit', service.second_unit)
    service.service = data.get('service', service.service)
    service.client = data.get('client', service.client)
    service.client_phone = data.get('client_phone', service.client_phone)

    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'data': {
                'uuid': service.uuid,
                'city': service.city,
                'unit': service.unit,
                'second_unit': service.second_unit,
                'service': service.service,
                'client': service.client,
                'client_phone': service.client_phone
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


#
#
#
# Service表删除接口
#
#
#
@app.route('/deleteService/<string:uuid>', methods=['DELETE'])
def delete_service(uuid):
    service = Service.query.filter_by(uuid=uuid).first()

    if not service:
        return jsonify({'success': False, 'error': 'Service not found'}), 404

    try:
        db.session.delete(service)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/stats/<field>', methods=['GET'])
def get_stats(field):
    # 确保字段是有效的
    if field not in ['city', 'payment', 'commit_id', 'unit', 'second_unit', 'service', 'usingfor', 'system', 'ip',
                     'eip', 'bill_subject']:
        return jsonify({'error': 'Invalid field'}), 400

    # 选择对应的表
    model = Service if field in ['city', 'unit', 'second_unit'] else Cost

    # 查询字段的统计信息，并限制返回10条记录
    result = db.session.query(getattr(model, field), db.func.count(getattr(model, field))) \
        .group_by(getattr(model, field)) \
        .order_by(db.func.count(getattr(model, field)).desc()) \
        .limit(10) \
        .all()

    # 格式化数据
    stats = [{'type': r[0], 'value': r[1]} for r in result]

    return jsonify(stats)


def build_SunTree(services, key_order, current_key=0):
    tree = {}

    for service in services:
        # 当前级别的键
        key = key_order[current_key]

        # 获取该级别的值
        value = getattr(service, key)

        # 如果该级别的值不在树中，添加它
        if value not in tree:
            tree[value] = {
                "label": value,
                "children": [],
                "uv": 0,
                "sum": 0,
                "count": 0
            }

        # 如果还有下一级，递归调用
        if current_key + 1 < len(key_order):
            child_tree = build_SunTree([service], key_order, current_key + 1)
            tree[value]["children"].extend(child_tree.values())

            # 递归结束后，累加子节点的 sum、uv 和 count
            for child in child_tree.values():
                tree[value]["sum"] += child["sum"]
                tree[value]["uv"] += child["uv"]
                tree[value]["count"] += child["count"]
        else:
            # 最后一级的叶节点
            tree[value]["children"] = None
            tree[value]["uv"] = 1  # 可以根据需求调整
            tree[value]["sum"] = 1  # 可以根据需求调整
            tree[value]["count"] = 0  # 可以根据需求调整

    return tree


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
