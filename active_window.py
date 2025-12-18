import pywinctl as pwc

try:
    active_title = pwc.getActiveWindowTitle()
    if active_title:
        print(f"The active window title is: {active_title}")
    else:
        print("No active window found or permission denied.")
except Exception as e:
    print(f"An error occurred: {e}")
