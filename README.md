# OttoDIYPython

## This is a port of the OttoDIY Robot Arduino API Otto.h to a [micropython based esp platform](https://docs.micropython.org/en/latest/)

### This project is begining a new life. 3/31/2024
so this branch 'devel' is currently broken ... do not use

1) Install Micropython onto your microcontroller (I used a esp8266 nodemcu board)
2) Upload these files on to the board ... Use uPyCraft or ampy
3) run the Otto_allmoves_V9.py file from the REPL with the following command

`>>> exec(open('./Otto_allmoves_V9.py').read(),globals())`

### Example Code
```
"""
Otto All moves python test 
OttDIY Python Project, 2024 | sfranzyshen
"""
import otto9, time

Otto = otto.Otto()
Otto.init(D3, D4, D7, D8, True, D5)
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
