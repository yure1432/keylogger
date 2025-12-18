import pyautogui
import time

pyautogui.FAILSAFE = False
with open("mouse_log.txt", "a") as f:
    try:
        while True:
            x, y = pyautogui.position()
            f.write(f"{x},{y}\n")
            f.flush()
            time.sleep(0.1)  # 10 samples/sec
    except KeyboardInterrupt:
        pass
