import json
from ecdsa import SigningKey, SECP256k1
from typing import Optional


class Wallet:
    """Cryptocurrency wallet for managing keys and signing transactions"""

    def __init__(self, private_key: Optional[str] = None):
        if private_key:
            self.private_key = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        else:
            # Generate new key pair
            self.private_key = SigningKey.generate(curve=SECP256k1)

        self.public_key = self.private_key.get_verifying_key()

    def get_private_key_hex(self) -> str:
        """Get private key as hex string"""
        return self.private_key.to_string().hex()

    def get_public_key_hex(self) -> str:
        """Get public key (address) as hex string"""
        return self.public_key.to_string().hex()

    def get_address(self) -> str:
        """Get wallet address (public key)"""
        return self.get_public_key_hex()

    def save_to_file(self, filename: str) -> None:
        """Save wallet to file"""
        wallet_data = {
            "private_key": self.get_private_key_hex(),
            "public_key": self.get_public_key_hex()
        }
        with open(filename, 'w') as f:
            json.dump(wallet_data, f, indent=2)
        print(f"Wallet saved to {filename}")

    @staticmethod
    def load_from_file(filename: str) -> 'Wallet':
        """Load wallet from file"""
        with open(filename, 'r') as f:
            wallet_data = json.load(f)
        return Wallet(wallet_data["private_key"])

    def display_info(self) -> None:
        """Display wallet information"""
        print("\n=== Wallet Information ===")
        print(f"Address (Public Key): {self.get_address()}")
        print(f"Private Key: {self.get_private_key_hex()}")
        print("=" * 50)
