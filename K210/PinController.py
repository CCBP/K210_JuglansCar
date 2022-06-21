from Maix import GPIO

class PinController:

    def __init__(self):
        # LED
        self.__led_g = GPIO(GPIO.GPIO0, GPIO.OUT)
        self.__led_g.value(1)
        self.__led_r = GPIO(GPIO.GPIO1, GPIO.OUT)
        self.__led_r.value(1)
        self.__led_b = GPIO(GPIO.GPIO2, GPIO.OUT)
        self.__led_b.value(1)
        # control parameters
        self.record = False
        self.auto_drive = False
    
    def get_record(self):
        return self.record
    
    def get_auto_drive(self):
        return self.auto_drive

    def led_r(self, value = None):
        if (value is None): # reverse
            self.__led_r.value(not self.__led_r.value())
        else:               # set
            self.__led_r.value(value)

    def led_g(self, value = None):
        if (value is None): # reverse
            self.__led_g.value(not self.__led_g.value())
        else:               # set
            self.__led_g.value(value)

    def led_b(self, value = None):
        if (value is None): # reverse
            self.__led_b.value(not self.__led_b.value())
        else:               # set
            self.__led_b.value(value)