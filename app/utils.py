import random
import time
from datetime import datetime
import json
import re


def process_dynamic_response(response_template, request):
    """处理动态响应模板"""
    if isinstance(response_template, str):
        # 简单的模板替换
        result = response_template

        # 替换请求参数
        if request.json:
            for key, value in request.json.items():
                placeholder = f'{{{{request.json.{key}}}}}'
                if placeholder in result:
                    result = result.replace(placeholder, str(value))

        # 替换内置函数
        result = result.replace('{{random_int(100000,999999)}}', str(random.randint(100000, 999999)))
        result = result.replace('{{now()}}', datetime.now().isoformat())
        result = result.replace('{{timestamp}}', str(time.time()))

        # 处理随机选择
        choice_match = re.search(r'{{random_choice\(\[(.*?)\]\)}}', result)
        if choice_match:
            choices = [choice.strip().strip('"\'') for choice in choice_match.group(1).split(',')]
            result = result.replace(choice_match.group(0), random.choice(choices))

        try:
            return json.loads(result)
        except:
            return result

    elif isinstance(response_template, dict):
        # 递归处理字典
        result = {}
        for key, value in response_template.items():
            result[key] = process_dynamic_response(value, request)
        return result

    elif isinstance(response_template, list):
        # 递归处理列表
        return [process_dynamic_response(item, request) for item in response_template]

    return response_template


def generate_payment_response(request):
    """生成支付响应"""
    # 获取请求参数
    data = request.get_json() or {}
    payment_id = data.get('id')
    merchant_id = data.get('merchant_id')
    order_no = data.get('order_no')
    amount = data.get('amount')

    # 验证必要参数
    if not all([payment_id, merchant_id, order_no, amount]):
        return {
            "code": 400,
            "message": "缺少必要参数",
            "data": None
        }, 400

    # 模拟支付状态（80%成功，20%失败）
    is_success = random.random() > 0.2

    if is_success:
        response_data = {
            "code": 200,
            "message": "支付成功",
            "data": {
                "id": payment_id,
                "merchant_id": merchant_id,
                "order_no": order_no,
                "amount": amount,
                "pay_status": "SUCCESS",
                "transaction_id": f"TRX{random.randint(10000000, 99999999)}",
                "pay_time": datetime.now().isoformat(),
                "settlement_time": datetime.now().isoformat()
            }
        }
    else:
        response_data = {
            "code": 500,
            "message": "支付失败",
            "data": {
                "id": payment_id,
                "merchant_id": merchant_id,
                "order_no": order_no,
                "amount": amount,
                "pay_status": "FAILED",
                "error_code": "BALANCE_INSUFFICIENT",
                "error_message": "余额不足"
            }
        }

    return response_data, 200


def random_choice(choices):
    """随机选择"""
    if isinstance(choices, str):
        choices = choices.strip('[]').split(',')
        choices = [choice.strip().strip('"\'') for choice in choices]
    return random.choice(choices)