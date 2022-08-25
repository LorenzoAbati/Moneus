# pyright: reportMissingImports=false

from sawtooth_signing.secp256k1 import Secp256k1PublicKey
import binascii
import warnings
from sawtooth_signing.core import ParseError
from sawtooth_signing.core import PublicKey
import secp256k1

__CONTEXTBASE__ = secp256k1.Base(ctx=None, flags=secp256k1.ALL_FLAGS)
__CTX__ = __CONTEXTBASE__.ctx
__PK__ = secp256k1.PublicKey(ctx=__CTX__)  # Cache object to use as factory


class Secp256k1PublicKey(PublicKey):
    def __init__(self, secp256k1_public_key):
        self._public_key = secp256k1_public_key

    @property
    def secp256k1_public_key(self):
        return self._public_key

    def get_algorithm_name(self):
        return "secp256k1"

    def as_hex(self):
        return binascii.hexlify(self.as_bytes()).decode()

    def as_bytes(self):
        with warnings.catch_warnings():  # squelch secp256k1 warning
            warnings.simplefilter('ignore')
            return self._public_key.serialize()

    @staticmethod
    def from_bytes(byte_str):
        public_key = secp256k1.PublicKey(byte_str, raw=True, ctx=__CTX__)
        return Secp256k1PublicKey(public_key)

    @staticmethod
    def from_hex(hex_str):
        try:
            public_key = __PK__.deserialize(binascii.unhexlify(hex_str))

            return Secp256k1PublicKey(
                secp256k1.PublicKey(public_key, ctx=__CTX__))
        except Exception as e:
            raise ParseError('Unable to parse public key: {}'.format(e))

