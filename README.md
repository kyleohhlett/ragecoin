# RageCoin

A Bitcoin-like cryptocurrency implementation in Python with proof-of-work mining, digital signatures, and P2P networking.

## Features

- **Blockchain**: Immutable ledger with proof-of-work consensus
- **Mining**: SHA-256 based proof-of-work algorithm
- **Wallets**: ECDSA key pairs for secure transactions
- **Transactions**: Cryptographically signed transfers
- **P2P Network**: Decentralized node communication with consensus
- **REST API**: Full HTTP API for blockchain interaction

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Make CLI executable
chmod +x ragecoin.py
```

## Quick Start

### 1. Start a Node

```bash
# Start the first node
python ragecoin.py node -p 5000
```

In another terminal, start additional nodes:

```bash
# Start second node connected to first
python ragecoin.py node -p 5001 --peers http://localhost:5000

# Start third node
python ragecoin.py node -p 5002 --peers http://localhost:5000 http://localhost:5001
```

### 2. Create Wallets

```bash
# Create a wallet
python ragecoin.py wallet-create -o miner_wallet.json

# Show wallet info
python ragecoin.py wallet-show miner_wallet.json
```

### 3. Mine Blocks

```bash
# Mine a block (rewards go to your wallet)
python ragecoin.py mine miner_wallet.json -p 5000
```

### 4. Check Balance

```bash
# Check balance of an address
python ragecoin.py balance <your_address> -p 5000
```

### 5. Send Transactions

```bash
# Create second wallet for recipient
python ragecoin.py wallet-create -o recipient_wallet.json

# Send coins
python ragecoin.py send miner_wallet.json <recipient_address> 10.5 --broadcast -p 5000

# Mine the transaction into a block
python ragecoin.py mine miner_wallet.json -p 5000
```

### 6. View Blockchain

```bash
# View the blockchain
python ragecoin.py chain -p 5000
```

## CLI Commands

### Wallet Commands

- `wallet-create` - Create a new wallet with ECDSA key pair
- `wallet-show <file>` - Display wallet information

### Transaction Commands

- `send <wallet> <recipient> <amount>` - Create and optionally broadcast a transaction
- `balance <address>` - Check balance of an address

### Mining Commands

- `mine <wallet>` - Mine pending transactions into a new block

### Blockchain Commands

- `chain` - Display the blockchain

### Node Commands

- `node` - Start a blockchain node with P2P networking

## API Endpoints

### GET /chain
Get the complete blockchain

### POST /mine
Mine pending transactions
```json
{
  "miner_address": "wallet_public_key"
}
```

### POST /transactions/new
Submit a new transaction
```json
{
  "sender": "sender_public_key",
  "recipient": "recipient_public_key",
  "amount": 10.5,
  "signature": "transaction_signature"
}
```

### GET /balance/<address>
Get balance of an address

### GET /validate
Validate the blockchain integrity

### POST /peers/register
Register a peer node
```json
{
  "peer": "http://localhost:5001"
}
```

### GET /peers
Get list of connected peers

### GET /consensus
Trigger consensus algorithm (longest chain rule)

## Architecture

### Block Structure
```python
{
  "index": 1,
  "transactions": [...],
  "timestamp": 1234567890,
  "previous_hash": "abc123...",
  "nonce": 12345,
  "hash": "000abc..."
}
```

### Transaction Structure
```python
{
  "sender": "public_key_hex",
  "recipient": "public_key_hex",
  "amount": 10.5,
  "signature": "ecdsa_signature_hex"
}
```

## How It Works

1. **Mining**: Nodes compete to find a nonce that produces a hash with leading zeros (proof-of-work)
2. **Consensus**: Longest valid chain is accepted as truth
3. **Validation**: All transactions are verified using ECDSA signatures
4. **Rewards**: Miners receive 50 RAGE coins per block (coinbase transaction)

## Configuration

- **Difficulty**: 4 leading zeros (configurable in `blockchain.py`)
- **Mining Reward**: 50 RAGE (configurable in `blockchain.py`)
- **Default Port**: 5000 (configurable via CLI)

## Example Workflow

```bash
# Terminal 1: Start node
python ragecoin.py node -p 5000

# Terminal 2: Create wallet and mine
python ragecoin.py wallet-create -o wallet.json
python ragecoin.py mine wallet.json

# Check your balance
python ragecoin.py wallet-show wallet.json
# Copy your address
python ragecoin.py balance <your_address>

# Create second wallet
python ragecoin.py wallet-create -o wallet2.json

# Send coins
python ragecoin.py send wallet.json <wallet2_address> 25 --broadcast

# Mine to confirm transaction
python ragecoin.py mine wallet.json

# Verify balances
python ragecoin.py balance <wallet1_address>
python ragecoin.py balance <wallet2_address>
```

## Security Features

- ECDSA (secp256k1) for signatures (same as Bitcoin)
- SHA-256 hashing for blocks
- Proof-of-work prevents blockchain manipulation
- Transaction validation prevents double-spending
- Balance checking prevents overspending

## Technical Details

- **Language**: Python 3.7+
- **Consensus**: Proof-of-Work (longest chain)
- **Signature Algorithm**: ECDSA (secp256k1)
- **Hash Algorithm**: SHA-256
- **Network**: REST API with Flask
- **P2P Protocol**: HTTP-based peer discovery and sync

## License

MIT License - Feel free to use and modify!

## Contributing

RageCoin is a learning project demonstrating cryptocurrency fundamentals. Contributions welcome!

---

**Disclaimer**: This is an educational project. Not for production use or real financial transactions.
