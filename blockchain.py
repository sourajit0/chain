import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_votes = []
        self.nodes = set()
        self.create_block(previous_hash='1', proof=100)  # Genesis block

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'votes': self.current_votes,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.current_votes = []  # Reset the votes after adding to the block
        self.chain.append(block)
        return block

    def add_vote(self, voter_id, candidate):
        vote = {
            'voter_id': voter_id,
            'candidate': candidate
        }
        self.current_votes.append(vote)
        return self.last_block['index'] + 1

    def hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    def valid_proof(self, last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def add_node(self, address):
        self.nodes.add(address)

    def is_chain_valid(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            last_block = block
            current_index += 1

        return True
