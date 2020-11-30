import time
import hashlib
peer_name = 'hello'+str(time.time())
CONFIG = {
    'peer_id': hashlib.sha1(peer_name.encode('utf-8')).digest(),
    'block_length': 2**14,
    'max_peers': 8,
}