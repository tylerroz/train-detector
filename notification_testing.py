"""
This file is used to test notification sending functionality.

Currently uses Pushover service to send notifications. Instead of sending a POST request directly,
it uses the pushover-python library for simplicity.
Docs: https://pypi.org/project/python-pushover/
"""

def send_http_notification():
    import http.client, urllib
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": "token",
        "user": "user_key",
        "message": "hello world",
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    
def send_library_notification():
    """
    Instead of hardcoding the secrets, they're read from ~/.pushoverrc
    """
    from pushover import Client
    # client = Client("user_key", api_token="api_token")
    Client().send_message("TRAIN!", title="TRAIN")