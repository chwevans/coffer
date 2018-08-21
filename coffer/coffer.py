import os
import sys
import functools
import simplejson as json

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

rpc_url = "http://%s:%s@%s" % (os.environ['BTC_USER'], os.environ['BTC_PASS'], os.environ['BTC_HOST'])
CLIENT = AuthServiceProxy(rpc_url)
SATOSHI_CONVERSION = 100000000

START_COINBASE = 50.0
HALF_PERIOD = 210000

def block_reward(block_height):
    # Note that the power of 2 is using integer division.
    # The block reward halfs every HALF_PERIOD blocks, but doesn't
    # change at all before then.
    return START_COINBASE / (2 ** (block_height // HALF_PERIOD))

def block_gen(start_hash):
    """
    Iterate over blocks, block by block
    """
    # Add a wait or stop condition here
    while True:
        next_block = CLIENT.getblock(start_hash)
        yield next_block
        start_hash = next_block['nextblockhash']

def transaction_gen(block):
    """
    Iterate over the transactions in a given block
    """
    for tx_hash in block['tx']:
        # The second argument represents the verbosity
        yield get_transaction(tx_hash)

@functools.lru_cache(maxsize=1024)
def get_transaction(tx_hash):
    return CLIENT.getrawtransaction(tx_hash, 1)

def pp(item):
    print(json.dumps(item, indent=4, sort_keys=True, use_decimal=True))

# All of vin has to sum to vout
# What doesn't add up goes to miners
def parse_transaction(block, transaction):
    # TODO: Convert amounts to satoshis
    tx = {
            'txid': transaction['txid'],
            'sources': [],
            'outputs': []
    }
    for vin in transaction['vin']:
        if 'coinbase' in vin:
            # This VIN is newly generated from a coinbase
            tx['sources'].append({
                'type': 'coinbase',
                # TODO: This is buggy
                'amount': block_reward(block['height'])
            })
        else:
            # Transaction is sourced from a previous transaction
            in_tx = get_transaction(vin['txid'])
            # Get the n'th vout from the referred transaction
            tx_vout = vin['vout']
            vout = in_tx['vout'][tx_vout]

            tx['sources'].append({
                'type': 'address',
                # TODO: This may break with multisig
                'address': vout['scriptPubKey']['addresses'][0],
                'amount': vout['value']
            })

    for vout in transaction['vout']:
        # This is a normal expenditure
        tx['outputs'].append({
            'type': 'address',
            # If there are multiple addresses, its multisig, see:
            # https://www.blockchain.com/btc/tx/56214420a7c4dcc4832944298d169a75e93acf9721f00656b2ee0e4d194f9970
            'address': vout['scriptPubKey']['addresses'][0],
            'amount': vout['value']
        })

    return tx


# block = CLIENT.getblock(CLIENT.getblockhash(100001))
# # Modern block, lots of transactions
# # vins have references to txids instead of addresses (must get those transactions and get the vouts as the new vin (jfc))
# for tx in transaction_gen(block):
#     pp(parse_transaction(block, tx))
# 
# sys.exit(1)

# We skip the genesis block as it has no ordinary transactions
start_hash = CLIENT.getblockhash(2)
print(start_hash)
for block in block_gen(start_hash):
    for tx in transaction_gen(block):
        pp(parse_transaction(block, tx))

