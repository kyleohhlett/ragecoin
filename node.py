import json
import requests
from typing import List, Dict, Set
from flask import Flask, jsonify, request
from blockchain import Blockchain
from transaction import Transaction
from block import Block


class Node:
    """P2P network node for the blockchain"""

    def __init__(self, port: int = 5000):
        self.app = Flask(__name__)
        self.port = port
        self.blockchain = Blockchain()
        self.peers: Set[str] = set()
        self.setup_routes()

    def setup_routes(self):
        """Setup Flask API routes"""

        @self.app.route('/chain', methods=['GET'])
        def get_chain():
            """Get the full blockchain"""
            return jsonify(self.blockchain.to_dict()), 200

        @self.app.route('/mine', methods=['POST'])
        def mine():
            """Mine pending transactions"""
            data = request.get_json()
            miner_address = data.get('miner_address')

            if not miner_address:
                return jsonify({'message': 'Miner address required'}), 400

            self.blockchain.mine_pending_transactions(miner_address)
            return jsonify({
                'message': 'Block mined successfully',
                'block': self.blockchain.get_latest_block().to_dict()
            }), 200

        @self.app.route('/transactions/new', methods=['POST'])
        def new_transaction():
            """Add a new transaction"""
            data = request.get_json()

            required = ['sender', 'recipient', 'amount', 'signature']
            if not all(k in data for k in required):
                return jsonify({'message': 'Missing transaction data'}), 400

            tx = Transaction(
                data['sender'],
                data['recipient'],
                data['amount'],
                data['signature']
            )

            if self.blockchain.add_transaction(tx):
                self.broadcast_transaction(tx)
                return jsonify({'message': 'Transaction added to pending pool'}), 201
            else:
                return jsonify({'message': 'Invalid transaction'}), 400

        @self.app.route('/balance/<address>', methods=['GET'])
        def get_balance(address):
            """Get balance of an address"""
            balance = self.blockchain.get_balance(address)
            return jsonify({'address': address, 'balance': balance}), 200

        @self.app.route('/validate', methods=['GET'])
        def validate_chain():
            """Validate the blockchain"""
            is_valid = self.blockchain.is_chain_valid()
            return jsonify({'valid': is_valid}), 200

        @self.app.route('/peers/register', methods=['POST'])
        def register_peer():
            """Register a new peer"""
            data = request.get_json()
            peer = data.get('peer')

            if peer:
                self.peers.add(peer)
                return jsonify({'message': f'Peer {peer} registered'}), 201
            return jsonify({'message': 'Invalid peer'}), 400

        @self.app.route('/peers', methods=['GET'])
        def get_peers():
            """Get all registered peers"""
            return jsonify({'peers': list(self.peers)}), 200

        @self.app.route('/consensus', methods=['GET'])
        def consensus():
            """Resolve conflicts using longest chain rule"""
            replaced = self.resolve_conflicts()
            if replaced:
                return jsonify({'message': 'Chain was replaced', 'chain': self.blockchain.to_dict()}), 200
            return jsonify({'message': 'Chain is authoritative', 'chain': self.blockchain.to_dict()}), 200

    def broadcast_transaction(self, transaction: Transaction) -> None:
        """Broadcast transaction to all peers"""
        for peer in self.peers:
            try:
                requests.post(f'{peer}/transactions/new', json=transaction.to_dict(), timeout=2)
            except requests.exceptions.RequestException:
                pass

    def resolve_conflicts(self) -> bool:
        """Consensus algorithm: replace chain with longest valid chain in network"""
        new_chain = None
        max_length = len(self.blockchain.chain)

        for peer in self.peers:
            try:
                response = requests.get(f'{peer}/chain', timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    length = len(data['chain'])
                    chain = [Block.from_dict(block) for block in data['chain']]

                    # Check if length is longer and chain is valid
                    if length > max_length:
                        temp_blockchain = Blockchain()
                        temp_blockchain.chain = chain
                        if temp_blockchain.is_chain_valid():
                            max_length = length
                            new_chain = chain
            except requests.exceptions.RequestException:
                continue

        if new_chain:
            self.blockchain.chain = new_chain
            return True

        return False

    def register_with_peer(self, peer_address: str) -> None:
        """Register this node with a peer"""
        try:
            response = requests.post(
                f'{peer_address}/peers/register',
                json={'peer': f'http://localhost:{self.port}'},
                timeout=2
            )
            if response.status_code == 201:
                self.peers.add(peer_address)
                print(f"Registered with peer: {peer_address}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to register with peer: {e}")

    def run(self, host: str = '0.0.0.0'):
        """Start the node server"""
        print(f"\nRageCoin node starting on port {self.port}...")
        print(f"API available at http://localhost:{self.port}")
        self.app.run(host=host, port=self.port, debug=False)
