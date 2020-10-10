# -- OttoDIY Python Project, 2020

import oscillator, time, math, store
from us import us
from machine import Pin, PWM, ADC
import songs, notes, mouths, gestures
import otto_matrix

# -- Constants
FORWARD  = const(1)
BACKWARD = const(-1)
LEFT     = const(1)
RIGHT    = const(-1)
SMALL    = const(5)
MEDIUM   = const(15)
BIG      = const(30)

def DEG2RAD(g):
    return (g * math.pi) / 180

class Otto9:
    def __init__(self):
        self._servo = [oscillator.Oscillator(), oscillator.Oscillator(), oscillator.Oscillator(),
                       oscillator.Oscillator(), oscillator.Oscillator(), oscillator.Oscillator()]
        self._servo_pins = [-1, -1, -1, -1, -1, -1]
        self._servo_trim = [0, 0, 0, 0, 0, 0]
        self._servo_position = [90, 90, 90, 90, 90, 90]  # -- initialised to what the oscillator code defaults to
        self._servo_totals = 0
        self._final_time = 0
        self._partial_time = 0
        self._increment = [0, 0, 0, 0, 0, 0]
        self._isOttoResting = True
        self.usTrigger = -1
        self.usEcho = -1
        self.buzzer = -1
        self.noiseSensor = -1

    def deinit(self):
        if hasattr(self, 'ledmatrix'):
            self.ledmatrix.deinit()

        self.detachServos()

    # --  Otto9 or Otto9Humanoid initialization
    def init(self, YL, YR, RL, RR, load_calibration, NoiseSensor, Buzzer, USTrigger, USEcho, LA = -1, RA = -1):
        self._servo_pins[0] = YL
        self._servo_pins[1] = YR
        self._servo_pins[2] = RL
        self._servo_pins[3] = RR
        self._servo_totals = 4
        if LA != -1:
            self._servo_pins[4] = LA
            self._servo_pins[5] = RA
            self._servo_totals = 6
        self.attachServos()
        self.setRestState(False)
        if load_calibration == True:
            trims = store.load('Trims', [0, 0, 0, 0, 0, 0])
            for i in range(0, self._servo_totals):
                servo_trim = trims[i]
                if servo_trim > 128:
                    servo_trim -= 256
                self._servo[i].SetTrim(servo_trim)
        for i in range(0, self._servo_totals):  # -- this could be eliminated as we already initialize
            self._servo_position[i] = 90  # -- the array from __init__() above ...

        self.noiseSensor = NoiseSensor
        self.buzzer = Buzzer
        self.usTrigger = USTrigger
        self.usEcho = USEcho

        if self.usTrigger >= 0 and self.usEcho >= 0:
            self.us = us(self.usTrigger, self.usEcho)

        if self.buzzer >= 0:
            self.buzzerPin = Pin(self.buzzer, Pin.OUT)
            self.buzzerPin.value(0)

        if self.noiseSensor >= 0:
            self.noiseSensorPin = ADC(Pin(NoiseSensor))
            self.noiseSensorPin.atten(ADC.ATTN_11DB) # read the full voltage 0-3.3V

    # --  Otto9Humanoid initialization (depreciated)
    def initHUMANOID(self, YL, YR, RL, RR, LA, RA, load_calibration, NoiseSensor, Buzzer, USTrigger, USEcho):
        self.init(YL, YR, RL, RR, load_calibration, NoiseSensor, Buzzer, USTrigger, USEcho, LA, RA)

    # -- Otto LED matrix init
    # -- Parameters:
    # --    din: data pin number
    # --    cs: chip select pin number
    # --    clk: clock pin number
    # --    rotate: orientation of LED matric
    def initMATRIX(self, din, cs, clk, rotate):
        self.ledmatrix = otto_matrix.OttoMatrix(din, cs, clk, rotate)

    # -- Otto LED matrix set intensity
    # -- Parameters:
    # --    intensity: how bright should the LED metrix be
    def matrixIntensity(self, intensity):
        self.ledmatrix.setIntensity(intensity)

    # -- Attach & Detach Functions
    def attachServos(self):
        for i in range(0, self._servo_totals):
            self._servo[i].attach(self._servo_pins[i])

    def detachServos(self):
        for i in range(0, self._servo_totals):
            self._servo[i].detach()

    # -- Oscillator trims
    def setTrims(self, YL, YR, RL, RR, LA = 0, RA = 0):
        self._servo[0].SetTrim(0 if YL is None else YL)
        self._servo[1].SetTrim(0 if YR is None else YR)
        self._servo[2].SetTrim(0 if RL is None else RL)
        self._servo[3].SetTrim(0 if RR is None else RR)
        if self._servo_totals > 4:
            self._servo[4].SetTrim(0 if LA is None else LA)
            self._servo[5].SetTrim(0 if RA is None else RA)

    def saveTrimsOnEEPROM(self):
        trims = [0, 0, 0, 0, 0, 0]
        for i in range(0, self._servo_totals):
            trims[i] = self._servo[i].getTrim()
        store.save('Trims', trims)

    # -- Basic Motion Functions
    def _moveServos(self, T, servo_target):
        self.attachServos()
        if self.getRestState() == True:
            self.setRestState(False)
        if T > 10:
            for i in range(0, self._servo_totals):
                self._increment[i] = ((servo_target[i]) - self._servo_position[i]) / (T / 10.0)
            self._final_time = time.ticks_ms() + T
            iteration = 1
            while time.ticks_ms() < self._final_time:
                self._partial_time = time.ticks_ms() + 10
                for i in range(0, self._servo_totals):
                    self._servo[i].SetPosition(int(self._servo_position[i] + (iteration * self._increment[i])))
                while time.ticks_ms() < self._partial_time:
                    pass  # pause
                iteration += 1
        else:
            for i in range(0, self._servo_totals):
                self._servo[i].SetPosition(servo_target[i])
        for i in range(0, self._servo_totals):
            self._servo_position[i] = servo_target[i]

    def _moveSingle(self, position, servo_number):
        if position > 180 or position < 0:
            position = 90
        self.attachServos()
        if self.getRestState() == True:
            self.setRestState(False)
        self._servo[servo_number].SetPosition(position)
        self._servo_position[servo_number] = position

    def oscillateServos(self, A, O, T, phase_diff, cycle=1.0):
        for i in range(0, self._servo_totals):
            self._servo[i].SetO(O[i])
            self._servo[i].SetA(A[i])
            self._servo[i].SetT(T)
            self._servo[i].SetPh(phase_diff[i])

        ref = float(time.ticks_ms())
        x = ref
        while x <= T * cycle + ref:
            for i in range(0, self._servo_totals):
                self._servo[i].refresh()
            x = float(time.ticks_ms())

    def _execute(self, A, O, T, phase_diff, steps=1.0):
        self.attachServos()
        if self.getRestState() == True:
            self.setRestState(False)

        # -- Execute complete cycles
        cycles = int(steps)
        if cycles >= 1:
            i = 0
            while i < cycles:
                self.oscillateServos(A, O, T, phase_diff)
                i += 1
        # -- Execute the final not complete cycle
        self.oscillateServos(A, O, T, phase_diff, float(steps - cycles))

    def getRestState(self):
        return self._isOttoResting

    def setRestState(self, state):
        self._isOttoResting = state

    # -- Predetermined Motion Sequences

    # -- Otto movement: HOME Otto at rest position
    def home(self):
        if self.getRestState() == False:  # -- Go to rest position only if necessary
            homes = [90, 90, 90, 90, 90, 90]  # -- All the servos at rest position
            self._moveServos(500, homes)  # -- Move the servos in half a second
            self.detachServos()
            self.setRestState(True)

    # -- Otto movement: Jump
    # --  Parameters:
    # --    steps: Number of steps
    # --    T: Period
    def jump(self, steps, T):
        up = [90, 90, 150, 30, 110, 70]
        down = [90, 90, 90, 90, 90, 90]
        self._moveServos(T, up)
        self._moveServos(T, down)

    # -- Otto gait: Walking  (forward or backward)
    # --  Parameters:
    # --    * steps:  Number of steps
    # --    * T : Period
    # --    * Dir: Direction: FORWARD / BACKWARD
    def walk(self, steps, T, dir):
        # -- Oscillator parameters for walking
        # -- Hip sevos are in phase
        # -- Feet servos are in phase
        # -- Hip and feet are 90 degrees out of phase
        # --      -90 : Walk forward
        # --       90 : Walk backward
        # -- Feet servos also have the same offset (for tiptoe a little bit)
        A = [30, 30, 20, 20, 90, 90]
        O = [0, 0, 4, -4, 0, 0]
        phase_diff = [0, 0, DEG2RAD(dir * -90), DEG2RAD(dir * -90), 0, 0]

        # -- Let's oscillate the servos!
        self._execute(A, O, T, phase_diff, steps)

    # -- Otto gait: Turning (left or right)
    # --  Parameters:
    # --   * Steps: Number of steps
    # --   * T: Period
    # --   * Dir: Direction: LEFT / RIGHT
    def turn(self, steps, T, dir):
        # -- Same coordination than for walking (see Otto.walk)
        # -- The Amplitudes of the hip's oscillators are not igual
        # -- When the right hip servo amplitude is higher, steps taken by
        # -- the right leg are bigger than the left. So, robot describes an left arc
        A = [30, 30, 20, 20, 90, 90]
        O = [0, 0, 4, -4, 0, 0]
        phase_diff = [0, 0, DEG2RAD(-90), DEG2RAD(-90), 0, 0]
        if dir == LEFT:
            A[0] = 30  # -- Left hip servo
            A[1] = 10  # -- Right hip servo
        else:
            A[0] = 10
            A[1] = 30

        # -- Let's oscillate the servos!
        self._execute(A, O, T, phase_diff, steps);

    # -- Otto gait: Lateral bend
    # --  Parameters:
    # --    steps: Number of bends
    # --    T: Period of one bend
    # --    dir: RIGHT=Right bend LEFT=Left bend
    def bend(self, steps, T, dir):
        # -- Parameters of all the movements. Default: Left bend
        bend1 = [90, 90, 40, 35, 120, 60]
        bend2 = [90, 90, 40, 105, 60, 120]
        homes = [90, 90, 90, 90, 90, 90]

        # -- Time of one bend, in order to avoid movements too fast.
        # T = max(T, 600)

        # -- Changes in the parameters if right direction is chosen
        if dir == RIGHT:
            bend1[2] = 180 - 50
            bend1[3] = 180 - 80  # -- Not 65. Otto is unbalanced
            bend2[2] = 180 - 105
            bend2[3] = 180 - 60

        # -- Time of the bend movement. Fixed parameter to avoid falls
        T2 = 800

        # -- Bend movement
        i = 0
        while i < steps:
            self._moveServos(T2 / 2, bend1)
            self._moveServos(T2 / 2, bend2)
            time.sleep_ms(int((T * 0.8)))
            self._moveServos(500, homes)
            i += 1

    # -- Otto gait: Shake a leg
    # --  Parameters:
    # --    steps: Number of shakes
    # --    T: Period of one shake
    # --    dir: RIGHT=Right leg LEFT=Left leg
    def shakeLeg(self, steps, T, dir):
        # -- This variable change the amount of shakes
        numberLegMoves = 2

        # -- Parameters of all the movements. Default: Right leg
        shake_leg1 = [90, 90, 40, 35, 90, 90]
        shake_leg2 = [90, 90, 40, 120, 100, 80]
        shake_leg3 = [90, 90, 70, 60, 80, 100]
        homes = [90, 90, 90, 90, 90, 90]

        # -- Changes in the parameters if right leg is chosen
        if dir == RIGHT:
            shake_leg1[2] = 180 - 15
            shake_leg1[3] = 180 - 40
            shake_leg2[2] = 180 - 120
            shake_leg2[3] = 180 - 58
            shake_leg3[2] = 180 - 60
            shake_leg3[3] = 180 - 58

        # -- Time of the bend movement. Fixed parameter to avoid falls
        T2 = 1000

        # -- Time of one shake, in order to avoid movements too fast.
        T = T - T2
        T = max(T, 200 * numberLegMoves)

        j = 0
        while j < steps:
            # -- Bend movement
            self._moveServos(T2 / 2, shake_leg1)
            self._moveServos(T2 / 2, shake_leg2)

            # -- Shake movement
            i = 0
            while i < numberLegMoves:
                self._moveServos(T / (2 * numberLegMoves), shake_leg3)
                self._moveServos(T / (2 * numberLegMoves), shake_leg2)
                self._moveServos(500, homes)  # -- Return to home position
                i += 1
            j += 1
        time.sleep_ms(T)

    # -- Otto movement: up & down
    # --  Parameters:
    # --    * steps: Number of jumps
    # --    * T: Period
    # --    * h: Jump height: SMALL / MEDIUM / BIG
    # --              (or a number in degrees 0 - 90)
    def updown(self, steps, T, h):
        # -- Both feet are 180 degrees out of phase
        # -- Feet amplitude and offset are the same
        # -- Initial phase for the right foot is -90, that it starts
        # --   in one extreme position (not in the middle)
        A = [0, 0, h, h, h, h]
        O = [0, 0, h, -h, h, -h]
        phase_diff = [0, 0, DEG2RAD(-90), DEG2RAD(90), DEG2RAD(-90), DEG2RAD(90)]

        # -- Let's oscillate the servos!
        self._execute(A, O, T, phase_diff, steps)

    # -- Otto movement: swinging side to side
    # --  Parameters:
    # --     steps: Number of steps
    # --     T : Period
    # --     h : Amount of swing (from 0 to 50 aprox)
    def swing(self, steps, T, h):
        # -- Both feets are in phase. The offset is half the amplitude
        # -- It causes the robot to swing from side to side
        A = [0, 0, h, h, h, h]
        O = [0, 0, h / 2, -h / 2, h, -h]
        phase_diff = [0, 0, DEG2RAD(0), DEG2RAD(0), DEG2RAD(0), DEG2RAD(0)]

        # -- Let's oscillate the servos!
        self._execute(A, O, T, phase_diff, steps)

    # -- Otto movement: swinging side to side without touching the floor with the heel
    # --  Parameters:
    # --     steps: Number of steps
    # --     T : Period
    # --     h : Amount of swing (from 0 to 50 aprox)
    def tiptoeSwing(self, steps, T, h):
        # -- Both feets are in phase. The offset is not half the amplitude in order to tiptoe
        # -- It causes the robot to swing from side to side
        A = [0, 0, h, h, h, h]
        O = [0, 0, h, -h, h, -h]
        phase_diff = [0, 0, 0, 0, 0, 0]

        # -- Let's oscillate the servos!
        self._execute(A, O, T, phase_diff, steps)

    # -- Otto gait: Jitter
    # --  Parameters:
    # --    steps: Number of jitters
    # --    T: Period of one jitter
    # --    h: height (Values between 5 - 25)
    def jitter(self, steps, T, h):
        # -- Both feet are 180 degrees out of phase
        # -- Feet amplitude and offset are the same
        # -- Initial phase for the right foot is -90, that it starts
        # --   in one extreme position (not in the middle)
        # -- h is constrained to avoid hit the feets
        h = min(25, h)
        A = [h, h, 0, 0, 0, 0]
        O = [0, 0, 0, 0, 0, 0]
        phase_diff = [DEG2RAD(-90), DEG2RAD(90), 0, 0, 0, 0]

        # -- Let's oscillate the servos!
        self._execute(A, O, T, phase_diff, steps)

    # -- Otto gait: Ascending & turn (Jitter while up&down)
    # --  Parameters:
    # --    steps: Number of bends
    # --    T: Period of one bend
    # --    h: height (Values between 5 - 15)
    def ascendingTurn(self, steps, T, h):
        # -- Both feet and legs are 180 degrees out of phase
        # -- Initial phase for the right foot is -90, that it starts
        # --   in one extreme position (not in the middle)
        # -- h is constrained to avoid hit the feets
        h = min(13, h)
        A = [h, h, h, h, 40, 40]
        O = [0, 0, h + 4, -h + 4, 0, 0]
        phase_diff = [DEG2RAD(-90), DEG2RAD(90), DEG2RAD(-90), DEG2RAD(90), 0, 0]

        # -- Let's oscillate the servos!
        self._execute(A, O, T, phase_diff, steps)

    # -- Otto gait: Moonwalker. Otto moves like Michael Jackson
    # --  Parameters:
    # --    Steps: Number of steps
    # --    T: Period
    # --    h: Height. Typical valures between 15 and 40
    # --    dir: Direction: LEFT / RIGHT
    def moonwalker(self, steps, T, h, dir):
        # -- This motion is similar to that of the caterpillar robots: A travelling
        # -- wave moving from one side to another
        # -- The two Otto's feet are equivalent to a minimal configuration. It is known
        # -- that 2 servos can move like a worm if they are 120 degrees out of phase
        # -- In the example of Otto, two feet are mirrored so that we have:
        # --    180 - 120 = 60 degrees. The actual phase difference given to the oscillators
        # --  is 60 degrees.
        # --  Both amplitudes are equal. The offset is half the amplitud plus a little bit of
        # -   offset so that the robot tiptoe lightly
        A = [0, 0, h, h, h, h]
        O = [0, 0, h / 2 + 2, -h / 2 - 2, -h, h]
        phi = -dir * 90
        phase_diff = [0, 0, DEG2RAD(phi), DEG2RAD(-60 * dir + phi), DEG2RAD(phi), DEG2RAD(phi)]

        # -- Let's oscillate the servos!
        self._execute(A, O, T, phase_diff, steps);

    # -- Otto gait: Crusaito. A mixture between moonwalker and walk
    # --   Parameters:
    # --     steps: Number of steps
    # --     T: Period
    # --     h: height (Values between 20 - 50)
    # --     dir:  Direction: LEFT / RIGHT
    def crusaito(self, steps, T, h, dir):
        A = [25, 25, h, h, 0, 0]
        O = [0, 0, h / 2 + 4, -h / 2 - 4, 0, 0]
        phase_diff = [90, 90, DEG2RAD(0), DEG2RAD(-60 * dir), 0, 0]

        # -- Let's oscillate the servos!
        self._execute(A, O, T, phase_diff, steps);

    # -- Otto gait: Flapping
    # --  Parameters:
    # --    steps: Number of steps
    # --    T: Period
    # --    h: height (Values between 10 - 30)
    # --    dir: direction: FOREWARD, BACKWARD
    def flapping(self, steps, T, h, dir):
        A = [12, 12, h, h, 0, 0]
        O = [0, 0, h - 10, -h + 10, 0, 0]
        phase_diff = [DEG2RAD(0), DEG2RAD(180), DEG2RAD(-90 * dir), DEG2RAD(90 * dir), 0, 0]

        # -- Let's oscillate the servos!
        self._execute(A, O, T, phase_diff, steps)

    # -- Otto movement: Hands up
    def handsup(self):
        if self._servo_totals > 4:
            homes = [90, 90, 90, 90, 20, 160]
            self._moveServos(1000, homes)

    # -- Otto movement: Wave , either left or right
    def handwave(self, dir):
        if self._servo_totals > 4:
            if dir == RIGHT:
                A = [0, 0, 0, 0, 30, 0]
                O = [0, 0, 0, 0, -30, -40]
                phase_diff = [0, 0, 0, 0, DEG2RAD(0), 0]
                # -- Let's oscillate the servos!
                self._execute(A, O, 1000, phase_diff, 5)
            if dir == LEFT:
                A = [0, 0, 0, 0, 0, 30]
                O = [0, 0, 0, 0, 40, 60]
                phase_diff = [0, 0, 0, 0, 0, DEG2RAD(0)]
                # -- Let's oscillate the servos!
                self._execute(A, O, 1000, phase_diff, 1)

    # -- Otto read noise sensor analog
    # -- return the reading
    def getNoise(self):
        if self.noiseSensor >= 0:
            return self.noiseSensorPin.read()
        else:
            return 0

    # -- Otto get US distance
    # -- returns distance in cm
    def getDistance(self):
        return self.us.distance_cm()

    # --   Mouths & Animations

    # -- setLed in matrix
    # -- Parameters:
    # --    x: x of led 0-7
    # --    y: y of led 0-7
    # --    value: on of off (1 or 0)
    def setLed(self, x, y, value):
        if hasattr(self, 'ledmatrix'):
            self.ledmatrix.setDot(x, y, value)

    # -- putAnimationMouth in matrix
    # -- Parameters:
    # --    mouth: which mouth array to use
    # --    index: index of mouth to use
    def putAnimationMouth(self, mouth, index):
        if hasattr(self, 'ledmatrix'):
            try:
                self.ledmatrix.writeFull(mouths.aniMouths[mouth][index])
            except:
                pass

    # -- putMouth in matrix
    # -- Parameters:
    # --    mouth: either a bitarray of the mouth or an index into the mouth dictonary
    def putMouth(self, mouth):
        if hasattr(self, 'ledmatrix'):
            if type(mouth) == bytes or type(mouth) == bytearray:
                self.ledmatrix.writeFull(mouth)
            else:
                try:
                    bits = mouths.mouths[mouth]
                    self.ledmatrix.writeFull(bits)
                except:
                    pass

    # -- clear the mouth
    # -- Parameters:
    def clearMouth(self):
        if hasattr(self, 'ledmatrix'):
            self.ledmatrix.clearMatrix()

    # -- write text to matrix
    # -- Parameters:
    # --    txt: text to display
    # --    scrollspeed
    def writeText(self, txt, scrollspeed):
        if hasattr(self, 'ledmatrix'):
            uTxt = txt.upper()
            a = len(uTxt)
            if a > 19:
                b = 19
            else:
                b = a
            for charNumber in range(b):
                self.ledmatrix.sendChar(uTxt[charNumber], charNumber, b, scrollspeed)

    # -- Tone stuff

    # -- Otto play tone
    # -- Parameters:
    # --    freq: Frequency of tone
    # --    duration: time to play tone
    # --    silentDur: time to play silence
    def _tone(self, freq, duration, silentDur):
        if self.buzzer >= 0:
            if silentDur <= 0:
                silentDur = 1
            # -- use 50% duty cycle
            pwm = PWM(self.buzzerPin, int(round(freq)), 512)
            time.sleep_ms(duration)
            pwm.deinit()
            time.sleep_ms(silentDur)

    # -- Otto bend tone from one tone to another
    # -- Parameters:
    # --     initFreq: Starting frequency
    # --     finalFreq: Ending frequency
    # --     prop: proportion to modify by
    # --     noteDur: time to play note(s)
    # --
    def bendTones(self, initFreq, finalFreq, prop, noteDur, silentDur):
        if silentDur <= 0:
            silentDur = 1

        if initFreq < finalFreq:
            i = initFreq
            while i < finalFreq:
                self._tone(i, noteDur, silentDur)
                i = i * prop
        else:
            i = initFreq
            while i > finalFreq:
                self._tone(i, noteDur, silentDur)
                i = i / prop

    # -- Otto sing a song
    # -- Parameters:
    # --    songName: number of song
    def sing(self, songName):
        if songName == songs.CONNECTION:
            self._tone(notes.E5, 50, 30)
            self._tone(notes.E6, 55, 25)
            self._tone(notes.A6, 60, 10)
        elif songName == songs.DISCONNECTION:
            self._tone(notes.E5, 50, 30)
            self._tone(notes.A6, 55, 25)
            self._tone(notes.E6, 50, 10)
        elif songName == songs.BUTTONPUSHED:
            self.bendTones(notes.E6, notes.G6, 1.03, 20, 2)
            time.sleep_ms(30)
            self.bendTones(notes.E6, notes.D7, 1.04, 10, 2)
        elif songName == songs.MODE1:
            self.bendTones(notes.E6, notes.A6, 1.02, 30, 10)
        elif songName == songs.MODE2:
            self.bendTones(notes.G6, notes.D7, 1.03, 30, 10)
        elif songName == songs.MODE3:
            self._tone(notes.E6, 50, 100)
            self._tone(notes.G6, 50, 80)
            self._tone(notes.D7, 300, 0)
        elif songName == songs.SURPRISE:
            self.bendTones(800, 2150, 1.02, 10, 1)
            self.bendTones(2149, 800, 1.03, 7, 1)
        elif songName == songs.OHOOH:
            self.bendTones(880, 2000, 1.04, 8, 3)
            time.sleep_ms(200)
            i = 880
            while i < 2000:
                self._tone(notes.C6, 10, 10)
                i = i * 1.04
        elif songName == songs.OHOOH2:
            self.bendTones(1880, 3000, 1.03, 8, 3)
            time.sleep_ms(200)
            i = 1880
            while i < 3000:
                self._tone(notes.C6, 10, 10)
                i = i * 1.03
        elif songName == songs.CUDDLY:
            self.bendTones(700, 900, 1.03, 16, 4)
            self.bendTones(899, 650, 1.01, 18, 7)
        elif songName == songs.SLEEPING:
            self.bendTones(100, 500, 1.04, 10, 10)
            time.sleep_ms(500)
            self.bendTones(400, 100, 1.04, 10, 1)
        elif songName == songs.HAPPY:
            self.bendTones(1500, 2500, 1.05, 20, 8)
            self.bendTones(2499, 1500, 1.05, 25, 8)
        elif songName == songs.SUPERHAPPY:
            self.bendTones(2000, 6000, 1.05, 8, 3)
            time.sleep_ms(50)
            self.bendTones(5999, 2000, 1.05, 13, 2)
        elif songName == songs.HAPPYSHORT:
            self.bendTones(1500, 2000, 1.05, 15, 8)
            time.sleep_ms(100)
            self.bendTones(1900, 2500, 1.05, 10, 8)
        elif songName == songs.SAD:
            self.bendTones(880, 669, 1.02, 20, 200)
        elif songName == songs.CONFUSED:
            self.bendTones(1000, 1700, 1.03, 8, 2)
            self.bendTones(1699, 500, 1.04, 8, 3)
            self.bendTones(1000, 1700, 1.05, 9, 10)
        elif songName == songs.FART1:
            self.bendTones(1600, 3000, 1.02, 2, 15)
        elif songName == songs.FART2:
            self.bendTones(2000, 6000, 1.02, 2, 20)
        elif songName == songs.FART3:
            self.bendTones(1600, 4000, 1.02, 2, 20)
            self.bendTones(4000, 3000, 1.02, 2, 20)

    # -- Gestures

    # -- Play Gesture
    # -- Parameters:
    # --    gesture: which gesture to do
    def playGesture(self, gesture):
        if gesture == gestures.OTTOHAPPY:
            self._tone(notes.E5, 50, 30)
            self.putMouth(mouths.SMILE)
            self.sing(songs.HAPPYSHORT)
            self.swing(1, 800, 20)
            self.sing(songs.HAPPYSHORT)
            self.home()
            self.putMouth(mouths.HAPPYOPEN)
        elif gesture == gestures.OTTOSUPERHAPPY:
            self.putMouth(mouths.HAPPYOPEN)
            self.sing(songs.HAPPY)
            self.putMouth(mouths.HAPPYCLOSED)
            self.tiptoeSwing(1, 500, 20)
            self.putMouth(mouths.HAPPYOPEN)
            self.sing(songs.SUPERHAPPY)
            self.tiptoeSwing(1, 500, 20)
            self.home()
            self.putMouth(mouths.HAPPYOPEN)
        elif gesture == gestures.OTTOSAD:
            self.putMouth(mouths.SAD)
            self._moveServos(700, [110, 70, 20, 160, 90, 90])
            self.bendTones(880, 830, 1.02, 20, 200)
            self.putMouth(mouths.SADCLOSED)
            self.bendTones(830, 790, 1.02, 20, 200)
            self.putMouth(mouths.SADOPEN)
            self.bendTones(790, 740, 1.02, 20, 200)
            self.putMouth(mouths.SADCLOSED)
            self.bendTones(740, 700, 1.02, 20, 200)
            self.putMouth(mouths.SADOPEN)
            self.bendTones(700, 669, 1.02, 20, 200)
            self.putMouth(mouths.SAD)
            time.sleep_ms(500)

            self.home()
            time.sleep_ms(300)
            self.putMouth(mouths.HAPPYOPEN)
        elif gesture == gestures.OTTOSLEEPING:
            self._moveServos(700, [100, 80, 60, 120, 90, 90])
            for i in range(4):
                self.putAnimationMouth(mouths.DREAMMOUTH, 0)
                self.bendTones(100, 200, 1.04, 10, 10)
                self.putAnimationMouth(mouths.DREAMMOUTH, 1)
                self.bendTones(200, 300, 1.04, 10, 10)
                self.putAnimationMouth(mouths.DREAMMOUTH, 2)
                self.bendTones(300, 500, 1.04, 10, 10)
                time.sleep_ms(500)
                self.putAnimationMouth(mouths.DREAMMOUTH, 1)
                self.bendTones(400, 250, 1.04, 10, 1)
                self.putAnimationMouth(mouths.DREAMMOUTH, 0)
                self.bendTones(250, 100, 1.04, 10, 1)
                time.sleep_ms(500)

            self.putMouth(mouths.LINEMOUTH)
            self.sing(songs.CUDDLY)

            self.home()
            self.putMouth(mouths.HAPPYOPEN)
        elif gesture == gestures.OTTOFART:
            self._moveServos(500, [90, 90, 145, 122, 90, 90])
            time.sleep_ms(300)
            self.putMouth(mouths.LINEMOUTH)
            self.sing(songs.FART1)
            self.putMouth(mouths.TONGUEOUT)
            time.sleep_ms(250)
            self._moveServo(500, [90, 90, 80, 122, 90, 90])
            time.sleep_ms(300)
            self.putMouth(mouths.LINEMOUTH)
            self.sing(songs.FART2)
            self.putMouth(mouths.TONGUEOUT)
            time.sleep_ms(250)
            self._moveServos(500.[90, 90, 145, 80, 90, 90])
            time.sleep_ms(300)
            self.putMouth(mouths.LINEMOUTH)
            self.sing(songs.FART3)
            self.putMouth(mouths.TONGUEOUT)
            time.sleep_ms(300)

            self.home()
            time.sleep_ms(500)
            self.putMouth(mouths.HAPPYOPEN)
        elif gesture == gestures.OTTOCONFUSED:
            self._moveServos(300, [110, 70, 90, 90, 90, 90])
            self.putMouth(mouths.CONFUSED)
            self.sing(songs.CONFUSED)
            time.sleep_ms(500)

            self.home()
            self.putMouth(mouths.HAPPYOPEN)
        elif gesture == gestures.OTTOLOVE:
            self.putMouth(mouths.HEART)
            self.sing(songs.CUDDLY)
            self.crusaito(2, 1500, 25, 1)

            self.home()
            self.sing(songs.HAPPYSHORT)
            self.putMouth(mouths.HAPPYOPEN)
        elif gesture == gestures.OTTOANGRY:
            self._moveServos(300, [90, 90, 70, 110, 90, 90])
            self.putMouth(mouths.ANGRY)

            self._tone(notes.A5, 100, 30)
            self.bendTones(notes.A5, notesD6, 1.02, 7, 4)
            self.bendTones(notes.D6, notes.G6, 1.02, 10, 1)
            self.bendTones(notes.G6, notes.A5, 1.02, 10, 1)
            time.sleep_ms(15)
            self.bendTones(notes.A5, notes.E5, 1.02, 20, 4)
            time.sleep_ms(400)
            self._moveServos(200, [110, 110, 90, 90, 90, 90])
            self.bendTones(notes.A5, notes.D6, 1.02, 20, 4)
            self._moveServos(200, [70, 70, 90, 90, 90, 90])
            self.bendTones(notes.A5, notes.E5, 1.02, 20, 4)

            self.home()
            self.putMouth(mouths.HAPPYOPEN)
        elif gesture == gestures.OTTOFRETFUL:
            self.putMouth(mouths.ANGRY)
            self.bendTones(notes.A5, notes.D6, 1.02, 20, 4)
            self.bendTones(notes.A5, notes.E5, 1.02, 20, 4)
            time.sleep_ms(300)
            self.putMouth(mouths.LINEMOUTH)

            for i in range(4):
                self._moveServos(100, [90, 90, 90, 110, 90, 90])
                self.home()

            self.putMouth(mouths.ANGRY)
            time.sleep_ms(500)

            self.home()
            self.putMouth(mouths.HAPPYOPEN)
        elif gesture == gestures.OTTOMAGIC:
            for i in range(4):

                noteM = 400

                for index in range(6):
                    self.putAnimationMouth(mouths.aniMouths[mouths.ADIVINAWI], index)
                    self.bendTones(noteM, noteM + 100, 1.04, 10, 10)
                    noteM += 100

                self.clearMouth()
                self.bendTones(noteM - 100, noteM + 100, 1.04, 10, 10)

                for index in range(6):
                    self.putAnimationMouth(mouths.aniMouths[mouths.ADIVINAWI], index)
                    self.bendTones(noteM, noteM + 100, 1.04, 10, 10)
                    noteM -= 100

            time.sleep_ms(300)
            self.putMouth(mouth.HAPPYOPEN);
        elif gesture == gestures.OTTOWAVE:
            for i in range(2):
                noteW = 500

                for index in range(10):
                    self.putAnimationMouth(mouths.aniMouths[mouths.WAVE], index)
                    self.bendTones(noteW, noteW + 100, 1.02, 10, 10)
                    noteW += 101
                for index in range(10):
                    self.putAnimationMouth(mouths.aniMouths[mouths.WAVE], index)
                    self.bendTones(noteW, noteW + 100, 1.02, 10, 10)
                    noteW += 101
                for index in range(10):
                    self.putAnimationMouth(mouths.aniMouths[mouths.WAVE], index)
                    self.bendTones(noteW, noteW - 100, 1.02, 10, 10)
                    noteW -= 101
                for index in range(10):
                    self.putAnimationMouth(mouths.aniMouths[mouths.WAVE], index)
                    self.bendTones(noteW, noteW - 100, 1.02, 10, 10)
                    noteW -= 101

            self.clearMouth()
            time.sleep_ms(100)
            self.putMouth(mouths.HAPPYOPEN)
        elif gesture == gestures.OTTOVICTORY:
            self.putMouth(mouths.SMALLSURPRISE)
            for i in range(60):
                self._moveServos(10, [9, 90, 90 + i, 90 - i, 90, 90])
                self._tone(1600 + i * 20, 15, 1)

            self.putMouth(mouths.BIGSURPRISE)
            for i in range(60):
                self._moveServos(10, [90, 90, 150 - i, 30 + i, 90, 90])
                self._tone(2800 + i * 20, 15, 1)

            self.putMouth(mouths.HAPPYOPEN)

            self.tiptoeSwing(1, 500, 20)
            self.sing(songs.SUPERHAPPY)
            self.putMouth(mouths.HAPPYCLOSED)
            self.tiptoeSwing(1, 500, 20)

            self.home()
            self.clearMouth()
            self.putMouth(mouths.HAPPYOPEN)
        elif gesture == gestures.OTTOFAIL:
            self.putMouth(mouths.SADOPEN)
            self._moveServos(300, [90, 90, 70, 35, 90, 90])
            self._tone(900, 200, 1)
            self.putMouth(mouths.SADCLOSED)
            self._moveServos(300, [90, 90, 55, 35, 90, 90])
            self._tone(600, 200, 1)
            self.putMouth(mouths.CONFUSED)
            self._moveServos(300, [90, 90, 42, 35, 90, 90])
            self._tone(300, 200, 1)
            self._moveServos(300, [90, 90, 34, 35, 90, 90])
            self.putMouth(mouths.XMOUTH)

            self.detachServos()
            self._tone(150, 2200, 1)

            time.sleep_ms(600)
            self.clearMouth()
            self.putMouth(mouths.HAPPYOPEN)
            self.home()

# end
