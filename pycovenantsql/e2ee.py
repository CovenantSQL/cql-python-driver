from Crypto.Cipher import AES
from Crypto import Random
import hashlib
from binascii import hexlify, unhexlify


BLOCK_SIZE = AES.block_size  # Bytes
pad = lambda s: s + ((BLOCK_SIZE - len(s) % BLOCK_SIZE) *
                     chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)).encode('utf-8')


unpad = lambda s: s[:-ord(s[len(s) - 1:])]

salt = unhexlify("3fb8877d37fdc04e4a4765EFb8ab7d36")

class PaddingError(Exception):
    """Exception raised for errors in the padding.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


def unpad(s):
    inLen = len(s)
    if inLen == 0:
        raise PaddingError("empty input")
    padChar = s[-1]
    padLen = ord(s[inLen-1:])
    if padLen > BLOCK_SIZE:
        raise PaddingError("padding length > 16")
    for i in s[inLen-padLen:]:
        if i != padChar:
            raise PaddingError("unknown padding char")
    return s[:-padLen]


# kdf does 2 times sha256 and takes the first 16 bytes
def kdf(raw_key):
    return hashlib.sha256(hashlib.sha256(raw_key + salt).digest()).digest()[:16]


def encrypt(raw, password):
    """
    encrypt encrypts data with given password by AES-128-CBC PKCS#7, iv will be placed
    at head of cipher data.

    :param raw: input raw byte array
    :param password: password byte array
    :return: encrypted byte array
    """
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(kdf(password), AES.MODE_CBC, iv)
    return iv + cipher.encrypt(pad(raw))


def decrypt(enc, password):
    """
    decrypt decrypts data with given password by AES-128-CBC PKCS#7. iv will be read from
    the head of raw.

    :param enc: input encrypted byte array
    :param password: password byte array
    :return: decrypted byte array
    """
    iv = enc[:16]
    cipher = AES.new(kdf(password), AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))
