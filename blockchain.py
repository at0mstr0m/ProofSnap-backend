import json
import time
from typing import List, Union

from block import Block
from crypto_helper import verify_signature


def validate(chain: List[Block]) -> bool:
    for i in range(1, len(chain)):
        current_block = chain[i]
        previous_block = chain[i - 1]
        if not (current_block.previous_signature == previous_block.signature
                and verify_signature(str(current_block), current_block.public_key, current_block.signature)
                and previous_block.nr == current_block.nr - 1
                and previous_block.timestamp < current_block.timestamp):
            print(f'Problem bei Block {str(i)} Blockchain invalide.')
            return False
    print('Blockchain valide!')
    return True


def init_empty_blockchain(private_key: str, public_key: str) -> List[Block]:
    genesis_block = Block(nr=0,
                          # the public key as data in the fist block
                          data={'public_key':
                                    '01751f348d0a392d89fc45d98a61077aa2d20be706f08ef97b2ecab34f09a276198c20aa4851b87830562e3e6e63bfa281705a92ff8f09bc964f8db0468c96f7710c01c8b964533f72b10c75be13dcff9dbd16275ab83fc83e3b7205ff44f19d53eb1647c7ece05f3b108a839ae43b35b77d8521981e5cde3da5c3fc08fd5b3a9b4fb410',
                                'curve': 'NIST521p'},
                          public_key=public_key,
                          # the numbers from LOST
                          previous_signature='4 8 15 16 23 42',
                          timestamp=time.time())
    genesis_block.sign(private_key)
    return [genesis_block]


class Blockchain:
    def __init__(self,
                 private_key: str,
                 public_key: str,
                 save_file_path: str = 'blockchain.json'):
        self._chain = []
        self.save_file_path = save_file_path
        self.private_key = private_key
        self.public_key = public_key
        try:
            self._chain = self._init_chain_from_json()
        except FileNotFoundError:
            self._chain = init_empty_blockchain(self.private_key, self.public_key)
            self.save_to_json()

    def _init_chain_from_json(self) -> list[Block]:
        temp_chain = [Block(nr=block_data['nr'],
                            data=block_data['data'],
                            public_key=self.public_key,
                            previous_signature=block_data['previous_signature'],
                            timestamp=block_data['timestamp'],
                            signature=block_data['signature'])
                      for block_data in self.get_chain_from_json()]
        if validate(temp_chain):
            return temp_chain
        return init_empty_blockchain(self.private_key, self.public_key)

    def save_to_json(self):
        if validate(self._chain):  # only save a valid blockchain
            with open(self.save_file_path,
                      mode='w',
                      encoding='utf-8') as file:
                data = [block.to_dict() for block in self._chain]
                json.dump(data,
                          file,
                          ensure_ascii=False,
                          indent=4)

    def get_chain_from_json(self) -> List[dict]:
        """
        loads chain saved in json file
        :return: chain as list of Dictionaries with Blocks' attributes
        """
        return json.load(open(self.save_file_path, encoding='utf-8'))

    #     def check_block_integrity(self, block: Block) -> bool:
    #         """
    #         checks hash, previous hash, difficulty, block nr and timestamp of block
    #         :param      block: Block
    #         :return:    True if block is valid
    #         """
    #         previous_block = self._chain[block.nr - 1]
    #         return (str(block) == block_hash
    #                 and block.previous_hash == str(previous_block)
    #                 and int(block_hash, 16) < 2 ** (256 - self.difficulty)
    #                 and previous_block.nr == block.nr - 1
    #                 and previous_block.timestamp < block.timestamp)

    def store_data(self, data: dict, timestamp: float):
        new_block = Block(nr=len(self._chain),
                          data=data,
                          public_key=self.public_key,
                          previous_signature=self._chain[-1].signature,
                          timestamp=timestamp)
        new_block.sign(private_key=self.private_key)
        self._chain.append(new_block)
        self.save_to_json()

    def contains(self, image_data: str, signature: str, timestamp: str) -> bool:
        for block in self._chain[1:]:  # omit genesis block
            if (block.data['image_data'] == image_data
                    and block.data['signature'] == signature
                    and block.timestamp == timestamp):
                return True
        return False
