import socket, time, sys
from ctypes import windll, Structure, c_long, byref

RECV_ADDR = '99.231.254.55'
RECV_PORT = 46331
POLL_RATE = 58
X_RES = 1920
Y_RES = 1080

KEYBOARD_TOGGLE = 0x4B # K
MOUSE_TOGGLE = 0x4D # M

# Max 31 keys
POLL_KEYS = (0x01, # LMB
            0x02, # RMB
            0x11, # VK_CONTROL
            0x51, # Q
            0x57, # W
            0x45, # E
            0x52, # R
            0x44, # D
            0x46, # F
            0x31, # 1
            0x32, # 2
            0x33, # 3
            0x34) # 4

POLL_TIME = 1 / POLL_RATE
MIN_INT = -32767
MIN_INT_BYTES = MIN_INT.to_bytes(2, byteorder='little', signed=True)
NULL_BYTES = b'\x00\x00'
HEARTBEAT_TIME = 60
X_RES_RATIO = round(X_RES / 1920)
Y_RES_RATIO = round(Y_RES / 1080)

class POINT(Structure):
    _fields_ = [('x', c_long), ('y', c_long)]

addr = (RECV_ADDR, RECV_PORT)
pollTime = 1 / POLL_RATE

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', 0))
print('KMM transmitter successfully started, connecting to reciever...')
s.sendto(MIN_INT_BYTES + MIN_INT_BYTES + NULL_BYTES, addr)
res, resAddr = s.recvfrom(1)
print('Response recieved from reciever @' , resAddr)

mousePos = POINT()
wapi = windll.user32
prevMkState = -1

nextHeartbeat = 0
while True:
    time.sleep(POLL_TIME)
    currTime = time.time()
    
    mouseMirroring = wapi.GetKeyState(MOUSE_TOGGLE) & 1
    keyboardMirroring = wapi.GetKeyState(KEYBOARD_TOGGLE) & 1

    mkState = mouseMirroring ^ keyboardMirroring
    if mkState != prevMkState:
        print('Keyboard', 'enabled' if keyboardMirroring else 'disabled',
              '\t\t\tMouse', 'enabled' if mouseMirroring else 'disabled')
    prevMkState = mkState

    if not (mouseMirroring or keyboardMirroring):
        if (nextHeartbeat > currTime): continue
        else:
            nextHeartbeat = currTime + HEARTBEAT_TIME
            print('Sending heartbeat to reciever to keep connection alive')
    
    if not mouseMirroring:
        xPosBytes = MIN_INT_BYTES
        yPosBytes = MIN_INT_BYTES
    else:
        wapi.GetCursorPos(byref(mousePos))
        xPosBytes = (mousePos.x // X_RES_RATIO).to_bytes(2, byteorder='little', signed=True)
        yPosBytes = (mousePos.y // Y_RES_RATIO).to_bytes(2, byteorder='little', signed=True) 

    keyStatesInt = 0
    for key in POLL_KEYS:
        keyState = int(wapi.GetKeyState(key) not in (0, 1))
        keyStatesInt = (keyStatesInt + keyState) << 1
    keyStatesInt += int(keyboardMirroring)
    keyStatesBytes = keyStatesInt.to_bytes(4, byteorder='little')

    s.sendto(xPosBytes + yPosBytes + keyStatesBytes, addr)
s.close()
