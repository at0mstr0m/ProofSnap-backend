import time
from hashlib import sha256


class Block:
    def __init__(self,
                 nr: int,
                 data: dict,
                 previous_hash: str,
                 trials: int = 0,
                 time_stamp: float = 0.0):
        self.nr = nr
        self.data = dict(sorted(data.items()))
        # Why the hell would you sort a dictionary?
        # Because since Python 3.8 dicts are keeping their order. To assure that str(self.data) always produces the same
        # string self.data is ordered. This avoids errors when loading the blockchain from .json
        self.previous_hash = previous_hash
        self.trials = trials
        self.hash = sha256()
        if time_stamp == 0.0:
            self.time_stamp = time.time()
        else:
            self.time_stamp = time_stamp

    def __str__(self):
        return sha256(f'{str(self.nr)}{str(self.time_stamp)}{str(self.data)}{str(self.trials)}{str(self.previous_hash)}'
                      .encode('utf-8')).hexdigest()

    def to_dict(self) -> dict:
        return {'nr': self.nr,
                'time_stamp': self.time_stamp,
                'data': self.data,
                'hash': str(self),
                'trials': self.trials,
                'previous_hash': self.previous_hash}

    def mine(self, difficulty: int):
        self.hash.update(str(self).encode('utf-8'))
        while int(self.hash.hexdigest(), 16) > 2 ** (256 - difficulty):
            self.trials += 1
            self.hash = sha256()
            self.hash.update(str(self).encode('utf-8'))
