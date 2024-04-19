from flask import request
from flask_socketio import emit, send

from .extensions import socketio

@socketio.on("connect")
def handle_connect(data):
    print("new connection")

@socketio.on("new_game")
def handle_new_game(num_players):
    print(f'message: {num_players}')
    emit("test", {"num_players" : num_players}, broadcast=True)

@socketio.on("from_pi")
def handle_from_pi(data):
    print(f'got {data} from pi')
    send('Success!')
    