# import requests

# url = 'http://127.0.0.1:5000/from_pi'

# response = requests.post(url)
# print(f'got response: {response.content.decode("ascii")}')

import socketio
import json
import time

sio = socketio.Client()
sio.connect('http://localhost:5000')

sio.emit('from_pi', 'hello')


@sio.on('test')
def response(data):
  print(f'client got {data}')

sio.wait()


# sio.disconnect()
