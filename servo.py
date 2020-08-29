import machine, math

class Servo:
    """
    A simple class for controlling hobby servos. Modeled after the ESP8266 Arduino Servo Driver
    """
    def __init__(self, pin, freq=50, min_us=24, max_us=115, max_ang=180):
        self.min_us = min_us
        self.max_us = max_us
        self.freq = freq
        self.pin = machine.Pin(pin)
        self.max_ang = max_ang
        self.pwm = None
        self._attached = False
        
    def attach(self, pin=self.pin, freq=self.freq):
        self.pwm = machine.PWM(pin, freq=freq, duty=0)
        self._attached = True
        
    def detach(self):
        self.pwm.deinit()
        self._attached = False

    def attached(self):
        return(self._attached)
      
    def write_us(self, us):
        """Set the signal to be ``us`` microseconds long. Zero disables it."""
        if us == 0:
            self.pwm.duty(0)
            return
        us = min(self.max_us, max(self.min_us, us))
        duty = us * 1024 * self.freq // 1000000
        self.pwm.duty(duty)

    def write(self, degrees):
        """Move to the specified angle in ``degrees``."""
        degrees = degrees % 360
        total_range = self.max_us - self.min_us
        us = self.min_us + total_range * degrees // self.max_ang
        self.write_us(us)
        
    def __deinit__(self):
        self.pwm.deinit()
