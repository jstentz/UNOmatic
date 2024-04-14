from website import create_app, socketio

if __name__ == "main":
    app = create_app()
    socketio.run(app)
