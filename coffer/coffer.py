import os
import sys

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

SATOSHI_CONVERSION = 100000000

def block_gen(client, start_hash):
    """
    Iterate over blocks, block by block
    """
    # Add a wait or stop condition here
    while True:
        next_block = client.getblock(start_hash)
        yield next_block
        start_hash = next_block['nextblockhash']

def transaction_gen(client, block):
    """
    Iterate over the transactions in a given block
    """
    for tx_hash in block['tx']:
        # The second argument represents the verbosity
        yield client.getrawtransaction(tx_hash, 1)

rpc_url = "http://%s:%s@%s" % (os.environ['BTC_USER'], os.environ['BTC_PASS'], os.environ['BTC_HOST'])
client = AuthServiceProxy(rpc_url)

#block = client.getblock('00000000b2cde2159116889837ecf300bd77d229d49b138c55366b54626e495d')
#print(block)
#for tx in transaction_gen(client, block):
#    print(tx)
#
#sys.exit(1)

# We skip the genesis block as it has no ordinary transactions
start_hash = client.getblockhash(1)
for block in block_gen(client, start_hash):
    #print(block)
    inputs = []
    outputs = []
    for tx in transaction_gen(client, block):
        #print(tx)
        inputs = tx['vin']
        for output in tx['vout']:
            outputs.append({
                'satoshis': int(output['value'] * SATOSHI_CONVERSION),
                'addresses': output['scriptPubKey']['addresses']
            })

    print({
        'hash': block['hash'],
        'inputs': inputs,
        'outputs': outputs
    })


