# pyright: reportMissingImports=false


from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
import binascii
from sawtooth_signing.core import ParseError
from sawtooth_signing.core import PrivateKey
import secp256k1
import bitcoinutils as pybitcointools

__CONTEXTBASE__ = secp256k1.Base(ctx=None, flags=secp256k1.ALL_FLAGS)
__CTX__ = __CONTEXTBASE__.ctx
__PK__ = secp256k1.PublicKey(ctx=__CTX__)  # Cache object to use as factory


class Secp256k1PrivateKey(PrivateKey):

    def __init__(self, secp256k1_private_key):
        self._private_key = secp256k1_private_key

    def get_algorithm_name(self):
        return "secp256k1"

    def as_hex(self):
        return binascii.hexlify(self.as_bytes()).decode()

    def as_bytes(self):
        return bytes(self._private_key.private_key)

    @property
    def secp256k1_private_key(self):
        return self._private_key

    @staticmethod
    def from_wif(wif):
        #Decodes a PrivateKey from a wif-encoded string
        
        try:
            priv = pybitcointools.encode_privkey(wif, 'hex')
            priv = binascii.unhexlify(priv)
            return Secp256k1PrivateKey(
                secp256k1.PrivateKey(priv, ctx=__CTX__))
        except Exception as e:
            raise ParseError('Unable to parse wif key: {}'.format(e))

    @staticmethod
    def from_hex(hex_str):
        try:
            priv = binascii.unhexlify(hex_str)
            return Secp256k1PrivateKey(secp256k1.PrivateKey(priv, ctx=__CTX__))
        except Exception as e:
            raise ParseError('Unable to parse hex private key: {}'.format(e))

    @staticmethod
    def new_random():
        return Secp256k1PrivateKey(secp256k1.PrivateKey(ctx=__CTX__))

