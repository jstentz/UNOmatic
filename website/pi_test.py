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
