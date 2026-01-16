from pushover import Client as PushoverClient

def notify_train_arrived():
    PushoverClient().send_message("A wild train has appeared.", title="Train has arrived!")
    
def notify_train_gone():
    PushoverClient().send_message("Train has left the station.", title="Train is gone!")