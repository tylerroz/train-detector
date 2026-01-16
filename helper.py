import datetime, time

def get_log_timestamp():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

def log(input):
    print(f"[{get_log_timestamp()}] {input}")