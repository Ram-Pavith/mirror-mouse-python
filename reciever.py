#!/usr/bin/env python3
# Key scan code reference: https://msdn.microsoft.com/en-us/ie/aa299374(v=vs.100)
# VK code reference: https://docs.microsoft.com/en-us/windows/desktop/inputdev/virtual-key-codes

# Packet breakdown, 64 bits or 8 bytes
# [bits] (type) description
# [0,15] (int16) xPos of mouse
# [16,31] (int16) yPos of mouse
# [32, 65] (uint32) key state where each bit holds the keystate, bit 65 is keyboard state

import socket
from ctypes import windll

BIND_ADDR = socket.gethostbyname(socket.gethostname())
BIND_PORT = 46331

KEYBOARD_TOGGLE = 0x4B # K
MOUSE_TOGGLE = 0x4D # M

# Max 31 keys
TARGET_KEYS = [(0x01, -1), # LMB
            (0x02, -1), # RMB
            (0x11, 29), # VK_CONTROL
            (0x51, 16), # Q
            (0x57, 17), # W
            (0x45, 18), # E
            (0x52, 19), # R
            (0x54, 20), # T
            (0x59, 21), # Y
            (0x31, 2),  # 1
            (0x32, 3),  # 2
            (0x33, 4),  # 3
            (0x34, 4)]  # 4

MIN_INT = -32767
TARGET_KEYS.reverse()
TARGET_KEYS = tuple(TARGET_KEYS)

def print_response(response):
    xPos = int.from_bytes(response[0:2], byteorder='little', signed=True)
    yPos = int.from_bytes(response[2:4], byteorder='little', signed=True)
    keyStatesInt = int.from_bytes(response[4:8], byteorder='little')
    keyStatesStr = ""
    for i in range(32):
        keyStatesStr += str(keyStatesInt & 1)
        keyStatesInt >>= 1
    print(xPos, yPos, keyStatesStr)

# Create and bind socket to port
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((BIND_ADDR, BIND_PORT))
print('KMM successfully started at', s.getsockname(), '\nWaiting for first contact')
response, addr = s.recvfrom(16)
print('Data recieved from ', addr, ', sending reply') 
s.sendto(b'1', addr)

wapi = windll.user32
prevMkState = -1
oldKeyStates = [0] * len(TARGET_KEYS)

while True:
    response, addr = s.recvfrom(16)
    
    mouseMirroring = wapi.GetKeyState(MOUSE_TOGGLE) & 1
    keyboardMirroring = wapi.GetKeyState(KEYBOARD_TOGGLE) & 1

    mkState = mouseMirroring ^ keyboardMirroring
    if mkState != prevMkState:
        print('Keyboard', 'enabled' if keyboardMirroring else 'disabled',
              '\t\t\tMouse', 'enabled' if mouseMirroring else 'disabled')
    prevMkState = mkState
    
    xPos = int.from_bytes(response[0:2], byteorder='little', signed=True)
    mouseDataEnabled = xPos != MIN_INT and mouseMirroring

    keyStatesInt = int.from_bytes(response[4:8], byteorder='little')
    keyDataEnabled = keyStatesInt & 1 and keyboardMirroring

    if xPos == MIN_INT and not keyStatesInt & 1:
        print('Heartbeat recieved from ', addr, ', sending reply')
        s.sendto(b'1', addr)
        continue

    if mouseDataEnabled:
        yPos = int.from_bytes(response[2:4], byteorder='little', signed=True)
        wapi.SetCursorPos(xPos, yPos)
        
    keyStates = []
    for key in TARGET_KEYS:
        keyStatesInt >>= 1
        keyStates.append(keyStatesInt & 1)

    for i in range(len(keyStates)):
        # if action = 0, press key down, if action = 2, release key
        action = 1 + oldKeyStates[i] - keyStates[i]
        if action == 1: continue

        if TARGET_KEYS[i][0] == 0x01:
            if mouseDataEnabled:
                wapi.mouse_event(2 + action, xPos, yPos, 0, 0)
        elif TARGET_KEYS[i][0] == 0x02:
            if mouseDataEnabled:
                wapi.mouse_event(8 + action * 4, xPos, yPos, 0, 0)
        elif keyDataEnabled:
            wapi.keybd_event(TARGET_KEYS[i][0], TARGET_KEYS[i][1], action, 0)
            
    oldKeyStates = keyStates

s.close()
