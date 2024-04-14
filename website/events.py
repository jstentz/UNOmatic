from flask import request
from flask_socketio import emit

from .extensions import socketio

@socketio.on("connect")
def handle_connect(data):
    print("new connection")

@socketio.on("new_game")
def handle_new_game(num_players):
    print(f'message: {num_players}')
    emit("test", {"num_players" : num_players}, broadcast=True)
