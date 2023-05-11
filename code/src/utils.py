import time

GROUP = 'iluzio.nicco.io'
VERSION = 'v1'


def timestamp_ms() -> int:
    return int(time.time() * 1000)
