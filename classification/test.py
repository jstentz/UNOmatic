from picamera2 import Picamera2
# from gpiozero import LED, Button
import time
import serial
from forward import init_model, get_card
import cv2 as cv
import numpy as np

def cam_init(n, res):
    cam = Picamera2(n)
    config = cam.create_still_configuration({"size": res})
    cam.configure(config)
    cam.start(show_preview=False)
    return cam

def uart_init():
    ser = serial.Serial("/dev/ttyACM1", 9600, timeout=10)
    return ser

def get_line(ser):
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode("ascii").strip()
            return line
        time.sleep(0.1)

def main():
    cam_top = cam_init(1, (360, 360))
    # ser = uart_init()
    card_model = init_model('model_top_pretrain.pth', True)
    color_model = init_model('model_color_pretrain.pth', True)
    time.sleep(1)
    while True:
        cmd = input(">> ")
        if cmd == "q":
            break
        else:
            image = cam_top.capture_array().astype(np.float32) / 255
            cv.imshow("your mom", cv.cvtColor(image, cv.COLOR_RGB2BGR))
            cv.waitKey(0)
            cv.destroyAllWindows()
            # ser.write("d\n".encode("ascii"))

            color, card = get_card(card_model, color_model, True, image)
            print(color)
            print(card)
            # get_line(ser)

if __name__ == "__main__":
    main()
