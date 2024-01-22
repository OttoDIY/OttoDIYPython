import otto9
import mouths

import socket
import network
import websocket_helper
import uwebsocket
import ujson

try:
    from esp32 import RFCOMM
except ImportError:
    print("This version of micropython esp32 doesn't support RFCOMM")
    raise ImportError

from machine import Timer
import utime


class ottoRemote(otto9.Otto9):
    def __init__(self, name="Otto", prgId="Otto_V9", webPort=8181):
        super().__init__()
        self.timer = Timer(0)
        self.pending = False
        self.cmdList = []
        self.savedCmd = None
        self.name = name
        self.rfComm = RFCOMM(device=self.name, server="ESP32")
        self.rfComm.callback(RFCOMM.CBTYPE_PATTERN, self.rfRemoteCommand, pattern='\r')
        self.cmdDebug = False
        self.printCmd = False
        self.moveDebug = False
        self.prgId = prgId

        self.listenSock = None
        self.clientSock = None
        self.webSock = None
        self.webPort = webPort

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

        self.setupConn()

    def deinit(self):
        # we need to deinit rfComm
        self.rfComm.deinit()
        super().deinit()

    def cmdProc(self, _):
        self.pending = False

        if len(self.cmdList) > 0:
            # make otto move
            cmd = self.cmdList.pop(0)
        elif self.savedCmd is not None:
            cmd = self.savedCmd
        else:
            return

        # make sure command is in dict
        if 'command' in cmd:
            command = cmd['command']
        else:
            return

        self.savedCmd = None

        if command[0] == 'M':
            self.sendAck(cmd)
            # 'M' is for move
            moveIndex = int(command[1])

            if len(command) > 2:
                moveTime = int(command[2])
            else:
                moveTime = 1000

            if len(command) > 3:
                moveSize = int(command[3])
            else:
                moveSize = 15

            if self.moveDebug:
                print("index = " + str(moveIndex) + " T = " + str(moveTime) + " moveSize = " + str(moveSize))

            if len(self.ottoMoves) > moveIndex:
                # this should use the otto.getRestState()
                if moveIndex != 0:
                    self.savedCmd = cmd

                # get the actual move
                actualMove = self.ottoMoves[moveIndex]

                if isinstance(actualMove, tuple):
                    # get the specific move
                    ottoMove = actualMove[0]
                    if len(actualMove) == 2:
                        self.cmdPrint(ottoMove.__name__ + "(" + str(actualMove[1]) + ", " + str(moveTime) + ")")
                        ottoMove(actualMove[1], moveTime)
                    elif len(actualMove) == 3:
                        if actualMove[2] == 0:
                            self.cmdPrint(ottoMove.__name__ + "(" + str(actualMove[1]) + ", " +
                                          str(moveTime) + ", " + str(moveSize) + ")")
                            ottoMove(actualMove[1], moveTime, moveSize)
                        elif actualMove[2] >= -1:
                            self.cmdPrint(ottoMove.__name__ + "(" + str(actualMove[1]) + ", " +
                                          str(moveTime) + ", " + str(actualMove[2]) + ")")
                            ottoMove(actualMove[1], moveTime, actualMove[2])
                        elif actualMove[2] < -1:
                            self.cmdPrint(ottoMove.__name__ + "(" + str(actualMove[1]) + ")")
                            ottoMove(actualMove[1])
                        else:
                            self.savedCmd = None
                    elif len(actualMove) == 4:
                        self.cmdPrint(ottoMove.__name__ + "(" + str(actualMove[1]) + ", " + str(moveTime) +
                                      ", " + str(moveSize) + ", " + str(actualMove[3]) + ")")
                        ottoMove(actualMove[1], moveTime, moveSize, actualMove[3])
                    else:
                        self.savedCmd = None
                else:
                    ottoMove = actualMove
                    self.cmdPrint(ottoMove.__name__ + "()")
                    ottoMove()

                self.sendFinalAck(cmd)
        elif command[0] == 'B':
            # 'B' is for request battery
            self.cmdPrint("Otto request battery")
            batteryLevel = super().getBatteryLevel()

            self.sendResp(cmd, str(batteryLevel))
        elif command[0] == 'D':
            # 'D' is for request distance
            self.cmdPrint("Otto request distance")
            distance = super().getDistance()

            self.sendResp(cmd, str(distance))
        elif command[0] == 'H':
            self.sendAck(cmd)
            # 'H' is for gesture
            gesture = int(command[1]) - 1
            self.cmdPrint("Otto gesture=" + str(gesture))
            super().playGesture(gesture)
            self.sendFinalAck(cmd)
        elif command[0] == 'I':
            # 'I' is for request program ID
            print("Otto request program ID")
            self.sendResp(cmd, self.prgId)
        elif command[0] == 'K':
            self.sendAck(cmd)
            # 'K' is for sing
            song = int(command[1]) - 1
            self.cmdPrint("Otto sing=" + str(song))
            super().sing(song)
            self.sendFinalAck(cmd)
        elif command[0] == 'L':
            self.sendAck(cmd)
            # 'L' is for mouth
            mouth = int(command[1], 2)
            self.cmdPrint("Otto mouth=" + hex(mouth))
            super().putMouth(mouth, False)
            self.sendFinalAck(cmd)
        elif command[0] == 'N':
            # 'N' is for request noise
            print("Otto request noise")
            noise = super().getNoise()

            self.sendResp(cmd, str(noise))
        elif command[0] == 'T':
            self.sendAck(cmd)
            # 'T' is for buzzer

            if len(command) < 3:
                # this is an error
                super().putMouth(mouths.XMOUTH)
                utime.sleep_ms(2000)
                super().clearMouth()
            else:
                self.cmdPrint("Otto buzzer freq=" + command[1] + " time=" + command[2])
                super()._tone(int(command[1]), int(command[2]), 1)
            self.sendFinalAck(cmd)
        else:
            self.sendAck(cmd)
            super().home()
            self.sendFinalAck(cmd)

        # schedule again if the savedCmd is valid
        if self.savedCmd is not None:
            self.pending = True
            self.timer.init(period=100, mode=Timer.ONE_SHOT, callback=self.cmdProc)

    def addCmd(self, cmd):
        self.cmdList.append(cmd)
        if not self.pending:
            self.cmdProc(self.timer)

    def sendAck(self, cmd):
        utime.sleep_ms(30)
        if cmd['src'] == 'RFCOMM':
            if self.rfComm.connected()[cmd['ch']] != 0:
                self.rfComm.write(cmd['ch'], "&&A%%\r")
        elif cmd['src'] == 'WS':
            response = {
                'type': 'ottoAck',
                'command': cmd['command'][0]
            }

            cmd['sock'].write(ujson.dumps(response) + '\n')

    def sendFinalAck(self, cmd):
        utime.sleep_ms(30)
        if cmd['src'] == 'RFCOMM':
            if self.rfComm.connected()[cmd['ch']] != 0:
                self.rfComm.write(cmd['ch'], "&&F%%\r")
        elif cmd['src'] == 'WS':
            response = {
                'type': 'ottoFinalAck',
                'command': cmd['command'][0]
            }

            cmd['sock'].write(ujson.dumps(response) + '\n')

    def sendResp(self, cmd, result):
        if cmd['src'] == 'RFCOMM':
            if self.rfComm.connected()[cmd['ch']] != 0:
                self.rfComm.write(cmd['ch'], '&&' + cmd['command'][0] + ' ' + result + '%%\r')
        elif cmd['src'] == 'WS':
            response = {
                'type': 'ottoResponse',
                'command': cmd['command'][0],
                'result': result
            }

            cmd['sock'].write(ujson.dumps(response) + '\n')

    def rfRemoteCommand(self, ev):
        cmd = {
            'src': 'RFCOMM',
            'ch': ev[0],
            'command': ev[2].decode().split()
        }
        if self.cmdDebug:
            print(cmd)
        self.addCmd(cmd)

    def cmdDbg(self, yesNo):
        self.cmdDebug = yesNo

    def moveDbg(self, yesNo):
        self.moveDebug = yesNo

    def cmdPrt(self, yesNo):
        self.printCmd = yesNo

    def cmdPrint(self, cmdStr):
        if self.printCmd:
            print(cmdStr)

    def wsRemoteCommand(self, clientSock):
        if clientSock == self.clientSock:
            strg = self.webSock.readline()

            if len(strg) == 0:
                # the connection is gone
                self.webSock.close()
                self.clientSock.close()
                self.webSock = None
                self.clientSock = None
                return

            try:
                cmd = ujson.loads(strg)
                cmd['src'] = "WS"
                cmd['sock'] = self.webSock

                if self.cmdDebug:
                    print(cmd)
                self.addCmd(cmd)
            except:
                pass

    def acceptConn(self, listenSock):
        cl, remote_addr = self.listenSock.accept()
        print("\nOtto WS connection from:", remote_addr)

        if self.clientSock is not None:
            try:
                self.webSock.close()
                self.clientSock.close()
            except:
                pass
            self.webSock = None
            self.clientSock = None

        self.clientSock = cl
        websocket_helper.server_handshake(self.clientSock)
        self.webSock = uwebsocket.websocket(self.clientSock, True)
        self.clientSock.setblocking(False)
        self.clientSock.setsockopt(socket.SOL_SOCKET, 20, self.wsRemoteCommand)

    def setupConn(self):
        if self.listenSock is not None:
            self.listenSock.close()
            self.listenSock = None

        self.listenSock = socket.socket()
        self.listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ai = socket.getaddrinfo("0.0.0.0", self.webPort)
        addr = ai[0][4]

        self.listenSock.bind(addr)
        self.listenSock.listen(1)
        self.listenSock.setsockopt(socket.SOL_SOCKET, 20, self.acceptConn)
        for i in (network.AP_IF, network.STA_IF):
            iface = network.WLAN(i)
            if iface.active():
                print("Otto WS daemon started on ws://%s:%d" % (iface.ifconfig()[0], self.webPort))

