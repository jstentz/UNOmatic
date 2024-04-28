from flask import request
from flask_socketio import emit
import os
import base64

from .extensions import socketio

most_recent_state = None

@socketio.on("connect")
def handle_connect(data):
    print("new connection")

    # send off all the images to the website
    images_path = os.path.join(os.path.dirname(__file__), '../uno/images')
    image_names = os.listdir(images_path)
    
    images = []

    for image_name in image_names:
      image_path = os.path.join(images_path, image_name)

      # load image
      with open(image_path, 'rb') as f:
        image_data = f.read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')

      images.append({'image_name': image_name, 'img': encoded_image})
    
    sid = request.sid
    emit('get_images', images, room=sid)

    if most_recent_state is not None:
        print('sending state!')
        emit('new_state', most_recent_state)

@socketio.on("website_reset")
def handle_reset(data):
    print('got website reset')
    emit("reset", data, broadcast=True)

@socketio.on("website_round_reset")
def handle_reset(data):
    emit("round_reset", broadcast=True)

@socketio.on("pi_state")
def handle_pi_state(data):
    # receive the state (or something else, like game over)
    global most_recent_state
    most_recent_state = data
       
    emit("new_state", data, broadcast=True)

@socketio.on("pi_game_over")
def handle_pi_game_over(data):
    emit("game_over", data, broadcast=True)

@socketio.on("pi_round_over")
def handle_pi_round_over(data):
    emit("round_over", data, broadcast=True)
