from flask import Flask, jsonify, request
import hashlib
import json
import requests
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.votes = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'votes': self.votes,
            'proof': proof,
            'previous_hash': previous_hash,
        }
        self.votes = []  # Clear votes after block creation
        self.chain.append(block)
        return block

    def add_vote(self, voter_id, candidate):
        self.votes.append({'voter_id': voter_id, 'candidate': candidate})
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 1
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, node_address):
        self.nodes.add(node_address)

    def resolve_conflicts(self):
        # Consensus algorithm to resolve conflicts
        longest_chain = None
        max_length = len(self.chain)

        for node in self.nodes:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length:
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True
        return False

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(proof, previous_hash)

    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'votes': block['votes'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/vote', methods=['POST'])
def vote():
    values = request.get_json()

    required = ['voter_id', 'candidate']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.add_vote(values['voter_id'], values['candidate'])
    response = {'message': f'Vote will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/register_node', methods=['POST'])
def register_node():
    values = request.get_json()
    node_address = values.get('node_address')

    if not node_address:
        return 'Invalid data', 400

    blockchain.register_node(node_address)
    return jsonify({'message': 'Node registered successfully.'}), 201

@app.route('/nodes', methods=['GET'])
def get_nodes():
    return jsonify({'nodes': list(blockchain.nodes)}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Listen on all interfaces
