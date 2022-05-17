import ujson, time
from machine import I2C

class Receiver:

    def __init__(self, drive_controller, pin_controller, scl = 7, sda = 10, addr = 0x24):
        self.i2c = i2c = I2C(
            I2C.I2C1, 
            mode=I2C.MODE_SLAVE, 
            scl = scl, 
            sda = sda, 
            addr = addr, 
            addr_size = 7, 
            on_receive = self.__receive_callback, 
            on_transmit = self.__transmit_callback, 
            on_event = self.__event_callback
        )
        self.unlock = True
        self.controller = drive_controller
        self.pin = pin_controller
        self.record_callback = pin_controller.k2_callback
        self.auto_drive_callback = pin_controller.k3_callback
        self.angle = 0
        self.throttle = 0
        self.drive_mode = "user"
        self.recording = False

    def __receive_callback(self, data):
        if (self.unlock):                       # receive enable
            if (isinstance(self.msg, str)):     # try to prevent __iadd__ error
                self.msg += chr(data)

    def __transmit_callback(self):
        pass

    def __event_callback(self, event):
        if (event == I2C.I2C_EV_START):
            if (self.unlock is None):   # wait for next message
                self.unlock = True
            if (self.unlock):
                self.msg = ""
        elif (event == I2C.I2C_EV_RESTART):
            if (self.unlock is None):   # wait for next message
                self.unlock = True
            if (self.unlock):
                self.msg = ""
        elif  (event == I2C.I2C_EV_STOP):
            if (self.unlock):
                # print("[D] I2C received:", self.msg)
                if (self.msg == ""):        # query information from ESP32, ignore
                    print("[I] ESP32 connected")
                    return
                try:                        # JSON 解析
                    drive = ujson.loads(self.msg)
                    if ("angle" in drive):
                        self.angle = drive["angle"]
                    if ("throttle" in drive):
                        self.throttle = drive["throttle"]
                    if ("drive_mode" in drive):
                        self.drive_mode = drive["drive_mode"]
                    if ("recording" in drive):
                        self.recording = drive["recording"]
                except BaseException as err:
                    print("[E] receiver has %s %s\n[E] recevied massage: [%d]%s"
                            % (type(err), err, len(self.msg), self.msg))
                    self.controller.servo(0)
                    self.controller.motor(0)
                    return

                print("[W] Angle: % .4f\tThrottle: % .4f\tDrive Mode: %s\tRecording: %s"
                        % (self.angle, self.throttle, self.drive_mode, self.recording))
                # Pause the direct update "record" status and wait for the webpage 
                # update to release the binding between the handle and the record.
                #self.record_callback(data = self.recording)
                if ((self.pin.get_auto_drive() and self.drive_mode == "user")
                    or (not self.pin.get_auto_drive() and self.drive_mode != "user")):
                    self.auto_drive_callback(data = self.drive_mode)    # update the drive mode
                if (self.pin.get_auto_drive()):     # auto angle
                    self.controller.motor(self.throttle)
                else:                               # user control
                    self.controller.servo(self.angle)
                    self.controller.motor(self.throttle)
        else:
            self.msg = ""
            print("[E] I2C event error:", event)

    def receive_lock(self, lock):
        if (lock):
            self.unlock = False         # I2C receive disable
        else:
            self.unlock = None          # wait for next message
    
    def get_angle(self):
        return self.angle

    def get_throttle(self):
        return self.throttle

    def get_drive_mode(self):
        return self.drive_mode

    def get_recording(self):
        return self.recording