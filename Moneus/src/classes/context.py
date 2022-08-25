
from pyasn1_modules.rfc2459 import PrivateKeyUsagePeriod
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_signing.secp256k1 import Secp256k1PublicKey
import hashlib
import json
import codecs
from sawtooth_signing.core import SigningError
from sawtooth_signing.core import Context
import secp256k1

__CONTEXTBASE__ = secp256k1.Base(ctx=None, flags=secp256k1.ALL_FLAGS)
__CTX__ = __CONTEXTBASE__.ctx
__PK__ = secp256k1.PublicKey(ctx=__CTX__)  # Cache object to use as factory


class Context(Context):

    def __init__(self):
        self._ctx = __CTX__

    def get_algorithm_name(self):
        return "secp256k1"

    def sign(self, message, private_key):
        try:
            signature = private_key.secp256k1_private_key.ecdsa_sign(message)
            signature = private_key.secp256k1_private_key \
                .ecdsa_serialize_compact(signature)

            return signature.hex()
        except Exception as e:
            raise SigningError('Unable to sign message: {}'.format(str(e)))

    def verify(self, signature, message, public_key):
        try:
            sig_bytes = bytes.fromhex(signature)

            sig = public_key.secp256k1_public_key.ecdsa_deserialize_compact(
                sig_bytes)
            return public_key.secp256k1_public_key.ecdsa_verify(message, sig)
        # pylint: disable=broad-except
        except Exception:
            return False

    def new_random_private_key(self):
        return Secp256k1PrivateKey.new_random()

    def get_public_key(self, private_key):
        return Secp256k1PublicKey(private_key.secp256k1_private_key.pubkey)

    def generate_wallet_address(self, secret_key):
        
        PK0 = secret_key
        PK1 = '80'+ PK0
        PK2 = hashlib.sha256(codecs.decode(PK1, 'hex'))
        PK3 = hashlib.sha256(PK2.digest())
        checksum = codecs.encode(PK3.digest(), 'hex')[0:8]
        PK4 = PK1 + str(checksum)[2:10]  #I know it looks wierd
        address_hex = PK4

        alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        b58_string = ''
        # Get the number of leading zeros
        leading_zeros = len(address_hex) - len(address_hex.lstrip('0'))
        # Convert hex to decimal
        address_int = int(address_hex, 16)
        # Append digits to the start of string
        while address_int > 0:
            digit = address_int % 58
            digit_char = alphabet[digit]
            b58_string = digit_char + b58_string
            address_int //= 58
        # Add ‘1’ for each 2 leading zeros
        ones = leading_zeros // 2
        for one in range(ones):
            b58_string = '1' + b58_string
        return b58_string

    def get_number_of_blocks(self, blockchain):

        return len(blockchain.keys())

    def hash_email(self, email):
        h = hashlib.sha1(email.encode())
        return h.hexdigest()

    def private_key_string_to_object(self, private_key):
        return self.new_random_private_key().from_hex(private_key)
    
    def public_key_string_to_object(self, public_key, private_key):
        return self.get_public_key(private_key).from_hex(public_key)
    
    def public_key_hex_string_to_object(self, stringa):
        private_key = self.new_random_private_key()
        public_key = self.get_public_key(private_key)
        right_public_key = public_key.from_hex(stringa)

        return right_public_key


