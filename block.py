import time

from crypto_helper import generate_signature


class Block:
    def __init__(self,
                 nr: int,
                 data: dict,
                 public_key: str,
                 previous_signature: str,
                 time_stamp: float = time.time(),
                 signature: str = None):
        self.nr = nr
        self.data = dict(sorted(data.items()))
        # ----------------------------
        # Why the hell would you sort a dictionary in Python?
        # Because since Python 3.8 dicts are keeping their order. To assure that str(self.data) always produces the same
        # string self.data is ordered. This avoids errors when loading the blockchain from .json
        # ----------------------------
        # the corresponding public_key to the private_key this block was signed with
        self.public_key = public_key
        self.previous_signature = previous_signature
        # if time_stamp == 0.0:
        #     self.time_stamp = time.time()
        # else:
        #     self.time_stamp = time_stamp
        self.time_stamp = time_stamp
        self.signature = signature

    def to_dict(self) -> dict:
        return {'nr': self.nr,
                'time_stamp': self.time_stamp,
                'data': self.data,
                'public_key': self.public_key,
                'signature': self.signature,
                'previous_signature': self.previous_signature}

    def __str__(self):
        return str({'nr': self.nr,
                    'time_stamp': self.time_stamp,
                    'data': self.data,
                    'public_key': self.public_key,
                    'previous_signature': self.previous_signature})

    def sign(self, private_key: str):
        self.signature = generate_signature(f'{str(self)}', private_key)
