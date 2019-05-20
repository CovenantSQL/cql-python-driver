from Crypto.Cipher import AES
from Crypto import Random
import hashlib
from binascii import hexlify, unhexlify


BLOCK_SIZE = AES.block_size  # Bytes
pad = lambda s: s + ((BLOCK_SIZE - len(s) % BLOCK_SIZE) *
                     chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)).encode('utf-8')
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

salt = unhexlify("3fb8877d37fdc04e4a4765EFb8ab7d36")


# kdf does 2 times sha256 and takes the first 16 bytes
def kdf(raw_key):
    return hashlib.sha256(hashlib.sha256(raw_key.encode('utf-8') + salt).digest()).digest()[:16]


def encrypt(raw, password):
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(kdf(password), AES.MODE_CBC, iv)
    return iv + cipher.encrypt(pad(raw))


def decrypt(enc, password):
    iv = enc[:16]
    cipher = AES.new(kdf(password), AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))
