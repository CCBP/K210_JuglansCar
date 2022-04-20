from Maix import GPIO
import time

class Pin:

    def __init__(self, controller):
        self.controller = controller
        # LED
        self.__led_g = GPIO(GPIO.GPIO0, GPIO.OUT)
        self.__led_g.value(1)
        self.__led_r = GPIO(GPIO.GPIO1, GPIO.OUT)
        self.__led_r.value(1)
        self.__led_b = GPIO(GPIO.GPIO2, GPIO.OUT)
        self.__led_b.value(1)
        # receive the web client connection status come from ESP32
        self.esp32 = GPIO(GPIO.GPIOHS0, GPIO.IN)
        # keyboard interrupt
        self.k2 = GPIO(GPIO.GPIOHS2, GPIO.IN, GPIO.PULL_UP)
        self.k2.irq(self.k2_callback, GPIO.IRQ_FALLING)
        self.k3 = GPIO(GPIO.GPIOHS3, GPIO.IN, GPIO.PULL_UP)
        self.k3.irq(self.k3_callback, GPIO.IRQ_FALLING)
        self.k4 = GPIO(GPIO.GPIOHS4, GPIO.IN, GPIO.PULL_UP)
        self.k4.irq(self.k4_callback, GPIO.IRQ_FALLING)
        self.k5 = GPIO(GPIO.GPIOHS5, GPIO.IN, GPIO.PULL_UP)
        self.k5.irq(self.k5_callback, GPIO.IRQ_FALLING)
        # control parameters
        self.record = False
        self.auto_drive = False
    
    def get_esp32_state(self):
        return self.esp32.value()
    
    def get_record(self):
        return self.record
    
    def get_auto_drive(self):
        return self.auto_drive

    def k2_callback(self, pin = None, data = None):
        '''
        Controls whether driving data is recorded
        '''
        if (pin is None):       # called by the receiver
            self.record = data
            self.__led_g.value(not self.record)
            print("[I] K2 is called, record state:", self.record)
        else:                   # called by key interrupt
            time.sleep_ms(50)   # debounce
            if (not pin.value()):
                self.record = not self.record
                self.__led_g.value(not self.record)
                print("[I] K2 is pressed, record state:", self.record)

    def k3_callback(self, pin = None, data = None):
        print(type(pin))
        '''
        Control vehicle driving modes
        '''
        if (pin is None):       # called by the receiver
            if (data == "local" or data == "local_angle"):
                self.auto_drive = True
            # receiver can only turn on the auto_drive
            # else:               # "user" mode
            #     self.auto_drive = False
            self.__led_b.value(not self.auto_drive)
            print("[I] K3 is called, auto drive state: [%s]%s"
                    % (data, self.auto_drive))
        else:                   # called by key interrupt
            time.sleep_ms(50)   # debounce
            if (not pin.value()):
                self.controller.servo(0)
                self.controller.motor(0)
                self.auto_drive = not self.auto_drive
                self.__led_b.value(not self.auto_drive)
                print("[I] K3 is pressed, auto drive state:", self.auto_drive)

    def k4_callback(self, pin, data = None):
        '''
        Nothing
        '''
        time.sleep_ms(10)   # debounce
        if (not pin.value()):
            print("[I] K4 is pressed, with data:", data)

    def k5_callback(self, pin, data = None):
        '''
        Nothing
        '''
        time.sleep_ms(10)   # debounce
        if (not pin.value()):
            print("[I] K5 is pressed, with data:", data)

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