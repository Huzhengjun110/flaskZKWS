from app import create_app
application = create_app()

if __name__ == '__main__':
    # import uvicorns
    # from asgiref.wsgi import WsgiToAsgi
    # asgi_app = WsgiToAsgi(app)
    # uvicorn.run(asgi_app, host="0.0.0.0", port=8065)
    application.run(host="0.0.0.0", port=8065, debug=True)
