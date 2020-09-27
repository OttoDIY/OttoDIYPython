# OttoDIYPython

This is a port of the OttoDIY Robot API ([Otto9.h](https://github.com/OttoDIY/OttoDIYLib/blob/master/Otto9.h)) to a [micropython based esp platform](https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html)

This project has just begun ... it's not ready for use yet ... [please look at 
the issues](https://github.com/OttoDIY/OttoDIYPython/issues) to see if you can help make this a reality ...

we now have added the humanoid support 😄 ... [Read this issue post](https://github.com/OttoDIY/OttoDIYPython/issues/17) to see how it's used ...

The Motion Code has been ported ... and a test file has been created ... to test this out

1) Install Micropython onto your microcontroller (I used a esp8266 nodemcu board)
2) Upload these files on to the board ... Use uPyCraft or ampy
3) run the Otto_allmoves_V9.py file from the REPL with the following command

`>>> exec(open('./Otto_allmoves_V9.py').read(),globals())`

### Example Code
```
"""
Otto All moves python test 
OttDIY Python Project, 2020 | sfranzyshen
"""
import otto9, time

Otto = otto9.Otto9()
Otto.init(5, 12, 13, 14, True, 0, 1, 2, 3)
Otto.home()

Otto.walk(2, 1000, 1) #-- 2 steps, "TIME". IF HIGHER THE VALUE THEN SLOWER (from 600 to 1400), 1 FORWARD
Otto.walk(2, 1000, -1) #-- 2 steps, T, -1 BACKWARD 
Otto.turn(2, 1000, 1) #-- 3 steps turning LEFT
Otto.home()
time.sleep_ms(100)  
Otto.turn(2, 1000, -1) #-- 3 steps turning RIGHT 
Otto.bend(1, 500, 1) #-- usually steps =1, T=2000
Otto.bend(1, 2000, -1)     
Otto.shakeLeg(1, 1500, 1)
Otto.home()
```
