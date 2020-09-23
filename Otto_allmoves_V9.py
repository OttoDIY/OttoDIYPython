#-- Otto All moves python test 
#-- OttDIY Python Project, 2020

import otto9, time

Otto = otto9.Otto9()
Otto.init(5, 12, 13, 14, True, 0, 1, 2, 3)
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
