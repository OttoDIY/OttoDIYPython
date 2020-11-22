# this is the code for reading the battery

from machine import Pin, ADC

VOLTAGE_MAX = 3.6
BAT_MAX = 4.5
BAT_MIN = 3.25
OFFSET = (100 * BAT_MIN)/(BAT_MAX - BAT_MIN)


class BatReader9:
    def __init__(self, pin = 34):
        self.batPin = ADC(Pin(pin))
        self.batPin.atten(ADC.ATTN_11DB)
        self.batPin.width(ADC.WIDTH_12BIT)

    def readBatVoltage(self):
        volt = self.batPin.read() * VOLTAGE_MAX / 4096 * 2
        if volt < BAT_MIN:
            volt = BAT_MIN
        elif volt > BAT_MAX:
            volt = BAT_MAX

        return volt

    def readBatPercent(self):
        percent = self.readBatVoltage() * (100 / (BAT_MAX - BAT_MIN)) - OFFSET
        if percent < 0:
            percent = 0
        elif percent > 100:
            percent = 100
        return percent

    def read(self):
        return self.batPin.read()
