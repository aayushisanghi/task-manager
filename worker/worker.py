import time

def save_to_file(msg, delayTime):
    time.sleep(delayTime)
    return f"Processed message {msg} after {delayTime} seconds"