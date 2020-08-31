"""
OttDIY Python Project, 2020 
"""
import oscillator

class Otto9:
	def __init__(self):
		self._servo[4] = oscillator.Oscillator()
		self._servo_pins[4] =
		self._servo_trim[4] =
		self._servo_position[4] =
		self._final_time = 0
		self._partial_time = 0
		self._increment[4] =
		self._isOttoResting = True

	def init(self, YL, YR, RL, RR, load_calibration, NoiseSensor, Buzzer, USTrigger, USEcho):  
		self._servo_pins[0] = YL
		self._servo_pins[1] = YR
		self._servo_pins[2] = RL
		self._servo_pins[3] = RR

		self.attachServos()
		self._isOttoResting = False

		if (load_calibration)
			for (i = 0; i < 4; i++)
				servo_trim = EEPROM.read(i)
				if (servo_trim > 128) 
					servo_trim -= 256
				self._servo[i].SetTrim(servo_trim)
		for (i = 0; i < 4; i++)
			self._servo_position[i] = 90

	#-- ATTACH & DETACH FUNCTIONS 
	def attachServos(self):
		self._servo[0].attach(servo_pins[0])
		self._servo[1].attach(servo_pins[1])
		self._servo[2].attach(servo_pins[2])
		self._servo[3].attach(servo_pins[3])

	def detachServos(self):
		self._servo[0].detach()
		self._servo[1].detach()
		self._servo[2].detach()
		self._servo[3].detach()

	#-- OSCILLATORS TRIMS
	def setTrims(self, YL, YR, RL, RR):
		self._servo[0].SetTrim(YL)
		self._servo[1].SetTrim(YR)
		self._servo[2].SetTrim(RL)
		self._servo[3].SetTrim(RR)

	def saveTrimsOnEEPROM(self):  
		for (i = 0; i < 4; i++)
			EEPROM.write(i, self._servo[i].getTrim())


#-- BASIC MOTION FUNCTIONS -------------------------------------#
def _moveServos(self, time, servo_target[]):
  attachServos()
  if getRestState()==True:        setRestState(False)


  if time>10:    for (i = 0; i < 4; i++) increment[i] = ((servo_target[i]) - servo_position[i]) / (time / 10.0)
    final_time =  millis() + time

    for (iteration = 1; millis() < final_time; iteration++)      partial_time = millis() + 10
      for (i = 0; i < 4; i++) servo[i].SetPosition(servo_position[i] + (iteration * increment[i]))
      while (millis() < partial_time); #pause


  else:
    for (i = 0; i < 4; i++) servo[i].SetPosition(servo_target[i])

  for (i = 0; i < 4; i++) servo_position[i] = servo_target[i]


def _moveSingle(self, position, servo_number):if (position > 180) position = 90
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
