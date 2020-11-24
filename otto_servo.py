#-- A simple class for controlling hobby servos. Modeled after the ESP8266 Arduino Servo Driver
#-- OttDIY Python Project, 2020

import machine

try:
    from esp32 import Servo as espServo
    useServo = True
except ImportError:
    """This version of esp32 doesn't support Servo, use PWM instead"""
    useServo = False

class Servo:
    def __init__(self, freq = 50, min_us = 1000, max_us = 2000, max_ang = 180):
        global useServo
        self.min_us = min_us
        self.max_us = max_us
        self.freq = freq
        self.max_ang = max_ang
        self.pin = None
        if useServo:
            self.servo = None
        else:
            self.pwm = None
        self._attached = False

    def attach(self, pin):
        global useServo
        self.pin = machine.Pin(pin)
        if useServo:
            self.servo = espServo(self.pin)
        else:
            self.pwm = machine.PWM(self.pin, freq = self.freq)
        self._attached = True

    def detach(self):
        global useServo
        if useServo:
            self.servo.deinit()
        else:
            self.pwm.deinit()
        self._attached = False

    def attached(self):
        return(self._attached)

    def write_us(self, us):
        """Set the signal to be ``us`` microseconds long. Zero disables it."""
        global useServo
        if useServo:
            self.servo.duty(us)
        else:
            """PWM uses duty as a value from 0-1024"""
            duty = int(us / (1000000 / self.freq / 1024))
            self.pwm.duty(duty)

    def write(self, degrees):
        """Move to the specified angle in ``degrees``."""
        degrees = degrees % 360
        if degrees < 0:
            degrees += 360
        if degrees > 180:
            degrees = 180
        total_range = self.max_us - self.min_us
        us = self.min_us + total_range * degrees // self.max_ang
        self.write_us(us)

    def __deinit__(self):
        global useServo
        if useServo:
            self.servo.deinit()
        else:
            self.pwm.deinit()
