import otto9
import mouths
from machine import RFCOMM
from machine import Timer
import utime


class ottoRemote(otto9.Otto9):
    def __init__(self, name = "Otto"):
        super().__init__()
        self.timer = Timer(0)
        self.pending = False
        self.moveList = []
        self.savedMove = None
        self.name = name
        self.rfComm = RFCOMM(device = self.name, server = "ESP32")
        self.rfComm.callback(RFCOMM.CBTYPE_PATTERN, self.rfRemoteCommand, pattern='\r')
        self.commandDebug = False
        self.printMove = False
        self.moveDebug = False

        self.ottoMoves = [
            super().home,
            (super().walk, 1, 1),
            (super().walk, 1, -1),
            (super().turn, 1, 1),
            (super().turn, 1, -1),
            (super().updown, 1, 0),
            (super().moonwalker, 1, 0, 1),
            (super().moonwalker, 1, 0, -1),
            (super().swing, 1, 0),
            (super().crusaito, 1, 0, 1),
            (super().crusaito, 1, 0, -1),
            (super().jump, 1),
            (super().flapping, 1, 0, 1),
            (super().flapping, 1, 0, -1),
            (super().tiptoeSwing, 1, 0),
            (super().bend, 1, 1),
            (super().bend, 1, -1),
            (super().shakeLeg, 1, 1),
            (super().shakeLeg, 1, -1),
            (super().jitter, 1, 0),
            (super().ascendingTurn, 1, 0),
            super().handsup,
            (super().handwave, 1, -2),
            (super().handwave, -1, -2)
        ]

    def deinit(self):
        # we need to deinit rfComm
        self.rfComm.deinit()
        super().deinit()

    def moveFunc(self, timer):
        self.pending = False
        move = None
        if len(self.moveList) > 0:
            # make otto move
            move = self.moveList.pop(0).split()
        elif self.savedMove is not None:
            move = self.savedMove

        self.savedMove = None

        if move[0] == 'M':
            self.sendAck()
            # 'M' is for move
            moveIndex = int(move[1])

            if len(move) > 2:
                moveTime = int(move[2])
            else:
                moveTime = 1000

            if len(move) > 3:
                moveSize = int(move[3])
            else:
                moveSize = 15

            if self.moveDebug:
                print("index = " + str(moveIndex) + " T = " + str(moveTime) + " moveSize = " + str(moveSize))

            if len(self.ottoMoves) > moveIndex:
                if moveIndex != 0:
                    self.savedMove = move

                # get the actual move
                actualMove = self.ottoMoves[moveIndex]

                if isinstance(actualMove, tuple):
                    # get the specific move
                    ottoMove = actualMove[0]
                    if len(actualMove) == 2:
                        self.movePrint(ottoMove.__name__ + "(" + str(actualMove[1]) + ", " + str(moveTime) + ")")
                        ottoMove(actualMove[1], moveTime)
                    elif len(actualMove) == 3:
                        if actualMove[2] == 0:
                            self.movePrint(ottoMove.__name__ + "(" + str(actualMove[1]) + ", " +
                                           str(moveTime) + ", " + str(moveSize) + ")")
                            ottoMove(actualMove[1], moveTime, moveSize)
                        elif actualMove[2] >= -1:
                            self.movePrint(ottoMove.__name__ + "(" + str(actualMove[1]) + ", " +
                                  str(moveTime) + ", " + str(actualMove[2]) + ")")
                            ottoMove(actualMove[1], moveTime, actualMove[2])
                        elif actualMove[2] < -1:
                            self.movePrint(ottoMove.__name__ + "(" + str(actualMove[1]) + ")")
                            ottoMove(actualMove[1])
                        else:
                            self.savedMove = None
                    elif len(actualMove) == 4:
                        self.movePrint(ottoMove.__name__ + "(" + str(actualMove[1]) + ", " + str(moveTime) +
                                       ", " + str(moveSize) + ", " + str(actualMove[3]) + ")")
                        ottoMove(actualMove[1], moveTime, moveSize, actualMove[3])
                    else:
                        self.savedMove = None
                else:
                    ottoMove = actualMove
                    self.movePrint(ottoMove.__name__ + "()")
                    ottoMove()

                self.sendFinalAck()
        elif move[0] == 'B':
            # 'B' is for request battery
            print("Otto request battery")
            batteryLevel = 0.0
            batteryLevel = super().getBatteryLevel()

            if self.rfComm .connected()[0] != 0:
                self.rfComm.write(0, "&&B " + str(batteryLevel) + "%%\r")
        elif move[0] == 'D':
            # 'D' is for request distance
            print("Otto request distance")
            distance = 400.0
            distance = super().getDistance()

            if self.rfComm .connected()[0] != 0:
                self.rfComm.write(0, "&&D " + str(distance) + "%%\r")
        elif move[0] == 'H':
            self.sendAck()
            # 'H' is for gesture
            gesture = int(move[1]) - 1
            self.movePrint("Otto gesture=" + str(gesture))
            super().playGesture(gesture)
            self.sendFinalAck()
        elif move[0] == 'I':
            # 'I' is for request program ID
            print("Otto request program ID")
            prgId = 0.9
            if self.rfComm .connected()[0] != 0:
                self.rfComm.write(0, "&&I " + str(prgId) + "%%\r")
        elif move[0] == 'K':
            self.sendAck()
            # 'K' is for sing
            song = int(move[1]) - 1
            self.movePrint("Otto sing=" + str(song))
            super().sing(song)
            self.sendFinalAck()
        elif move[0] == 'L':
            self.sendAck()
            # 'L' is for mouth
            mouth = int(move[1], 2)
            self.movePrint("Otto mouth=" + hex(mouth))
            super().putMouth(mouth, False)
            self.sendFinalAck()
        elif move[0] == 'N':
            # 'N' is for request noise
            print("Otto request noise")
            noise = 0
            noise = super().getNoise()

            if self.rfComm .connected()[0] != 0:
                self.rfComm.write(0, "&&N " + str(noise) + "%%\r")
        elif move[0] == 'T':
            self.sendAck()
            # 'T' is for buzzer

            if len(move) < 3:
                # this is an error
                super().putMouth(mouths.XMOUTH)
                utime.sleep_ms(2000)
                super().clearMouth()
            else:
                self.movePrint("Otto buzzer freq=" + move[1] + " time=" + move[2])
                super()._tone(int(move[1]), int(move[2]), 1)
            self.sendFinalAck()
        else:
            self.sendAck()
            super().home()
            self.sendFinalAck()

        # schedule again if the savedMove is valid
        if self.savedMove is not None:
            self.pending = True
            self.timer.init(period=100, mode=Timer.ONE_SHOT, callback = self.moveFunc)

    def addMove(self, moveStr):
        self.moveList.append(moveStr)
        if not self.pending:
            self.moveFunc(self.timer)

    def sendAck(self):
        utime.sleep_ms(30)
        if self.rfComm.connected()[0] != 0:
            self.rfComm.write(0, "&&A%%\r")

    def sendFinalAck(self):
        utime.sleep_ms(30)
        if self.rfComm.connected()[0] != 0:
            self.rfComm.write(0, "&&F%%\r")

    def rfRemoteCommand(self, ev):
        # we don't care which channel
        if self.commandDebug:
            print(ev[2].decode())
        command = ev[2].decode()
        self.addMove(command)

    def commandDbg(self, yesNo):
        self.commandDebug = yesNo

    def moveDbg(self, yesNo):
        self.moveDebug = yesNo

    def movePrt(self, yesNo):
        self.printMove = yesNo

    def movePrint(self, moveStr):
        if self.printMove:
            print(moveStr)

