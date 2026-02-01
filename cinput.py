import ctypes
import time
from ctypes import wintypes
import win32api

# C Struct Definitions
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]
class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]
class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]
class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]
class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Constants
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_VIRTUALDESK = 0x4000

def _send_input(input_structure):
    ctypes.windll.user32.SendInput(1, ctypes.pointer(input_structure), ctypes.sizeof(input_structure))

def click(x=None, y=None):
    # If coordinates are provided, move there first
    if x is not None and y is not None:
        move_to(x, y)
    
    # Left Down
    extra = ctypes.c_ulong(0)
    ii_down = Input_I()
    ii_down.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
    x_down = Input(INPUT_MOUSE, ii_down)
    _send_input(x_down)
    
    time.sleep(0.05 + (time.time() % 0.1)) # Random tiny hold
    
    # Left Up
    ii_up = Input_I()
    ii_up.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(extra))
    x_up = Input(INPUT_MOUSE, ii_up)
    _send_input(x_up)

def left_down():
    extra = ctypes.c_ulong(0)
    ii_down = Input_I()
    ii_down.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
    x_down = Input(INPUT_MOUSE, ii_down)
    _send_input(x_down)

def left_up():
    extra = ctypes.c_ulong(0)
    ii_up = Input_I()
    ii_up.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(extra))
    x_up = Input(INPUT_MOUSE, ii_up)
    _send_input(x_up)

def move_to(x, y):
    # Convert pixels to 65535 normalized coordinates (required by MOUSEEVENTF_ABSOLUTE)
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    
    norm_x = int(x * 65535 / screen_width)
    norm_y = int(y * 65535 / screen_height)
    
    extra = ctypes.c_ulong(0)
    ii_move = Input_I()
    ii_move.mi = MouseInput(norm_x, norm_y, 0, MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK, 0, ctypes.pointer(extra))
    x_move = Input(INPUT_MOUSE, ii_move)
    _send_input(x_move)
    time.sleep(0.05)
