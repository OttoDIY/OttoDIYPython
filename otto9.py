"""
OttoDIY Python Project, 2020 | sfranzyshen
"""

import oscillator, time, math

#-- Constants
FORWARD = 1
BACKWARD = -1
LEFT = 1
RIGHT = -1
SMALL = 5
MEDIUM = 15
BIG = 30

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


#end
