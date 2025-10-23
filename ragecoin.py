#!/usr/bin/env python3
"""
RageCoin - A Bitcoin-like cryptocurrency implementation
Command-line interface for wallet, mining, and blockchain operations
"""

import argparse
import os
import sys
from wallet import Wallet
from blockchain import Blockchain
from transaction import Transaction
from node import Node


def create_wallet(args):
    """Create a new wallet"""
    wallet = Wallet()
    wallet.display_info()

    if args.output:
        wallet.save_to_file(args.output)
    else:
        save = input("\nSave wallet to file? (y/n): ")
        if save.lower() == 'y':
            filename = input("Enter filename (default: wallet.json): ").strip()
            if not filename:
                filename = "wallet.json"
            wallet.save_to_file(filename)


def show_wallet(args):
    """Show wallet information"""
    if not os.path.exists(args.file):
        print(f"Error: Wallet file '{args.file}' not found!")
        return

    wallet = Wallet.load_from_file(args.file)
    wallet.display_info()


def send_transaction(args):
    """Create and sign a transaction"""
    if not os.path.exists(args.wallet):
        print(f"Error: Wallet file '{args.wallet}' not found!")
        return

    wallet = Wallet.load_from_file(args.wallet)

    # Create transaction
    tx = Transaction(wallet.get_address(), args.recipient, args.amount)
    tx.sign_transaction(wallet.get_private_key_hex())

    print("\n=== Transaction Created ===")
    print(f"From: {tx.sender[:20]}...")
    print(f"To: {tx.recipient[:20]}...")
    print(f"Amount: {tx.amount} RAGE")
    print(f"Signature: {tx.signature[:40]}...")
    print("=" * 50)

    if args.broadcast:
        import requests
        try:
            response = requests.post(
                f'http://localhost:{args.port}/transactions/new',
                json=tx.to_dict(),
                timeout=5
            )
            if response.status_code == 201:
                print("\nTransaction broadcast successfully!")
            else:
                print(f"\nFailed to broadcast: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"\nError broadcasting transaction: {e}")


def check_balance(args):
    """Check balance of an address"""
    import requests
    try:
        response = requests.get(f'http://localhost:{args.port}/balance/{args.address}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"\nAddress: {data['address'][:20]}...")
            print(f"Balance: {data['balance']} RAGE")
        else:
            print("Error checking balance")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def mine_block(args):
    """Mine pending transactions"""
    if not os.path.exists(args.wallet):
        print(f"Error: Wallet file '{args.wallet}' not found!")
        return

    wallet = Wallet.load_from_file(args.wallet)
    miner_address = wallet.get_address()

    import requests
    try:
        print(f"\nMining block... (Reward will go to: {miner_address[:20]}...)")
        response = requests.post(
            f'http://localhost:{args.port}/mine',
            json={'miner_address': miner_address},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"\n{data['message']}")
            print(f"Block #{data['block']['index']} mined!")
            print(f"Hash: {data['block']['hash']}")
        else:
            print("Mining failed")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def show_blockchain(args):
    """Display the blockchain"""
    import requests
    try:
        response = requests.get(f'http://localhost:{args.port}/chain', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"\n=== RageCoin Blockchain ===")
            print(f"Difficulty: {data['difficulty']}")
            print(f"Mining Reward: {data['mining_reward']} RAGE")
            print(f"Total Blocks: {len(data['chain'])}")
            print(f"Pending Transactions: {len(data['pending_transactions'])}")
            print("\n=== Blocks ===")

            for block in data['chain'][-10:]:  # Show last 10 blocks
                print(f"\nBlock #{block['index']}")
                print(f"Hash: {block['hash']}")
                print(f"Previous: {block['previous_hash'][:20]}...")
                print(f"Transactions: {len(block['transactions'])}")
                print(f"Nonce: {block['nonce']}")
        else:
            print("Error retrieving blockchain")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def start_node(args):
    """Start a blockchain node"""
    node = Node(port=args.port)

    if args.peers:
        for peer in args.peers:
            node.register_with_peer(peer)

    node.run()


def main():
    parser = argparse.ArgumentParser(description='RageCoin - Bitcoin-like cryptocurrency')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Wallet commands
    wallet_create = subparsers.add_parser('wallet-create', help='Create a new wallet')
    wallet_create.add_argument('-o', '--output', help='Output file for wallet')

    wallet_show = subparsers.add_parser('wallet-show', help='Show wallet information')
    wallet_show.add_argument('file', help='Wallet file')

    # Transaction commands
    send = subparsers.add_parser('send', help='Send RageCoins')
    send.add_argument('wallet', help='Wallet file')
    send.add_argument('recipient', help='Recipient address')
    send.add_argument('amount', type=float, help='Amount to send')
    send.add_argument('-b', '--broadcast', action='store_true', help='Broadcast to network')
    send.add_argument('-p', '--port', type=int, default=5000, help='Node port')

    balance = subparsers.add_parser('balance', help='Check balance')
    balance.add_argument('address', help='Address to check')
    balance.add_argument('-p', '--port', type=int, default=5000, help='Node port')

    # Mining commands
    mine = subparsers.add_parser('mine', help='Mine a block')
    mine.add_argument('wallet', help='Wallet file for mining rewards')
    mine.add_argument('-p', '--port', type=int, default=5000, help='Node port')

    # Blockchain commands
    chain = subparsers.add_parser('chain', help='Show blockchain')
    chain.add_argument('-p', '--port', type=int, default=5000, help='Node port')

    # Node commands
    node = subparsers.add_parser('node', help='Start a blockchain node')
    node.add_argument('-p', '--port', type=int, default=5000, help='Port to run on')
    node.add_argument('--peers', nargs='+', help='Peer nodes to connect to')

    args = parser.parse_args()

    if args.command == 'wallet-create':
        create_wallet(args)
    elif args.command == 'wallet-show':
        show_wallet(args)
    elif args.command == 'send':
        send_transaction(args)
    elif args.command == 'balance':
        check_balance(args)
    elif args.command == 'mine':
        mine_block(args)
    elif args.command == 'chain':
        show_blockchain(args)
    elif args.command == 'node':
        start_node(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
