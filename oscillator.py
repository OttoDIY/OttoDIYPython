"""
MicroPython driver to Generate sinusoidal oscillations in the servos
Requires a Pulse width modulation (PWM) pin. On the ESP8266 the 
pins 0, 2, 4, 5, 12, 13, 14 and 15 all support PWM. 
The limitation is that they must all be at the same frequency, 
and the frequency must be between 1Hz and 1kHz.
Oscillator.pde: GPL license (c) Juan Gonzalez-Gomez (Obijuan), 2011
"""

import math, time, servo

#-- should be taken (i.e. the TS time has passed since
#-- the last sample was taken
def next_sample(self):	
  self._currentMillis = time.ticks_ms() #-- Read current time
  if self._currentMillis - self._previousMillis > self._TS:		
    self._previousMillis = self._currentMillis;   
    return True
  return False

Class Oscillator:
  def __init__(self, trim = 0):
    self._trim = trim
    
  #-- Attach an oscillator to a servo
  #-- Input: pin is the arduino pin were the servo is connected
  def attach(self, pin, rev):	#-- If the oscillator is detached, it.
  	if not self._servo.attached():		#-- Attach the servo and move it to the home position
  		self._servo.attach(pin)
  		self._servo.write(90)
  		#-- Initialization of oscilaltor parameters
  		self._TS = 30
  		self._T = 2000
  		self._N = self._T / self._TS
  		self._inc = 2 * math.pi / self._N
  		self._previousMillis = 0
  		#-- Default parameters
  		self._A = 45
  		self._phase = 0
  		self._phase0 = 0
  		self._O = 0
	  	self._stop = False
		  #-- Reverse mode
		  self._rev = rev

  #-- Detach an oscillator from his servo
  def detach(self):	#-- If the oscillator is attached, it.
	  if self._servo.attached():
		  self._servo.detach()

  #--  Set the oscillator Phase (radians)
  def SetA(self, int A):	self._A = A

  #-- Set the oscillator Phase (radians)
  def SetO(self, int O):	self._O = O

  #-- Set the oscillator Phase (radians)
  def SetPh(self, Ph):	self._phase0 = Ph

  #-- Set the oscillator period, ms
  def SetT(self, int T):	#-- Assign the period
	  self._T = T
	  #-- Recalculate the parameters
	  self._N = self._T / self._TS
	  self._inc = 2 * math.pi / self._N

  #-- Manual set of the position
  def SetPosition(self, position): self._servo.write(position + self._trim)

  #-- SetTrim
  def SetTrim(self, trim): self._trim = trim

  #-- getTrim
  def getTrim(self): return self._trim

  #-- Stop
  def Stop(self): self._stop = True

  #-- Play
  def Play(self): self._stop = False

  #-- Reset
  def Reset(self): self._phase = 0

  """
  This function should be periodically called
  in order to maintain the oscillations. It calculates
  if another sample should be taken and position the servo if so
  """
  def refresh(self):	#-- Only When TS milliseconds have passed, sample is obtained
	  if next_sample():		#-- If the oscillator is not stopped, the servo position
		  if not self._stop:			#-- Sample the sine function and set the servo pos
			  self._pos = round(self._A * math.sin(self._phase + self._phase0) + self._O)
			  if (self._rev) 
				  self._pos=-self._pos
			  self._servo.write(self._pos+90+self._trim)

		  #-- Increment the phase
		  #-- It is always increased, when the oscillator is stop
		  #-- so that the coordination is always kept
      self._phase = self._phase + self._inc
