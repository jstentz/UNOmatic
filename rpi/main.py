from smbus2.smbus2 import SMBus
import time

def main():
    addr = 0x8 
    bus = SMBus(1);
    cond = 1

    while cond == 1:
        buf = []
        data = input("enter command")
        bus.write_byte(addr, int(data))
        while bus.read_byte(addr, False) != 0x1:
            time.sleep(0.1)
        buf.append(bus.read_byte(addr, False))
        buf.append(bus.read_byte(addr, False))
        buf.append(bus.read_byte(addr, False))
        print(*buf)

    bus.close()
    


if __name__ == "__main__":
    main()
