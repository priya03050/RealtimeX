import base64
import hashlib


MAGIC_WEBSOCKET_UUID_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

def generate_sec_websocket_accept(sec_websocket_key):
    combined = sec_websocket_key + MAGIC_WEBSOCKET_UUID_STRING
    hashed_combined_string = hashlib.sha1(combined.encode())
    encoded = base64.b64encode(hashed_combined_string.digest())
    return encoded