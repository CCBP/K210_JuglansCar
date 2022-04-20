import pca9685

class Actuator:

    # STEERING FOR PWM_STEERING_THROTTLE (and deprecated I2C_SERVO)
    STEERING_CHANNEL = 1            # (deprecated) channel on the 9685 pwm board 0-15
    STEERING_LEFT_PWM = 450         # pwm value for full left steering
    STEERING_RIGHT_PWM = 250        # pwm value for full right steering

    # THROTTLE FOR PWM_STEERING_THROTTLE (and deprecated I2C_SERVO)
    THROTTLE_CHANNEL = 0            # (deprecated) channel on the 9685 pwm board 0-15
    THROTTLE_FORWARD_PWM = 400      # pwm value for max forward throttle
    THROTTLE_STOPPED_PWM = 370      # pwm value for no movement
    THROTTLE_REVERSE_PWM = 320      # pwm value for max reverse throttle

    def __init__(self, i2c, addr = 0x40, freq = 60):
        self.pca = pca9685.PCA9685(i2c, addr)
        self.pca.freq(freq)
        self.angle = 0
        self.throttle = 0
        self.servo(0)
        self.motor(0)

    def map_range(self, x, X_min, X_max, Y_min, Y_max):
        '''
        Linear mapping between two ranges of values
        '''
        X_range = X_max - X_min
        Y_range = Y_max - Y_min
        XY_ratio = X_range/Y_range

        y = ((x-X_min) / XY_ratio + Y_min) // 1

        return int(y)

    def servo(self, angle = None):
        if (angle is None):
            return self.angle
        if (angle < -1 or angle > 1):
            print("Servo angle must be in range -1 to 1")
        else:
            self.angle = angle
            angle_pulse = self.map_range(angle, -1, 1,
                                        self.STEERING_LEFT_PWM,
                                        self.STEERING_RIGHT_PWM)
            self.pca.duty(self.STEERING_CHANNEL, angle_pulse)

    def motor(self, speed = None):
        if (speed is None):
            return self.speed
        if (speed < -1 or speed > 1):
            print("Motor speed must be in range -1 to 1")
        else:
            self.speed = speed
            # The forward and reverse pulse length of the throttle
            # is not asymmetrical relative to the stop pulse length.
            # Therefore, the pulse lengths are mapped separately 
            # in the positive and negative intervals.
            if (speed >= 0):
                speed_pulse = self.map_range(speed, 0, 1,
                                            self.THROTTLE_STOPPED_PWM,
                                            self.THROTTLE_FORWARD_PWM)
                self.pca.duty(self.THROTTLE_CHANNEL, speed_pulse)
            elif (speed < 0):
                speed_pulse = self.map_range(speed, -1, 0,
                                            self.THROTTLE_REVERSE_PWM,
                                            self.THROTTLE_STOPPED_PWM)
                self.pca.duty(self.THROTTLE_CHANNEL, speed_pulse)

    def release(self):
        self.pca.duty(self.STEERING_CHANNEL, 0)
        self.pca.duty(self.THROTTLE_CHANNEL, 0)
