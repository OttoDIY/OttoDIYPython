"""
OttDIY Python Project, 2020 
"""
import oscillator, time

class Otto9:
	def __init__(self):
		self._servo = [oscillator.Oscillator(), oscillator.Oscillator(), oscillator.Oscillator(), oscillator.Oscillator()]
		self._servo_pins = [0,0,0,0]
		self._servo_trim = [0,0,0,0]
		self._servo_position = [90,90,90,90] # initialise to what the oscillator code defaults to 
		self._final_time = 0
		self._partial_time = 0
		self._increment = [0,0,0,0]
		self._isOttoResting = True

	def init(self, YL, YR, RL, RR, load_calibration = False, NoiseSensor, Buzzer, USTrigger, USEcho):  
		self._servo_pins[0] = YL
		self._servo_pins[1] = YR
		self._servo_pins[2] = RL
		self._servo_pins[3] = RR
		self.attachServos()
		self._isOttoResting = False
		if load_calibration == True:
			for i in range(0, 5):
				servo_trim = EEPROM.read(i) # FIXME ... add some sort of eeprom emulation
				if servo_trim > 128:
					servo_trim -= 256
				self._servo[i].SetTrim(servo_trim)
		for i in range(0, 5):			# this could be eliminated as we already initialize 
			self._servo_position[i] = 90	# the array from __init__() above ...

	#-- ATTACH & DETACH FUNCTIONS 
	def attachServos(self):
		for i in range(0, 5):
			self._servo[i].attach(self._servo_pins[i])

	def detachServos(self):	
		for i in range(0, 5):
			self._servo[i].detach()

	#-- OSCILLATORS TRIMS
	def setTrims(self, YL, YR, RL, RR):
		self._servo[0].SetTrim(YL)
		self._servo[1].SetTrim(YR)
		self._servo[2].SetTrim(RL)
		self._servo[3].SetTrim(RR)

	def saveTrimsOnEEPROM(self):
		for i in range(0, 5):
			EEPROM.write(i, self._servo[i].getTrim()) # FIXME  ... add some sort of eeprom emulation

#-- BASIC MOTION FUNCTIONS -------------------------------------#
def _moveServos(self, time, servo_target):
	self.attachServos()
	if self.getRestState() == True:
		self.setRestState(False)
	if time > 10:
		for i in range(0, 5): 
			self._increment[i] = ((servo_target[i]) - self._servo_position[i]) / (time / 10.0)
		self._final_time = time.ticks_ms() + time
		iteration = 1
		while time.ticks_ms() < self._final_time:
			self._partial_time = time.ticks_ms() + 10
			for i in range(0, 5): 
				self._servo[i].SetPosition(self._servo_position[i] + (iteration * self._increment[i]))
			while time.ticks_ms() < self._partial_time: 
 				pass # pause
			iteration += 1
	else:
		for i in range(0, 5):
			self._servo[i].SetPosition(servo_target[i])
	for i in range(0, 5): 
        	self._servo_position[i] = servo_target[i]


def _moveSingle(self, position, servo_number):

if (position > 180) position = 90
if (position < 0) position = 90
  attachServos()
  if getRestState()==True:        setRestState(False)

servoNumber = servo_number
if servoNumber == 0:  servo[0].SetPosition(position)

if servoNumber == 1:  servo[1].SetPosition(position)

if servoNumber == 2:  servo[2].SetPosition(position)

if servoNumber == 3:  servo[3].SetPosition(position)



def oscillateServos(self, A[4], O[4], T, phase_diff[4], cycle=1):
  for (int i=0; i<4; i++)    servo[i].SetO(O[i])
    servo[i].SetA(A[i])
    servo[i].SetT(T)
    servo[i].SetPh(phase_diff[i])

  double ref=millis()
   for (double x=ref; x<=T*cycle+ref; x=millis())     for (int i=0; i<4; i++)        servo[i].refresh()





def _execute(self, A[4], O[4], T, phase_diff[4], steps = 1.0):
  attachServos()
  if getRestState()==True:        setRestState(False)



  int cycles=(int)steps;    

  #-- Execute complete cycles
  if (cycles >= 1) 
    for(i = 0; i < cycles; i++) 
      oscillateServos(A,O, T, phase_diff)
      
  #-- Execute the final not complete cycle    
  oscillateServos(A,O, T, phase_diff,(float)steps-cycles)
