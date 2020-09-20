"""
OttoDIY Python Project, 2020 | sfranzyshen
"""

import oscillator, time, math
from us import us
from machine import Pin
from machine import PWM

#-- Constants
FORWARD = 1
BACKWARD = -1
LEFT = 1
RIGHT = -1
SMALL = 5
MEDIUM = 15
BIG = 30

#-- Song CONSTANTS

S_CONNECTION = 0
S_DISCONNECTION = 1
S_BUTTONPUSHED = 2
S_MODE1 = 3
S_MODE2 = 4
S_MODE3 = 5
S_SURPRISE = 6
S_OHOOH = 7
S_OHOOH2 = 8
S_CUDDLY = 9
S_SLEEPING = 10
S_HAPPY = 11
S_SUPERHAPPY = 12
S_HAPPYSHORT = 13
S_SAD = 14
S_CONFUSED = 15
S_FART1 = 16
S_FART2 = 17
S_FART3 = 18

#-- Note constants
NOTE_C0  = 16.35
NOTE_Db0 = 17.32
NOTE_D0  = 18.35
NOTE_Eb0 = 19.45
NOTE_E0  = 20.6
NOTE_F0  = 21.83
NOTE_Gb0 = 23.12
NOTE_G0  = 24.5
NOTE_Ab0 = 25.96
NOTE_A0  = 27.5
NOTE_Bb0 = 29.14
NOTE_B0  = 30.87
NOTE_C1  = 32.7
NOTE_Db1 = 34.65
NOTE_D1  = 36.71
NOTE_Eb1 = 38.89
NOTE_E1  = 41.2
NOTE_F1  = 43.65
NOTE_Gb1 = 46.25
NOTE_G1  = 49
NOTE_Ab1 = 51.91
NOTE_A1  = 55
NOTE_Bb1 = 58.27
NOTE_B1  = 61.74
NOTE_C2  = 65.41
NOTE_Db2 = 69.3
NOTE_D2  = 73.42
NOTE_Eb2 = 77.78
NOTE_E2  = 82.41
NOTE_F2  = 87.31
NOTE_Gb2 = 92.5
NOTE_G2  = 98
NOTE_Ab2 = 103.83
NOTE_A2  = 110
NOTE_Bb2 = 116.54
NOTE_B2  = 123.47
NOTE_C3  = 130.81
NOTE_Db3 = 138.59
NOTE_D3  = 146.83
NOTE_Eb3 = 155.56
NOTE_E3  = 164.81
NOTE_F3  = 174.61
NOTE_Gb3 = 185
NOTE_G3  = 196
NOTE_Ab3 = 207.65
NOTE_A3  = 220
NOTE_Bb3 = 233.08
NOTE_B3  = 246.94
NOTE_C4  = 261.63
NOTE_Db4 = 277.18
NOTE_D4  = 293.66
NOTE_Eb4 = 311.13
NOTE_E4  = 329.63
NOTE_F4  = 349.23
NOTE_Gb4 = 369.99
NOTE_G4  = 392
NOTE_Ab4 = 415.3
NOTE_A4  = 440
NOTE_Bb4 = 466.16
NOTE_B4  = 493.88
NOTE_C5  = 523.25
NOTE_Db5 = 554.37
NOTE_D5  = 587.33
NOTE_Eb5 = 622.25
NOTE_E5  = 659.26
NOTE_F5  = 698.46
NOTE_Gb5 = 739.99
NOTE_G5  = 783.99
NOTE_Ab5 = 830.61
NOTE_A5  = 880
NOTE_Bb5 = 932.33
NOTE_B5  = 987.77
NOTE_C6  = 1046.5
NOTE_Db6 = 1108.73
NOTE_D6  = 1174.66
NOTE_Eb6 = 1244.51
NOTE_E6  = 1318.51
NOTE_F6  = 1396.91
NOTE_Gb6 = 1479.98
NOTE_G6  = 1567.98
NOTE_Ab6 = 1661.22
NOTE_A6  = 1760
NOTE_Bb6 = 1864.66
NOTE_B6  = 1975.53
NOTE_C7  = 2093
NOTE_Db7 = 2217.46
NOTE_D7  = 2349.32
NOTE_Eb7 = 2489.02
NOTE_E7  = 2637.02
NGOTE_F7  = 2793.83
NOTE_Gb7 = 2959.96
NOTE_G7  = 3135.96
NOTE_Ab7 = 3322.44
NOTE_A7  = 3520
NOTE_Bb7 = 3729.31
NOTE_B7  = 3951.07
NOTE_C8  = 4186.01
NOTE_Db8 = 4434.92
NOTE_D8  = 4698.64
NOTE_Eb8 = 4978.03


def DEG2RAD(g):
	return (g * math.pi) / 180
  
class Eeprom:
	def read(i):
		return 0

	def write(i, trim):
		pass

EEPROM = Eeprom

class Otto9:
	def __init__(self):
		self._servo = [oscillator.Oscillator(), oscillator.Oscillator(), oscillator.Oscillator(), oscillator.Oscillator()]
		self._servo_pins = [0, 0, 0, 0]
		self._servo_trim = [0, 0, 0, 0]
		self._servo_position = [90, 90, 90, 90] #-- initialised to what the oscillator code defaults to 
		self._final_time = 0
		self._partial_time = 0
		self._increment = [0, 0, 0, 0]
		self._isOttoResting = True
		self.usTrigger = -1
		self.usEcho = -1
		self.buzzer = -1
		self.noiseSensor = -1
		
	def init(self, YL, YR, RL, RR, load_calibration, NoiseSensor, Buzzer, USTrigger, USEcho):  
		self._servo_pins[0] = YL
		self._servo_pins[1] = YR
		self._servo_pins[2] = RL
		self._servo_pins[3] = RR
		self.attachServos()
		self.setRestState(False)
		if load_calibration == True:
			for i in range(0, 4):
				servo_trim = EEPROM.read(i)
				if servo_trim > 128:
					servo_trim -= 256
				self._servo[i].SetTrim(servo_trim)
		for i in range(0, 4):			#-- this could be eliminated as we already initialize 
			self._servo_position[i] = 90	#-- the array from __init__() above ...

		self.noiseSensor = NoiseSensor
		self.buzzer = Buzzer
		self.usTrigger = USTrigger
		self.usEcho = USEcho

		if self.usTrigger >= 0 and self.usEcho >= 0 :
			self.us = us(self.usTrigger, self.usEcho)

		if self.buzzer >= 0:
			self.buzzerPin = Pin(self.buzzer, Pin.OUT)
			self.buzzerPin.value(0)
			
	#-- ATTACH & DETACH FUNCTIONS
	
	def attachServos(self):
		for i in range(0, 4):
			self._servo[i].attach(self._servo_pins[i])

	def detachServos(self):
		for i in range(0, 4):
			self._servo[i].detach()

	#-- OSCILLATORS TRIMS

	def setTrims(self, YL, YR, RL, RR):
		self._servo[0].SetTrim(YL)
		self._servo[1].SetTrim(YR)
		self._servo[2].SetTrim(RL)
		self._servo[3].SetTrim(RR)

	def saveTrimsOnEEPROM(self):
		for i in range(0, 4):
			EEPROM.write(i, self._servo[i].getTrim())

	#-- BASIC MOTION FUNCTIONS

	def _moveServos(self, T, servo_target):
		self.attachServos()
		if self.getRestState() == True:
			self.setRestState(False)
		if T > 10:
			for i in range(0, 4):
				self._increment[i] = ((servo_target[i]) - self._servo_position[i]) / (T / 10.0)
			self._final_time = time.ticks_ms() + T
			iteration = 1
			while time.ticks_ms() < self._final_time:
				self._partial_time = time.ticks_ms() + 10
				for i in range(0, 4):
					self._servo[i].SetPosition(int(self._servo_position[i] + (iteration * self._increment[i])))
				while time.ticks_ms() < self._partial_time:
					pass # pause
				iteration += 1
		else:
			for i in range(0, 4):
				self._servo[i].SetPosition(servo_target[i])
		for i in range(0, 4):
			self._servo_position[i] = servo_target[i]

	def _moveSingle(self, position, servo_number):
		if position > 180 or position < 0:
			position = 90
		self.attachServos()
		if self.getRestState() == True:
			self.setRestState(False)
		self._servo[servo_number].SetPosition(position)
		self._servo_position[servo_number] = position

	def oscillateServos(self, A, O, T, phase_diff, cycle = 1.0):
		for i in range(0, 4):
			self._servo[i].SetO(O[i])
			self._servo[i].SetA(A[i])
			self._servo[i].SetT(T)
			self._servo[i].SetPh(phase_diff[i])

		ref = float(time.ticks_ms())
		x = ref
		while x <= T * cycle + ref:
			for i in range(0, 4):
				self._servo[i].refresh()
			x = float(time.ticks_ms())

	def _execute(self, A, O, T, phase_diff, steps = 1.0):
		self.attachServos()
		if self.getRestState() == True:
			self.setRestState(False)

		#-- Execute complete cycles
		cycles = int(steps)
		if cycles >= 1:
			i = 0
			while i < cycles:
				self.oscillateServos(A, O, T, phase_diff)
				i += 1
		#-- Execute the final not complete cycle
		self.oscillateServos(A, O, T, phase_diff, float(steps - cycles))

	#-- HOME = Otto at rest position
	def home(self):
		if self.getRestState() == False:	#-- Go to rest position only if necessary
			homes = [90, 90, 90, 90]	#-- All the servos at rest position
			self._moveServos(500, homes)	#-- Move the servos in half a second
			self.detachServos()
			self.setRestState(True)

	def getRestState(self):
		return self._isOttoResting

	def setRestState(self, state):
		self._isOttoResting = state

	#-- PREDETERMINED MOTION SEQUENCES

	#-- Otto movement: Jump
	#--  Parameters:
	#--    steps: Number of steps
	#--    T: Period

	def jump(self, steps, T):
		up = [90, 90, 150, 30]
		self._moveServos(T, up)
		down = [90, 90, 90, 90]
		self._moveServos(T, down)

	#-- Otto gait: Walking  (forward or backward)
	#--  Parameters:
	#--    * steps:  Number of steps
	#--    * T : Period
	#--    * Dir: Direction: FORWARD / BACKWARD

	def walk(self, steps, T, dir):
		#-- Oscillator parameters for walking
		#-- Hip sevos are in phase
		#-- Feet servos are in phase
		#-- Hip and feet are 90 degrees out of phase
		#--      -90 : Walk forward
		#--       90 : Walk backward
		#-- Feet servos also have the same offset (for tiptoe a little bit)
		A = [30, 30, 20, 20]
		O = [0, 0, 4, -4]
		phase_diff = [0, 0, DEG2RAD(dir * -90), DEG2RAD(dir * -90)]

		#-- Let's oscillate the servos!
		self._execute(A, O, T, phase_diff, steps)

	#-- Otto gait: Turning (left or right)
	#--  Parameters:
	#--   * Steps: Number of steps
	#--   * T: Period
	#--   * Dir: Direction: LEFT / RIGHT

	def turn(self, steps, T, dir):
		#-- Same coordination than for walking (see Otto.walk)
		#-- The Amplitudes of the hip's oscillators are not igual
		#-- When the right hip servo amplitude is higher, steps taken by
		#-- the right leg are bigger than the left. So, robot describes an left arc
		A = [30, 30, 20, 20]
		O = [0, 0, 4, -4]
		phase_diff = [0, 0, DEG2RAD(-90), DEG2RAD(-90)] #-- FIXME DEG2RAD()
		if dir == LEFT:
			A[0] = 30	#-- Left hip servo
			A[1] = 10	#-- Right hip servo
		else:
			A[0] = 10
			A[1] = 30

		#-- Let's oscillate the servos!
		self._execute(A, O, T, phase_diff, steps); 

	#-- Otto gait: Lateral bend
	#--  Parameters:
	#--    steps: Number of bends
	#--    T: Period of one bend
	#--    dir: RIGHT=Right bend LEFT=Left bend
	
	def bend(self, steps, T, dir):
		#-- Parameters of all the movements. Default: Left bend
		bend1 = [90, 90, 40, 35]
		bend2 = [90, 90, 40, 105]
		homes = [90, 90, 90, 90]

		#-- Time of one bend, in order to avoid movements too fast.
		#T = max(T, 600)

		#-- Changes in the parameters if right direction is chosen 
		if dir == RIGHT:
			bend1[2] = 180 - 50
			bend1[3] = 180 - 80	#-- Not 65. Otto is unbalanced
			bend2[2] = 180 - 105
			bend2[3] = 180 - 60

		#-- Time of the bend movement. Fixed parameter to avoid falls
		T2 = 800

		#-- Bend movement
		i = 0
		while i < steps:
			self._moveServos(T2 / 2, bend1)
			self._moveServos(T2 / 2, bend2)
			time.sleep_ms(int((T * 0.8)))
			self._moveServos(500, homes)
			i += 1

	#-- Otto gait: Shake a leg
	#--  Parameters:
	#--    steps: Number of shakes
	#--    T: Period of one shake
	#--    dir: RIGHT=Right leg LEFT=Left leg
	def shakeLeg(self, steps, T, dir):
		#-- This variable change the amount of shakes
		numberLegMoves = 2

		#-- Parameters of all the movements. Default: Right leg
		shake_leg1 = [90, 90, 40, 35]
		shake_leg2 = [90, 90, 40, 120]
		shake_leg3 = [90, 90, 70, 60]
		homes = [90, 90, 90, 90]

		#-- Changes in the parameters if right leg is chosen
		if dir == RIGHT:
			shake_leg1[2] = 180 - 15
			shake_leg1[3] = 180 - 40
			shake_leg2[2] = 180 - 120
			shake_leg2[3] = 180 - 58
			shake_leg3[2] = 180 - 60
			shake_leg3[3] = 180 - 58

		#-- Time of the bend movement. Fixed parameter to avoid falls
		T2 = 1000

		#-- Time of one shake, in order to avoid movements too fast.            
		T = T - T2
		T = max(T, 200 * numberLegMoves)

		j = 0
		while j < steps:
			#-- Bend movement
			self._moveServos(T2 / 2, shake_leg1)
			self._moveServos(T2 / 2, shake_leg2)

			#-- Shake movement
			i = 0
			while i < numberLegMoves:
				self._moveServos(T / (2 * numberLegMoves), shake_leg3)
				self._moveServos(T / (2 * numberLegMoves), shake_leg2)
				self._moveServos(500, homes)	#-- Return to home position
				i += 1
			j += 1
		time.sleep_ms(T)

	#-- Otto movement: up & down
	#--  Parameters:
	#--    * steps: Number of jumps
	#--    * T: Period
	#--    * h: Jump height: SMALL / MEDIUM / BIG 
	#--              (or a number in degrees 0 - 90)
	def updown(self, steps, T, h):
		#-- Both feet are 180 degrees out of phase
		#-- Feet amplitude and offset are the same
		#-- Initial phase for the right foot is -90, that it starts
		#--   in one extreme position (not in the middle)
		A = [0, 0, h, h]
		O = [0, 0, h, -h]
		phase_diff = [0, 0, DEG2RAD(-90), DEG2RAD(90)]

		#-- Let's oscillate the servos!
		self._execute(A, O, T, phase_diff, steps)

	#-- Otto movement: swinging side to side
	#--  Parameters:
	#--     steps: Number of steps
	#--     T : Period
	#--     h : Amount of swing (from 0 to 50 aprox)
	def swing(self, steps, T, h):
		#-- Both feets are in phase. The offset is half the amplitude
		#-- It causes the robot to swing from side to side
		A = [0, 0, h, h]
		O = [0, 0, h / 2, -h / 2]
		phase_diff = [0, 0, DEG2RAD(0), DEG2RAD(0)]
  
		#-- Let's oscillate the servos!
		self._execute(A, O, T, phase_diff, steps)

	#-- Otto movement: swinging side to side without touching the floor with the heel
	#--  Parameters:
	#--     steps: Number of steps
	#--     T : Period
	#--     h : Amount of swing (from 0 to 50 aprox)
	def tiptoeSwing(self, steps, T, h):
		#-- Both feets are in phase. The offset is not half the amplitude in order to tiptoe
		#-- It causes the robot to swing from side to side
		A = [0, 0, h, h]
		O = [0, 0, h, -h]
		phase_diff = [0, 0, 0, 0]

		#-- Let's oscillate the servos!
		self._execute(A, O, T, phase_diff, steps)

	#-- Otto gait: Jitter 
	#--  Parameters:
	#--    steps: Number of jitters
	#--    T: Period of one jitter 
	#--    h: height (Values between 5 - 25)   
	def jitter(self, steps, T, h):
		#-- Both feet are 180 degrees out of phase
		#-- Feet amplitude and offset are the same
		#-- Initial phase for the right foot is -90, that it starts
		#--   in one extreme position (not in the middle)
		#-- h is constrained to avoid hit the feets
		h = min(25, h)
		A = [h, h, 0, 0]
		O = [0, 0, 0, 0]
		phase_diff = [DEG2RAD(-90), DEG2RAD(90), 0, 0]
  
		#-- Let's oscillate the servos!
		self._execute(A, O, T, phase_diff, steps)

	#-- Otto gait: Ascending & turn (Jitter while up&down)
	#--  Parameters:
	#--    steps: Number of bends
	#--    T: Period of one bend
	#--    h: height (Values between 5 - 15) 
	def ascendingTurn(self, steps, T, h):
		#-- Both feet and legs are 180 degrees out of phase
		#-- Initial phase for the right foot is -90, that it starts
		#--   in one extreme position (not in the middle)
		#-- h is constrained to avoid hit the feets
		h = min(13, h)
		A = [h, h, h, h]
		O = [0, 0, h + 4, -h + 4]
		phase_diff = [DEG2RAD(-90), DEG2RAD(90), DEG2RAD(-90), DEG2RAD(90)]

		#-- Let's oscillate the servos!
		self._execute(A, O, T, phase_diff, steps)

	#-- Otto gait: Moonwalker. Otto moves like Michael Jackson
	#--  Parameters:
	#--    Steps: Number of steps
	#--    T: Period
	#--    h: Height. Typical valures between 15 and 40
	#--    dir: Direction: LEFT / RIGHT
	def moonwalker(self, steps, T, h, dir):
		#-- This motion is similar to that of the caterpillar robots: A travelling
		#-- wave moving from one side to another
		#-- The two Otto's feet are equivalent to a minimal configuration. It is known
		#-- that 2 servos can move like a worm if they are 120 degrees out of phase
		#-- In the example of Otto, two feet are mirrored so that we have:
		#--    180 - 120 = 60 degrees. The actual phase difference given to the oscillators
		#--  is 60 degrees.
		#--  Both amplitudes are equal. The offset is half the amplitud plus a little bit of
		#-   offset so that the robot tiptoe lightly

		A = [0, 0, h, h]
		O = [0, 0, h / 2 + 2, -h / 2 - 2]
		phi = -dir * 90
		phase_diff = [0, 0, DEG2RAD(phi), DEG2RAD(-60 * dir + phi)]

		#-- Let's oscillate the servos!
		self._execute(A, O, T, phase_diff, steps); 

	#-- Otto gait: Crusaito. A mixture between moonwalker and walk
	#--   Parameters:
	#--     steps: Number of steps
	#--     T: Period
	#--     h: height (Values between 20 - 50)
	#--     dir:  Direction: LEFT / RIGHT
	def crusaito(self, steps, T, h, dir):
		A = [25, 25, h, h]
		O = [0, 0, h / 2 + 4, -h / 2 - 4]
		phase_diff = [90, 90, DEG2RAD(0), DEG2RAD(-60 * dir)]

		#-- Let's oscillate the servos!
		self._execute(A, O, T, phase_diff, steps); 

	#-- Otto gait: Flapping
	#--  Parameters:
	#--    steps: Number of steps
	#--    T: Period
	#--    h: height (Values between 10 - 30)
	#--    dir: direction: FOREWARD, BACKWARD
	def flapping(self, steps, T, h, dir):
		A = [12, 12, h, h]
		O = [0, 0, h - 10, -h + 10]
		phase_diff = [DEG2RAD(0), DEG2RAD(180), DEG2RAD(-90 * dir), DEG2RAD(90 * dir)]

		#-- Let's oscillate the servos!
		self._execute(A, O, T, phase_diff, steps)

	#-- Otto get US distance
	#-- returns distance in cm
	def getDistance(self):
		return self.us.distance_cm()

	#-- Otto play tone
	#-- Parameters:
	#--    freq: Frequency of tone
	#--    duration: time to play tone
	#--    silentDur: time to play silence
	def _tone(self, freq, duration, silentDur):
		if self.buzzer >= 0:
			if silentDur <= 0:
				silentDur = 1
			#-- use 50% duty cycle
			pwm = PWM(self.buzzerPin, int(round(freq)), 512)
			time.sleep_ms(duration)
			pwm.deinit()
			time.sleep_ms(silentDur)

	#-- Otto bend tone from one tone to another
	#-- Parameters:
	#--     initFreq: Starting frequency
	#--     finalFreq: Ending frequency
	#--     prop: proportion to modify by
	#--     noteDur: time to play note(s)
	#--     
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

	#-- Otto sing a song
	#-- Parameters:
	#--    songName: number of song
	def sing(self, songName):
		if songName == S_CONNECTION:
			self._tone(NOTE_E5, 50, 30)
			self._tone(NOTE_E6, 55, 25)
			self._tone(NOTE_A6, 60, 10)
		elif songName == S_DISCONNECTION:
			self._tone(NOTE_E5, 50, 30)
			self._tone(NOTE_A6, 55, 25)
			self._tone(NOTE_E6, 50, 10)
		elif songName == S_BUTTONPUSHED:
			self.bendTones(NOTE_E6, NOTE_G6, 1.03, 20, 2)
			time.sleep_ms(30)
			self.bendTones(NOTE_E6, NOTE_D7, 1.04, 10, 2)
		elif songName == S_MODE1:
			self.bendTones(NOTE_E6, NOTE_A6, 1.02, 30, 10)
		elif songName == S_MODE2:
			self.bendTones(NOTE_G6, NOTE_D7, 1.03, 30, 10)
		elif songName == S_MODE3:
			self._tone(NOTE_E6, 50, 100)
			self._tone(NOTE_G6, 50, 80)
			self._tone(NOTE_D7, 300, 0)
		elif songName == S_SURPRISE:
			self.bendTones(800, 2150, 1.02, 10, 1)
			self.bendTones(2149, 800, 1.03, 7, 1)
		elif songName == S_OHOOH:
			self.bendTones(880, 2000, 1.04, 8, 3)
			time.sleep_ms(200)
			i = 880
			while i < 2000:
				self._tone(NOTE_C6, 10, 10)
				i = i * 1.04
		elif songName == S_OHOOH2:
			self.bendTones(1880, 3000, 1.03, 8, 3)
			time.sleep_ms(200)
			i = 1880
			while i < 3000:
				self._tone(NOTE_C6, 10, 10)
				i = i * 1.03
		elif songName == S_CUDDLY:
			self.bendTones(700, 900, 1.03, 16, 4)
			self.bendTones(899, 650, 1.01, 18, 7)
		elif songName == S_SLEEPING:
			self.bendTones(100, 500, 1.04, 10, 10)
			time.sleep_ms(500)
			self.bendTones(400, 100, 1.04, 10, 1)
		elif songName == S_HAPPY:
			self.bendTones(1500, 2500, 1.05, 20, 8)
			self.bendTones(2499, 1500, 1.05, 25, 8)
		elif songName == S_SUPERHAPPY:
			self.bendTones(2000, 6000, 1.05, 8, 3)
			time.sleep_ms(50)
			self.bendTones(5999, 2000, 1.05, 13, 2)
		elif songName == S_HAPPYSHORT:
			self.bendTones(1500, 2000, 1.05, 15, 8)
			time.sleep_ms(100)
			self.bendTones(1900, 2500, 1.05, 10, 8)
		elif songName == S_SAD:
			self.bendTones(880, 669, 1.02, 20, 200)
		elif songName == S_CONFUSED:
			self.bendTones(1000, 1700, 1.03, 8, 2)
			self.bendTones(1699, 500, 1.04, 8, 3)
			self.bendTones(1000, 1700, 1.05, 9, 10)
		elif songName == S_FART1:
			self.bendTones(1600, 3000, 1.02, 2, 15)
		elif songName == S_FART2:
			self.bendTones(2000, 6000, 1.02, 2, 20)
		elif songName == S_FART3:
			self.bendTones(1600, 4000, 1.02, 2, 20)
			self.bendTones(4000, 3000, 1.02, 2, 20)

			
#end
