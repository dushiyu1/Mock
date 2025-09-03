import os
import sys
import time
import logging
from sqlalchemy import text

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    # 设置环境变量，避免加载路由
    os.environ['SKIP_ROUTES'] = 'true'

    from app import create_app, db
    from app.models import MockRoute

    app = create_app()

    max_retries = 10
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            with app.app_context():
                logger.info(f"Attempt {attempt + 1}/{max_retries}: 数据库连接中......")

                # 测试数据库连接
                db.session.execute(text('SELECT 1'))
                logger.info("数据库连接成功")

                # 创建所有表
                db.create_all()
                logger.info("表格创建成功")

                # 添加示例数据（可选）
                if not MockRoute.query.first():
                    sample_routes = [
                        MockRoute(
                            path='/api/health',
                            methods='GET',
                            response={'status': 'healthy', 'service': 'mock-server'},
                            status_code=200,
                            description='健康检查接口'
                        ),
                        MockRoute(
                            path='/api/payment',
                            methods='POST',
                            response={
                                'code': 200,
                                'message': '支付成功',
                                'data': {
                                    'order_no': 'ORDER_123456',
                                    'status': 'SUCCESS',
                                    'amount': 100.0
                                }
                            },
                            status_code=200,
                            description='支付接口Mock'
                        )
                    ]

                    for route in sample_routes:
                        db.session.add(route)

                    db.session.commit()
                    logger.info("示例添加成功")

                logger.info("数据库初始化完成")
                return True

        except Exception as e:
            logger.error(f"Database initialization attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Exiting.")
                return False


if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)