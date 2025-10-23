import json
import time
from typing import List, Optional, Dict
from block import Block
from transaction import Transaction


class Blockchain:
    """The main blockchain class"""

    def __init__(self, difficulty: int = 4, mining_reward: float = 50.0):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions: List[Transaction] = []
        self.mining_reward = mining_reward
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        """Create the first block in the chain"""
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]

    def mine_pending_transactions(self, mining_reward_address: str) -> None:
        """Mine all pending transactions and reward the miner"""
        # Create coinbase transaction (mining reward)
        reward_tx = Transaction("COINBASE", mining_reward_address, self.mining_reward)
        self.pending_transactions.insert(0, reward_tx)

        # Create new block with pending transactions
        block = Block(
            len(self.chain),
            [tx.to_dict() for tx in self.pending_transactions],
            time.time(),
            self.get_latest_block().hash
        )

        print(f"Mining block {block.index}...")
        block.mine_block(self.difficulty)
        self.chain.append(block)

        # Clear pending transactions
        self.pending_transactions = []

    def add_transaction(self, transaction: Transaction) -> bool:
        """Add a new transaction to pending transactions"""
        if not transaction.sender or not transaction.recipient:
            return False

        if not transaction.is_valid():
            print("Invalid transaction signature!")
            return False

        # Check if sender has enough balance (except for coinbase)
        if transaction.sender != "COINBASE":
            balance = self.get_balance(transaction.sender)
            if balance < transaction.amount:
                print(f"Insufficient balance! Has {balance}, needs {transaction.amount}")
                return False

        self.pending_transactions.append(transaction)
        return True

    def get_balance(self, address: str) -> float:
        """Get the balance of an address"""
        balance = 0.0

        for block in self.chain:
            for tx in block.transactions:
                if tx["sender"] == address:
                    balance -= tx["amount"]
                if tx["recipient"] == address:
                    balance += tx["amount"]

        # Include pending transactions
        for tx in self.pending_transactions:
            if tx.sender == address:
                balance -= tx.amount
            if tx.recipient == address:
                balance += tx.amount

        return balance

    def is_chain_valid(self) -> bool:
        """Verify the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Verify hash is correct
            if current_block.hash != current_block.calculate_hash():
                print(f"Block {i} has invalid hash!")
                return False

            # Verify link to previous block
            if current_block.previous_hash != previous_block.hash:
                print(f"Block {i} has invalid previous hash!")
                return False

            # Verify proof of work
            if not current_block.hash.startswith("0" * self.difficulty):
                print(f"Block {i} has invalid proof of work!")
                return False

            # Verify all transactions in the block
            for tx_dict in current_block.transactions:
                tx = Transaction.from_dict(tx_dict)
                if not tx.is_valid():
                    print(f"Block {i} contains invalid transaction!")
                    return False

        return True

    def to_dict(self) -> Dict:
        """Convert blockchain to dictionary"""
        return {
            "chain": [block.to_dict() for block in self.chain],
            "difficulty": self.difficulty,
            "mining_reward": self.mining_reward,
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions]
        }

    def save_to_file(self, filename: str) -> None:
        """Save blockchain to file"""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def load_from_file(filename: str) -> 'Blockchain':
        """Load blockchain from file"""
        with open(filename, 'r') as f:
            data = json.load(f)

        blockchain = Blockchain(data["difficulty"], data["mining_reward"])
        blockchain.chain = [Block.from_dict(block_dict) for block_dict in data["chain"]]
        blockchain.pending_transactions = [
            Transaction.from_dict(tx_dict) for tx_dict in data["pending_transactions"]
        ]
        return blockchain
