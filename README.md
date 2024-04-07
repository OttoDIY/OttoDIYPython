# OttoDIY Robot micropython Libraries - Development Branch

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![version](https://img.shields.io/badge/version-0.1.0-blue)

This branch of the repository has the development [OttoDIY robot](https://www.ottodiy.com/) micropython libraries for [all Arduinos and compatible boards](#compatible-hardwareboards) .

This project is begining a new life as of 3/31/2024 - this branch 'devel' could be currently broken ... do not use it!

:star: Star us on GitHub, it helps!

## Installation - Development Branch:

1) Install Micropython onto your microcontroller
2) Upload these files on to the board ... Use uPyCraft, ampy, etc.
3) run the Otto_allmoves.py file from the REPL with the following command

`>>> exec(open('./examples/Otto_allmoves.py').read(),globals())`

### Example Code
```
#-- Otto All moves python test 
#-- OttDIY Python Project, 2024

import otto, time

Otto = otto.Otto()
Otto.init(D3, D4, D7, D8, True, D5)
Otto.home()

Otto.walk(2, 1000, FORWARD)         #-- 2 steps, "TIME". IF HIGHER THE VALUE THEN SLOWER (from 600 to 1400), 1 FORWARD
Otto.walk(2, 1000, BACKWARD)        #-- 2 steps, T, -1 BACKWARD 
Otto.turn(2, 1000, LEFT)            #-- 3 steps turning LEFT
Otto.home()
time.sleep_ms(100)  
Otto.turn(2, 1000, RIGHT)           #-- 3 steps turning RIGHT 
Otto.bend(1, 500, LEFT)             #-- usually steps =1, T=2000
Otto.bend(1, 2000, RIGHT)     
Otto.shakeLeg(1, 1500, LEFT)
Otto.home()
time.sleep_ms(100)
Otto.shakeLeg(1, 2000, RIGHT)
Otto.moonwalker(3, 1000, 25, LEFT)  #-- LEFT
Otto.moonwalker(3, 1000, 25, RIGHT) #-- RIGHT  
Otto.crusaito(2, 1000, 20, LEFT)
Otto.crusaito(2, 1000, 20, RIGHT)
time.sleep_ms(100)
Otto.flapping(2, 1000, 20, LEFT)
Otto.flapping(2, 1000, 20, RIGHT)
time.sleep_ms(100)
Otto.swing(2, 1000, 20)
Otto.tiptoeSwing(2, 1000, 20)
Otto.jitter(2, 1000, 20)            #-- (small T)
Otto.updown(2, 1500, 20)            #-- 20 = H "HEIGHT of movement"T 
Otto.ascendingTurn(2, 1000, 50)
Otto.jump(1, 2000)

Otto.home()

#end
```



