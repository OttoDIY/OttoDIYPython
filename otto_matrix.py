#-- OttDIY Python Project, 2020

from machine import Pin, SPI
import otto_font, time

DECODEMODE  = const(0x09)
INTENSITY   = const(0x0a)
SCANLIMIT   = const(0x0b)
SHUTDOWN    = const(0x0c)
DISPLAYTEST = const(0x0f)

class OttoMatrix:
    #-- initialize an LED matrix with all the pins
    #-- Parameters:
    #--    data: pin to use for data
    #--    cs: pin to use for chip select low = selected
    #--    clock: pin to use as clock
    #--    num: number of leds in chain
    #--    rotation: 1-4 rotation of LED
    def __init__(self, data = 5, cs = 18, clock = 19, num = 1, rotation = 1):
        self.spi = SPI(2, baudrate = 125000, polarity = 0, phase = 0, firstbit = SPI.MSB, sck = Pin(clock), mosi = Pin(data))
        self.cs = Pin(cs, Pin.OUT)
        self.cs.value(1) #start with the select high
        self.num = num
        if rotation > 4 or rotation <= 0:
            rotation = 1
        self.rotation = rotation
        self.buffer = bytearray(8 * self.num)
        self.charBuffer = bytearray(160)

        self.setCommand(SCANLIMIT, 0x07)
        self.setCommand(DECODEMODE, 0x00)
        self.setCommand(SHUTDOWN, 0x01)
        self.setCommand(DISPLAYTEST, 0x00)

        self.clearMatrix()
        self.setIntensity(0x0f)

    def deinit(self):
#        print("OttoMatrix del called")
        self.spi.deinit()
        del(self.spi)

    #-- Set the intensity of the LED matrix
    #-- Parameters:
    #--    intensity: how bright the LEDs are
    def setIntensity(self, intensity):
        self.setCommand(INTENSITY, intensity)

    #-- Clear all the leds and the buffers
    def clearMatrix(self):
        for i in range(len(self.buffer)):
            self.setColumnAll(i, 0)
            self.buffer[i] = 0

        for i in range(len(self.charBuffer)):
            self.charBuffer[i] = 0

    #-- Send a command to the LED matrix
    #-- Parameters:
    #--     command: command number
    #--     value: command value
    def setCommand(self, command, value):
        buf = bytearray(2)
        buf[0] = command
        buf[1] = value
        # we must first set the CS low
        self.cs.value(0)
        for i in range(self.num):
            self.spi.write(buf)
        #we must set the CS HIGH
        self.cs.value(1)

    #-- Set a column to a value
    #-- Parmeters:
    #--    col: which column
    #--    value: value to set
    def setColumn(self, col, value):
        n = col // 8
        c = col % 8
        buf = bytearray(2)
        buf[0] = c + 1
        buf[1] = value
        self.buffer[col] = value

        # we must first set the CS low
        self.cs.value(0)
        for i in range(self.num):
            if i == n:
                self.spi.write(buf)
            else:
                self.spi.write(b'\x00\x00')
                
        #we must set the CS HIGH
        self.cs.value(1)


 
    #-- Set all Led matrixes column to a value
    #-- Parmeters:
    #--    col: which column
    #--    value: value to set
    def setColumnAll(self, col, value):
        buf = bytearray(2)
        buf[0] = col + 1
        buf[1] = value

        # we must first set the CS low
        self.cs.value(0)
        for i in range(self.num):
            self.spi.write(buf)
            self.buffer[col * i] = value
        #we must set the CS HIGH
        self.cs.value(1)

    #-- Set a dot
    #-- Parmeters:
    #--    col: which column
    #--    row: which row
    #--    value: value to set
    def setDot(self, col, row, value):
        if value == 0:
            self.buffer[col] = self.buffer[col] & ~(1 << row)
        else:
            self.buffer[col] = self.buffer[col] | (1 << row)
            
        n = col // 8
        c = col % 8
        buf = bytearray(2)
        buf[0] = c + 1
        buf[1] = self.buffer[col]

        # we must first set the CS low
        self.cs.value(0)
        for i in range(self.num):
            if i == n:
                self.spi.write(buf)
            else:
                self.spi.write(b'\x00\x00')
                
        #we must set the CS HIGH
        self.cs.value(1)

    #-- take a 30 bit value and write it to a 6x5 array
    #-- Parmeters:
    #--    value: 30 bits if led on/off info
    def writeFull(self, value):
        for r in range(5):
            for c in range(6):
                bit = 1 & (value >> (r * 6 + c))
                if self.rotation == 1:
                    self.setDot(6 - c, 7 - r, bit)
                if self.rotation == 2:
                    self.setDot(1 + c, r, bit)
                if self.rotation == 3:
                    self.setDot(r, 6 - c, bit)
                if self.rotation == 4:
                    self.setDot(7 - r, 6 - c, bit)
       
    #-- display a character on the LED matrix
    #-- Parameters:
    #--    data: character to display
    #--    pos: position to display it at
    #--    number: total number of characters we are displaying
    #--    scrollspeed: how fast to scroll text
    def sendChar(self, data, pos, number, scrollspeed):
        if scrollspeed < 50:
            scrollspeed = 50
        if scrollspeed > 150:
            scrollspeed = 150
        charPos = pos * 8
        try:
            ch = otto_font.font_6x8[data]
        except:
            ch = otto_font.font_6x8['+']

        self.charBuffer[0 + charPos] = 0
        self.charBuffer[1 + charPos: 6 + charPos] = ch
        self.charBuffer[7 + charPos] = 0

        #-- this is the last character so display them
        if number == (pos + 1):
            for c in range(8):
                value = self.charBuffer[c]
                for r in range(8):
                    bit = 1 & (value >> r)
                    if self.rotation == 1:
                        self.setDot(c, 7 - r, bit)
                    if self.rotation == 2:
                        self.setDot(7 - c, r, bit)
                    if self.rotation == 3:
                        self.setDot(r, c, bit)
                    if self.rotation == 4:
                        self.setDot(7 - r, 7 - c, bit)

            #-- show the first character for longer
            time.sleep_ms(500)

            for i in range((number * 8) - 1):
                self.charBuffer[i] = self.charBuffer[i + 1]
                for c in range(8):
                    bv = self.charBuffer[c + 1 + i]
                    for r in range(8):
                        bit = 1 & (bv >> r)
                        if self.rotation == 1:
                            self.setDot(c, 7 - r, bit)
                        if self.rotation == 2:
                            self.setDot(7 - c, r, bit)
                        if self.rotation == 3:
                            self.setDot(r, c, bit)
                        if self.rotation == 4:
                            self.setDot(7 - r, 7 - c, bit)
                time.sleep_ms(scrollspeed)

            self.clearMatrix()
