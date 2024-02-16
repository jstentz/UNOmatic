from picamera2 import Picamera2
import serial
import time

def uart_init():
    ser = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
    return ser

def cam_init():
    picam2 = Picamera2()
    config = picam2.create_still_configuration({"size": (1280, 720)})
    picam2.start(show_preview=True)
    return picam2, config

def get_line():
    while True:
        line = serial.readline().decode('utf-8').strip()
        if line != "":
            return line


def main():
    # ser = uart_init()
    picam2, config = cam_init()
    while True:
        cmd = input(">> ")
        if cmd == "q":
            break
        picam2.switch_mode_and_capture_file(config, "image.jpg")
        # ser.write(b'hello')
        # line = get_line():
        # print(line)
            
        


    


if __name__ == "__main__":
    main()
