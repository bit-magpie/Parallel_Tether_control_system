import serial

class Reel:
    def __init__(self, serial_port) -> None:
        self.serial = serial.Serial(timeout=3)
        self.serial.port = serial_port
        self.serial.baudrate = 115200
        self.reel_id = 0
        self.last_value = 0
    
    def getReelId(self):
        self.serial.open()
        self.serial.write("rlid".encode("utf-8"))
        value = self.serial.readline()
        if len(value) > 0:
            self.reel_id = int(value)
        else:
            self.reel_id = -1
        self.serial.close()
        print(self.reel_id)

    def setValue(self, value):
        print(self.serial.port)
        print(value)
        self.serial.open()
        self.serial.write(str(value).encode("utf-8"))
        self.last_value = value
        self.serial.close()

    def testReel(self):
        self.serial.open()
        self.serial.write(str(50).encode("utf-8"))
        time.sleep(1)
        self.serial.write(str(-50).encode("utf-8"))
        self.serial.close()
