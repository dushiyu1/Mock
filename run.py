from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("MySQL Mock Server")
    print("=" * 60)
    print("Management API:")
    print("  GET     /_manage/routes - 展示所有可用路由")
    print("  GET     /_manage/routes/<id> - 获取路由详情")
    print("  POST    /_manage/routes - 创建新路由")
    print("  POST     /_manage/routes/<id> - 更新路由")
    print("  POST  /_manage/routes/delete1/<int:route_id> - 删除路由")
    print("  POST    /_manage/routes/batch - 批量管理")
    print("  GET     /_manage/health - 健康检查")
    print("\n 管理路由时，请添加请求头 'X-API-Key: mock-server-admin'")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)