from picamera2 import Picamera2
from gpiozero import LED, Button
import serial
import time
import numpy as np

def uart_init():
    ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
    return ser

def cam_init(n, res):
    cam = Picamera2(n)
    config = cam.create_still_configuration({"size": res})
    cam.configure(config)
    cam.start(show_preview=True)
    return cam


def get_line(ser):
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode("ascii").strip()
            return line
        time.sleep(0.1)

def model_init():
    pass

def classify(model, image):
    pass

def play_one_turn(card):
    pass

def add_card(card):
    pass

def rotate(ser, angle):
    steps = 200*angle//360
    ser.write(f'r{steps}')
    get_line(ser)

def deal(ser, cam, num_deal):
    images = []
    for _ in range(num_deal):
        images.append(cam.capture_array())
        ser.write(f'd')
        get_line(ser)
    return images
            
def event_loop():
    ser = uart_init()
    cam_top = cam_init(0, (540, 360))
    cam_bottom= cam_init(0, (540, 360))
    cam_top.start(show_preview=True)
    cam_bottom.start(show_preview=True)
    model = model_init()
    button_new_move = Button(2)
    while True:
        button_new_move.wait_for_press()
        out_top = cam_top.capture_array()
        card = classify(model, out_top)
        num_deal = play_one_turn(card)
        # need to do a bunch of control flow
        rotate(ser, 90)
        images = deal(ser, cam_bottom, num_deal)
        for image in images:
            card = classify(model, image)
            add_card(card)

def main():
    ser = uart_init()
    cam = cam_init(0, (540, 360))
    while True:
        cmd = input(">> ")
        if cmd == "q":
            break
        cam.capture_file("image.jpg")
        data = cmd + "\n"
        data = data.encode("ascii")
        ser.write(data)
        line = get_line(ser)
        print(line)

if __name__ == "__main__":
    main()
