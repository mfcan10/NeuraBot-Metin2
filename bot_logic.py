import cv2
import numpy as np
import mss
from ultralytics import YOLO
import time
import os
import random
import win32gui
import pydirectinput
import ctypes
import sys
import threading
from interception import Interception, MouseStroke, MouseButtonFlag, KeyStroke

# Import cinput for fallback (ensure it's in the same directory)
try:
    import cinput
except ImportError:
    pass

MOUSE_LEFT_BUTTON_DOWN = MouseButtonFlag.MOUSE_LEFT_BUTTON_DOWN
MOUSE_LEFT_BUTTON_UP = MouseButtonFlag.MOUSE_LEFT_BUTTON_UP

class MetinBot:
    def __init__(self, log_callback=None, status_callback=None, stats_callback=None):
        self.log_callback = log_callback
        self.status_callback = status_callback
        self.stats_callback = stats_callback
        self.running = False
        self.paused = False
        
        # Runtime Stats
        self.stones_destroyed = 0
        self.auto_loot_enabled = True
        
        # Paths
        if getattr(sys, 'frozen', False):
            self.app_path = sys._MEIPASS
        else:
            self.app_path = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(self.app_path, "models", "village1.pt")
        
        # State Config
        self.STATE_SEARCHING = 0
        self.STATE_WAITING = 1
        self.STATE_ATTACKING = 2
        self.STATE_EXPLORING = 3
        
        # Default Config
        self.WAIT_DURATION_AFTER_CLICK = 5.0
        self.ATTACK_TIMEOUT_NO_BAR = 2.0
        self.SEARCH_TIMEOUT = 5.0
        self.STUCK_TIMEOUT = 10.0
        
        # Runtime vars
        self.current_state = self.STATE_SEARCHING
        self.target_hwnd = None
        self.debug_mode = True
        self.monitor = None
        self.driver = None
        self.mouse_device = None
        self.keyboard_device = None
        self.model = None
        self.sct = None
        
        # Exploration State
        self.current_heading_keys = []
        self.heading_expiry = 0
        
    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def update_status(self, status):
        if self.status_callback:
            self.status_callback(status)

    def load_model(self):
        self.log("Loading model...")
        try:
            self.model = YOLO(self.model_path)
            self.log("Model loaded successfully.")
            return True
        except Exception as e:
            self.log(f"Error loading model: {e}")
            return False

    def init_driver(self):
        self.log("Initializing Systems...")
        try:
            self.driver = Interception()
            for i in range(1, 21):
                if self.mouse_device is None and self.driver.is_mouse(i):
                    self.mouse_device = i
                if self.keyboard_device is None and self.driver.is_keyboard(i):
                    self.keyboard_device = i
            
            if self.mouse_device:
                 self.log(f"Mouse Device: {self.mouse_device}")
            else:
                 self.log("WARNING: No Mouse Device found!")
                 
            if self.keyboard_device:
                 self.log(f"Keyboard Device: {self.keyboard_device}")
            else:
                 self.log("WARNING: No Keyboard Device found!")
                 
        except Exception as e:
            self.log(f"Systems Init Failed: {e}")

    def get_window_rect(self, hwnd):
        try:
            client_rect = win32gui.GetClientRect(hwnd)
            width = client_rect[2]
            height = client_rect[3]
            top_left_screen = win32gui.ClientToScreen(hwnd, (0, 0))
            return {"top": top_left_screen[1], "left": top_left_screen[0], "width": width, "height": height}
        except:
            return None

    def interception_click(self, screen_x, screen_y):
        try:
            win32gui.SetForegroundWindow(self.target_hwnd)
            time.sleep(np.random.uniform(0.08, 0.12))
            pydirectinput.moveTo(screen_x, screen_y)
            time.sleep(0.1)
            
            self.log(f"CLICK -> {screen_x}, {screen_y}")
            
            if self.driver and self.mouse_device:
                self.driver.send(self.mouse_device, MouseStroke(0, MOUSE_LEFT_BUTTON_DOWN, 0, 0, 0))
                time.sleep(np.random.uniform(0.1, 0.15))
                self.driver.send(self.mouse_device, MouseStroke(0, MOUSE_LEFT_BUTTON_UP, 0, 0, 0))
            else:
                pydirectinput.click() # Fallback
                
        except Exception as e:
            self.log(f"Click Error: {e}")

    def hit_z_key(self):
        # Scancode 0x2C is 'Z'
        if self.driver and self.keyboard_device:
            self.driver.send(self.keyboard_device, KeyStroke(0x2C, 0)) # Down (State 0)
            time.sleep(np.random.uniform(0.04, 0.09))
            self.driver.send(self.keyboard_device, KeyStroke(0x2C, 1)) # Up (State 1)
        else:
            pydirectinput.press('z')

    def perform_loot(self):
        if not self.auto_loot_enabled: return
        
        self.log("Looting...")
        for _ in range(4):
            self.hit_z_key()
            time.sleep(np.random.uniform(0.1, 0.2))

    def check_health_bar(self, frame):
        height, width = frame.shape[:2]
        roi_top, roi_bottom = 0, 60
        roi_left, roi_right = int(width * 0.30), int(width * 0.70)
        roi = frame[roi_top:roi_bottom, roi_left:roi_right]
        
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        
        mask = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))
        red_pixels = cv2.countNonZero(mask)
        
        return red_pixels > 5, red_pixels, (roi_left, roi_top, roi_right, roi_bottom)

    def check_screen_change(self, frame1, frame2):
        if frame1 is None or frame2 is None: return True
        g1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        g2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(g1, g2)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        non_zero = cv2.countNonZero(thresh)
        return (non_zero / (frame1.shape[0] * frame1.shape[1])) > 0.01

    def perform_smart_escape(self):
        self.log("STUCK! Escaping...")
        pydirectinput.keyDown('s'); time.sleep(1.5); pydirectinput.keyUp('s')
        
        turn = random.choice(['a', 'd'])
        pydirectinput.keyDown(turn); time.sleep(1.0); pydirectinput.keyUp(turn)
        
        pydirectinput.keyDown('w'); time.sleep(2.0); pydirectinput.keyUp('w')
        self.log("Escape complete.")

    def run(self, target_hwnd, debug_mode=True):
        self.target_hwnd = target_hwnd
        self.debug_mode = debug_mode
        self.running = True
        self.sct = mss.mss()
        
        if not self.model:
            if not self.load_model(): return
            
        if not self.driver:
            self.init_driver()
            
        self.log("Starting in 3...")
        time.sleep(1)
        self.log("Starting in 2...")
        time.sleep(1)
        self.log("Starting in 1...")
        time.sleep(1)
            
        self.log("Bot Started.")
        
        state_start_time = time.time()
        last_seen_stone_time = time.time()
        bar_missing_counter = 0
        last_hp_pixels = 0
        stagnation_start_time = None
        
        while self.running:
            if self.paused:
                time.sleep(0.5)
                continue
                
            if win32gui.IsIconic(self.target_hwnd):
                self.log("Window Minimized. Pausing...")
                time.sleep(1)
                continue
                
            monitor = self.get_window_rect(self.target_hwnd)
            if not monitor or monitor["width"] <= 0:
                self.log("Invalid Window. waiting...")
                time.sleep(1)
                continue
                
            try:
                # Capture
                scr = self.sct.grab(monitor)
                img = np.array(scr)
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Inference
                results = self.model(frame, verbose=False)
                
                # Visuals
                annotated_frame = frame.copy() if self.debug_mode else None
                
                # Logic Vars
                best_target = None
                max_conf = -1.0
                
                for result in results:
                    for box in result.boxes:
                        label = result.names[int(box.cls[0])]
                        if label.endswith('L'): continue
                        conf = float(box.conf[0])
                        if conf > max_conf:
                            max_conf = conf
                            best_target = (box, label)

                # --- STATE MACHINE ---
                if self.current_state == self.STATE_SEARCHING:
                    self.update_status("SEARCHING")
                    
                    if best_target:
                        last_seen_stone_time = time.time()
                        box, _ = best_target
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cx, cy = (x1+x2)//2, (y1+y2)//2
                        
                        abs_x = monitor["left"] + cx
                        abs_y = monitor["top"] + cy
                        
                        self.log(f"Target Found. Clicking...")
                        self.interception_click(abs_x, abs_y)
                        
                        self.current_state = self.STATE_WAITING
                        state_start_time = time.time()
                    
                    else:
                        if time.time() - last_seen_stone_time > self.SEARCH_TIMEOUT:
                             self.log("No stones. Exploring...")
                             self.current_state = self.STATE_EXPLORING
                             state_start_time = time.time()
                             
                elif self.current_state == self.STATE_WAITING:
                    self.update_status("WAITING FOR BAR")
                    elapsed = time.time() - state_start_time
                    has_bar, hp, roi = self.check_health_bar(frame)
                    
                    if has_bar:
                        # self.log("Health Bar Detected. Attacking.") # Removed verbose log
                        self.current_state = self.STATE_ATTACKING
                        state_start_time = time.time()
                        bar_missing_counter = 0
                        last_hp_pixels = hp
                        stagnation_start_time = None
                    elif elapsed > self.WAIT_DURATION_AFTER_CLICK:
                        self.log("Wait Timeout. Retrying search.")
                        self.current_state = self.STATE_SEARCHING
                        
                    if self.debug_mode:
                        rx1, ry1, rx2, ry2 = roi
                        cv2.rectangle(annotated_frame, (rx1, ry1), (rx2, ry2), (0, 255, 255), 2)

                elif self.current_state == self.STATE_ATTACKING:
                    has_bar, hp, roi = self.check_health_bar(frame)
                    self.update_status(f"ATTACKING") # Removed HP info
                    
                    if has_bar:
                        bar_missing_counter = 0
                        # Stagnation
                        if hp < (last_hp_pixels - 5):
                            last_hp_pixels = hp
                            stagnation_start_time = None
                        elif hp >= (last_hp_pixels - 5):
                            if stagnation_start_time is None: stagnation_start_time = time.time()
                            if (time.time() - stagnation_start_time) > self.STUCK_TIMEOUT:
                                self.log("Stuck detected. Escaping.") # Shortened
                                self.perform_smart_escape()
                                self.current_state = self.STATE_SEARCHING
                                stagnation_start_time = None
                                
                        if self.debug_mode:
                             rx1, ry1, rx2, ry2 = roi
                             cv2.rectangle(annotated_frame, (rx1, ry1), (rx2, ry2), (0, 255, 0), 2)
                    else:
                        bar_missing_counter += 1
                        if bar_missing_counter > 60:
                            self.log("Target Destroyed.")
                            self.stones_destroyed += 1
                            if self.stats_callback:
                                self.stats_callback(self.stones_destroyed)
                                
                            self.perform_loot()
                            self.current_state = self.STATE_SEARCHING
                            last_seen_stone_time = time.time()

                elif self.current_state == self.STATE_EXPLORING:
                    self.update_status("EXPLORING")
                    
                    if best_target:
                        self.current_state = self.STATE_SEARCHING
                        pydirectinput.keyUp('w'); pydirectinput.keyUp('a'); pydirectinput.keyUp('d')
                        continue
                        
                    # Momentum Logic
                    if time.time() > self.heading_expiry:
                        options = [['w'], ['w'], ['w'], ['w', 'a'], ['w', 'd']]
                        self.current_heading_keys = random.choice(options)
                        self.heading_expiry = time.time() + random.randint(10, 20)
                        self.log(f"New Path: {self.current_heading_keys}")
                        
                    # Execution
                    frame_start = frame.copy()
                    
                    for k in self.current_heading_keys: pydirectinput.keyDown(k)
                    time.sleep(2.0)
                    for k in self.current_heading_keys: pydirectinput.keyUp(k)
                    
                    # Visual Check
                    scr_check = self.sct.grab(monitor)
                    frame_end = cv2.cvtColor(np.array(scr_check), cv2.COLOR_BGRA2BGR)
                    
                    if not self.check_screen_change(frame_start, frame_end):
                        self.log("Explore Stuck. Escaping.")
                        self.perform_smart_escape()
                        self.heading_expiry = 0
                        self.current_state = self.STATE_SEARCHING
                        last_seen_stone_time = time.time()
                    else:
                        self.current_state = self.STATE_SEARCHING
                        last_seen_stone_time = time.time()

                if self.debug_mode and annotated_frame is not None:
                     cv2.imshow("Bot View", annotated_frame)
                     if cv2.waitKey(1) & 0xFF == ord('q'):
                         self.running = False
                         
            except Exception as e:
                self.log(f"Loop Error: {e}")
                time.sleep(1)

        self.log("Bot Stopped.")
        cv2.destroyAllWindows()

    def stop(self):
        self.running = False
