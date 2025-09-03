from flask import request, jsonify, make_response
from functools import wraps
from sqlalchemy import text
from .models import MockRoute, db
from .config import Config
import time
import json

# 导入工具函数
from .utils import process_dynamic_response
# generate_payment_response)


def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != Config.API_KEY:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)

    return decorated_function


def setup_routes(app):
    # 统一的Mock路由处理函数
    def handle_mock_request(path):
        # 查询数据库中的路由配置
        route = MockRoute.query.filter_by(path=path, is_active=True).first()

        if not route:
            return jsonify({'error': '未查询到路由'}), 404

        # 检查请求方法是否允许
        allowed_methods = route.methods.split(',')
        if request.method not in allowed_methods:
            return jsonify({'error': 'Method not allowed'}), 405

        # 记录请求信息
        request_data = {
            'method': request.method,
            'headers': dict(request.headers),
            'args': request.args.to_dict(),
            'form': request.form.to_dict(),
            'json': request.get_json(silent=True) or {},
            'path': path
        }

        app.logger.info(f"Mock request received: {request.method} {path}")

        # 添加延迟
        if route.delay > 0:
            time.sleep(route.delay)

        # 处理动态响应
        # if isinstance(route.response, dict) and route.response.get('__handler') == 'payment_handler':
        #     response_data, status_code = generate_payment_response(request)
        # else:
        response_data = process_dynamic_response(route.response, request)
        status_code = route.status_code

        # 创建响应
        response = make_response(jsonify(response_data), status_code)

        # 处理动态headers
        headers = process_dynamic_response(route.headers, request)
        for key, value in headers.items():
            response.headers[key] = value

        return response

    # 注册通配路由 - 处理所有非管理API的请求
    @app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
    @app.route('/<path:path>', methods=['GET', 'POST'])
    def catch_all_handler(path):
        # 排除管理API
        if path.startswith('_manage'):
            return jsonify({'error': 'Not found'}), 404

        full_path = f'/{path}' if path else '/'
        return handle_mock_request(full_path)

    # 管理API - 获取所有路由
    @app.route('/_manage/routes', methods=['GET'])
    @require_api_key
    def get_routes():
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        query = MockRoute.query

        # 搜索过滤
        search = request.args.get('search', '')
        if search:
            query = query.filter(
                (MockRoute.path.ilike(f'%{search}%')) |
                (MockRoute.description.ilike(f'%{search}%'))
            )

        # 过滤条件
        if request.args.get('active_only'):
            query = query.filter_by(is_active=True)

        routes = query.order_by(MockRoute.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'routes': [route.to_dict() for route in routes.items],
            'total': routes.total,
            'pages': routes.pages,
            'current_page': page
        })

    # 管理API - 获取特定路由
    @app.route('/_manage/routes/<int:route_id>', methods=['GET'])
    @require_api_key
    def get_route(route_id):
        route = MockRoute.query.get_or_404(route_id)
        return jsonify(route.to_dict())

    # 管理API - 创建新路由
    @app.route('/_manage/routes', methods=['POST'])
    @require_api_key
    def create_route():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': '参数不能为空'}), 400

            # 验证必要字段
            if 'path' not in data or 'response' not in data:
                return jsonify({'error': ' Path和response不能为空'}), 400

            # 检查路径是否已存在
            if MockRoute.query.filter_by(path=data['path']).first():
                return jsonify({'error': 'Route 已存在'}), 409

            # 创建新路由
            methods = data.get('methods', ['GET'])
            if isinstance(methods, list):
                methods = ','.join(methods)

            route = MockRoute(
                path=data['path'],
                methods=methods,
                response=data['response'],
                status_code=data.get('status_code', 200),
                headers=data.get('headers', {}),
                delay=data.get('delay', 0),
                description=data.get('description'),
                is_active=data.get('is_active', True)
            )

            db.session.add(route)
            db.session.commit()

            app.logger.info(f"Created new route: {methods} {route.path}")
            return jsonify({'message': '创建成功', 'route': route.to_dict()}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'创建失败: {str(e)}'}), 500

    # 管理API - 更新路由
    @app.route('/_manage/routes/<int:route_id>', methods=['POST'])
    @require_api_key
    def update_route(route_id):
        try:
            route = MockRoute.query.get_or_404(route_id)
            data = request.get_json()

            if 'methods' in data:
                methods = data['methods']
                if isinstance(methods, list):
                    methods = ','.join(methods)
                route.methods = methods

            if 'response' in data:
                route.response = data['response']

            if 'status_code' in data:
                route.status_code = data['status_code']

            if 'headers' in data:
                route.headers = data['headers']

            if 'delay' in data:
                route.delay = data['delay']

            if 'description' in data:
                route.description = data['description']

            if 'is_active' in data:
                route.is_active = data['is_active']

            db.session.commit()

            app.logger.info(f"Updated route: {route.methods} {route.path}")
            return jsonify({'message': '更新成功', 'route': route.to_dict()})

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'更新失败: {str(e)}'}), 500

    # 管理API - 删除路由--软删除
    @app.route('/_manage/routes/delete1/<int:route_id>', methods=['POST'])
    @require_api_key
    def delete_route(route_id):
        try:
            route = MockRoute.query.get_or_404(route_id)
            route.is_active = False
            # db.session.delete(route)
            db.session.commit()

            app.logger.info(f"Deleted route: {route.path}")
            return jsonify({'message': '删除成功'})

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'删除失败: {str(e)}'}), 500

    # 批量操作
    @app.route('/_manage/routes/batch', methods=['POST'])
    @require_api_key
    def batch_operations():
        try:
            data = request.get_json()
            operation = data.get('operation')
            route_ids = data.get('route_ids', [])

            if operation == 'activate':
                MockRoute.query.filter(MockRoute.id.in_(route_ids)).update(
                    {'is_active': True}, synchronize_session=False
                )
                message = 'Routes activated successfully'
            elif operation == 'deactivate':
                MockRoute.query.filter(MockRoute.id.in_(route_ids)).update(
                    {'is_active': False}, synchronize_session=False
                )
                message = 'Routes deactivated successfully'
            elif operation == 'delete':
                MockRoute.query.filter(MockRoute.id.in_(route_ids)).delete(
                    synchronize_session=False
                )
                message = 'Routes deleted successfully'
            else:
                return jsonify({'error': 'Invalid operation'}), 400

            db.session.commit()
            return jsonify({'message': message})

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to perform batch operation: {str(e)}'}), 500

    # 健康检查端点
    @app.route('/_manage/health', methods=['GET'])
    def health_check():
        try:
            # 检查数据库连接
            db.session.execute(text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'

        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'timestamp': time.time(),
            'total_routes': MockRoute.query.count(),
            'active_routes': MockRoute.query.filter_by(is_active=True).count()
        })