'''
flask --app run run --host=0.0.0.0
'''

from website import create_app, socketio

# TODO: this does nothing if you run the above command lmao
if __name__ == "main":
    app = create_app()
    socketio.run(app)
