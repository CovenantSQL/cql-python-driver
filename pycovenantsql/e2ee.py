from Crypto.Cipher import AES
from Crypto import Random
import hashlib
from binascii import hexlify, unhexlify

BLOCK_SIZE = AES.block_size  # Bytes

salt = unhexlify("3fb8877d37fdc04e4a4765EFb8ab7d36")


class PaddingError(Exception):
    """Exception raised for errors in the padding.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message


pad = lambda s: s + ((BLOCK_SIZE - len(s) % BLOCK_SIZE) *
                     chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)).encode('ascii')


def unpad(s):
    in_len = len(s)
    if in_len == 0:
        raise PaddingError("empty input")
    pad_char = s[-1]
    if pad_char > BLOCK_SIZE:
        raise PaddingError("padding length > 16")
    for i in s[in_len - pad_char:]:
        if i != pad_char:
            raise PaddingError("unexpected padding char")
    return s[:-pad_char]


# kdf does 2 times sha256 and takes the first 16 bytes
def kdf(raw_key):
    """
    kdf does 2 times sha256 and takes the first 16 bytes
    :param raw_key:
    :return:
    """
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
