from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("MySQL Mock Server")
    print("=" * 60)
    print("Management API:")
    print("  GET     /_manage/routes - List all routes")
    print("  GET     /_manage/routes/<id> - Get a specific route")
    print("  POST    /_manage/routes - Create a new route")
    print("  PUT     /_manage/routes/<id> - Update a route")
    print("  DELETE  /_manage/routes/<id> - Delete a route")
    print("  POST    /_manage/routes/batch - Batch operations")
    print("  GET     /_manage/health - Health check")
    print("\nUse header 'X-API-Key: mock-server-admin' for management API")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)