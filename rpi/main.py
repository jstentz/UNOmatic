from picamera2 import Picamera2
import gpiod
import serial
import time

def uart_init():
    ser = serial.Serial("/dev/ttyACM0", 9600, timeout=10)
    return ser

def cam_init(n, res):
    cam = Picamera2(n)
    config = cam.create_still_configuration({"size": res})
    cam.configure(config)
    cam.start(show_preview=False)
    return cam


def get_line(ser):
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode("ascii").strip()
            return line
        time.sleep(0.1)

def model_init():
    model = ConvNetwork()

def classify(model, image):
    pass

def play_one_turn(card):
    pass

def add_card(card):
    pass

def rotate(ser, angle):
    steps = 200*angle//360
    ser.write(f'r{steps}\n'.encode("ascii"))
    get_line(ser)

def deal(ser, cam, num_deal):
    images = []
    for _ in range(num_deal):
        images.append(cam.capture_array())
        ser.write("d\n".encode("ascii"))
        get_line(ser)
    return images

def keypad_read(col_lines, row_lines):
    names = [["1","4","7","*"], ["2","5","8","0"], ["3","6","9","#"]]
    for (i, col) in enumerate(col_lines):
        col.set_value(1)
        for (j, row) in enumerate(row_lines):
            if row.get_value() == 1:
                col.set_value(0)
                return names[i][j]
        col.set_value(0)
    return ""
        

def read():
    pass
def main():
    row_pins = [
    ("r1", 6),
    ("r2", 21),
    ("r3", 20),
    ("r4", 19)]
    col_pins = [
    ("c1", 13),
    ("c2", 5),
    ("c3", 26)]
    # ser = uart_init()
    # time.sleep(1)
    # cam_top = cam_init(1, (360, 360))
    # cam_bot = cam_init(0, (360, 360))
    # cnt = 141
    chip = gpiod.Chip('gpiochip4')
    row_lines = []
    for (consumer, pin) in row_pins:
        row_lines.append(chip.get_line(pin))
        row_lines[-1].request(consumer = consumer, type=gpiod.LINE_REQ_DIR_IN, flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_DOWN)
    col_lines = []
    for (consumer, pin) in col_pins:
        col_lines.append(chip.get_line(pin))
        col_lines[-1].request(consumer = consumer, type=gpiod.LINE_REQ_DIR_OUT)
        col_lines[-1].set_value(0)
    while True:
        cmd = input(">> ")
        if cmd == "q":
            break
        else:
            print(keypad_read(col_lines, row_lines))

if __name__ == "__main__":
    main()
