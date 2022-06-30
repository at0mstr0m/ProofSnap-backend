from block import Block
import json
from typing import List, Optional, Union


class Blockchain:
    def __init__(self,
                 save_file_path: str = 'data.json'):
        self._chain = []
        self.pool = []
        self.save_file_path = save_file_path
        try:
            self._chain = self.init_blocks_from_dicts()
        except Exception:
            self._init_empty_blockchain()

    def _init_empty_blockchain(self) -> None:
        genesis_block = Block(nr=0,
                              data={'data_type': 'GENESIS'},
                              previous_hash='0' * 64)
        genesis_block.mine(self.difficulty)
        self._chain.append(genesis_block)

    def init_blocks_from_dicts(self) -> list[Block]:
        return [Block(nr=block['nr'],
                      data=block['data'],
                      previous_hash=block['previous_hash'],
                      trials=block['trials'],
                      time_stamp=block['time_stamp'])
                for block in json.load(open(self.save_file_path, encoding='utf-8'))]

