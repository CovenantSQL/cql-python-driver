# coding: utf-8

import unittest
from pycovenantsql.e2ee import encrypt, decrypt
from binascii import hexlify, unhexlify

# Test cases for all implementations.
# Because iv is random, so Encrypted data is not always the same,
# 	but Decrypt(possibleEncrypted) will get raw.
cases = [
    {
        "raw": "11",
        "pass": ";#K]As9C*6L",
        "possibleEncrypted": "a372ea2c158a2f99d386e309db4355a659a7a8dd3986fd1d94f7604256061609",
    },
    {
        "raw": "111282C128421286712857128C2128EF" +
               "128B7671283C128571287512830128EC" +
               "128391281A1312849128381281E1286A" +
               "12871128621287A9D12857128C412886" +
               "128FD12834128DA128F5",
        "pass": "",
        "possibleEncrypted": "1bfb6a7fda3e3eb1e14c9afd0baefe86" +
                             "c90979101f179db7e48a0fa7617881e8" +
                             "f752c59fb512bb86b8ed69c5644bf2dc" +
                             "30fbcd3bf79fb20342595c84fad00e46" +
                             "2fab3e51266492a3d5d085e650c1e619" +
                             "6278d7f5185c263440ec6fd940ffbb85",
    },
    {
        "raw": "11",
        "pass": "'K]\"#'pi/1/JD2",
        "possibleEncrypted": "a83d152777ce3a1c0710b03676ae867c86ab0a47b3ca080f825683ac1079eb41",
    },
    {
        "raw": "11111111111111111111111111111111",
        "pass": "",
        "possibleEncrypted": "7dda438c4256a63c62d6816617fcbf9c" +
                             "7773b9b4f87902b7253848ba2b0ed0ba" +
                             "f70a3ac976a835b7bc3008e9ba43da74",
    },
    {
        "raw": "11111111111111111111111111111111",
        "pass": "youofdas1312",
        "possibleEncrypted": "cab07967cf377dbc010fbf5f84d12bcb" +
                             "6f8b188e6965738cf9007a671b4bfeb9" +
                             "f52257aac3808048c341dcaa1c125ca7",
    },
    {
        "raw": "11111111111111111111111111",
        "pass": "空のBottle😄",
        "possibleEncrypted": "4384874473945c5b70519ad5ace6305ef6b78c60c3c694add08a8b81899c4171",
    },
]


class TestE2ee(unittest.TestCase):
    def test_enc_dec(self):
        i = 0
        for case in cases:
            print("Case: #" + str(i))
            i += 1
            enc = encrypt(unhexlify(case["raw"]), case["pass"])
            dec = decrypt(enc, case["pass"])
            self.assertEqual(unhexlify(case["raw"]), dec)
            dec2 = decrypt(unhexlify(case["possibleEncrypted"]), case["pass"])
            self.assertEqual(unhexlify(case["raw"]), dec2)
