# this is the code for reading the battery

from machine import Pin, ADC

MAX_VOLTAGE = 7.6
BAT_MAX = 4.8
BAT_MIN = 3.25


class BatReader9:
    def __init__(self, pin = 34):
        self.batPin = ADC(Pin(pin))
        self.batPin.atten(ADC.ATTN_11DB)
        self.batPin.width(ADC.WIDTH_12BIT)

    def readBatVoltage(self):
        try:
            volt = round(self.batPin.raw_to_voltage(self.batPin.read()) * 2 / 1000.0, 2)
        except AttributeError:
            volt = round(self.batPin.read() * MAX_VOLTAGE / 4096.0, 2)
        if volt < BAT_MIN:
            volt = BAT_MIN
        elif volt > BAT_MAX:
            volt = BAT_MAX

        return volt

    def readBatPercent(self):
        percent = round((self.readBatVoltage() - BAT_MIN) / (BAT_MAX - BAT_MIN) * 100, 2)
        if percent < 0:
            percent = 0
        elif percent > 100:
            percent = 100
        return percent

    def read(self):
        return self.batPin.read()
