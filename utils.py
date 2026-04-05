import shortuuid
from models import get_url

def generate_short_id():
    while True:
        short_id = shortuuid.uuid()[:6]
        if not get_url(short_id):  # avoid collision
            return short_id