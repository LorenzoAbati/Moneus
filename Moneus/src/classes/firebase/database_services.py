
import pyrebase
import sys
import os

sys.path.append("..")
try:
    from firebase_config import firebaseConfig
except:
    from firebase.firebase_config import firebaseConfig

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from wallet import Wallet
from peer import Peer
from miner import Miner
from objects import handyman

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
auth = firebase.auth()
storage = firebase.storage()


def set(peer, key_value):
    try:
        if peer.is_miner:
            data = {
                'email':peer.email, 
                'secret_key':peer.secret_key.as_hex(), 
                'public_key':peer.public_key.as_hex(), 
                'wallet_address':peer.wallet.address,
                'moneus_amount':peer.wallet.money,
                'hashrate':peer.hashrate
            }
            db.child("peers").child(key_value).set(data)

    except:
        data = {
            'email':peer.email, 
            'secret_key':peer.secret_key.as_hex(), 
            'public_key':peer.public_key.as_hex(), 
            'wallet_address':peer.wallet.address,
            'moneus_amount':peer.wallet.money
        }
        db.child("peers").child(key_value).set(data)

    data = {
            'public_key':peer.public_key.as_hex()
        }

    db.child("public_keys").child(peer.wallet.address).set(data)


def get(key_value): 

    peers = db.child("peers").child(key_value).get()
    
    peer = peers.val()
    wallet = Wallet(peer['wallet_address'],peer['moneus_amount'])
    private_key = handyman.private_key_string_to_object(peer['secret_key'])
    public_key = handyman.public_key_string_to_object(peer['public_key'],private_key)

    try:
        miner = Miner(peer['email'], private_key, public_key, wallet, peer["hashrate"],True)
        return miner, "miner"
    except:
        user = Peer(peer['email'], private_key, public_key, wallet)
        return user, "user"


def get_public_key(wallet_address):

    pks = db.child("public_keys").get()
    
    for i in pks.each():
    
        if i.key() == wallet_address:
            pk = i.val()

            return pk['public_key']


def update_value(id, key, value):
    db.child("peers").child(str(id)).update({key: value})


def set_miner_status(wallet_address, status):
    db.child("miners_status").child(wallet_address).set(status)


def get_miner_status(wallet_address):
    status = db.child("miners_status").child(wallet_address).get()
    return status.val()
    