import hashlib
import json
from typing import Optional
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError


class Transaction:
    """Represents a transaction in the blockchain"""

    def __init__(self, sender: str, recipient: str, amount: float, signature: Optional[str] = None):
        self.sender = sender  # Public key of sender
        self.recipient = recipient  # Public key of recipient
        self.amount = amount
        self.signature = signature

    def calculate_hash(self) -> str:
        """Calculate the hash of the transaction"""
        tx_string = json.dumps({
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount
        }, sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()

    def sign_transaction(self, private_key: str) -> None:
        """Sign the transaction with the sender's private key"""
        if self.sender == "COINBASE":
            # Coinbase transactions (mining rewards) don't need signatures
            return

        sk = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        tx_hash = self.calculate_hash()
        signature = sk.sign(tx_hash.encode())
        self.signature = signature.hex()

    def is_valid(self) -> bool:
        """Verify the transaction signature"""
        if self.sender == "COINBASE":
            return True

        if not self.signature:
            return False

        try:
            vk = VerifyingKey.from_string(bytes.fromhex(self.sender), curve=SECP256k1)
            tx_hash = self.calculate_hash()
            vk.verify(bytes.fromhex(self.signature), tx_hash.encode())
            return True
        except (BadSignatureError, Exception):
            return False

    def to_dict(self) -> dict:
        """Convert transaction to dictionary"""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "signature": self.signature
        }

    @staticmethod
    def from_dict(tx_dict: dict) -> 'Transaction':
        """Create a transaction from dictionary"""
        return Transaction(
            tx_dict["sender"],
            tx_dict["recipient"],
            tx_dict["amount"],
            tx_dict.get("signature")
        )
