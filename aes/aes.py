from aes.state import State
from aes.key_expansion import key_expansion

# main file containing AES encrypt and decrypt methods 

# algorithm constructed and tested as described in
# https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf
# and on wiki
# https://en.wikipedia.org/wiki/Advanced_Encryption_Standard

def encrypt(input: str, cipher_key: str) -> str:
    """AES encrypt, given input and cipher_key as 128-bit hex number"""

    # generate round keys
    Nk = 11
    key = State(number=cipher_key)
    round_keys = key_expansion(key, Nk)

    # add first round key
    state = State(number=input)
    state ^= round_keys[0]

    for i in range(1, Nk - 1):
        state.sub_bytes()
        state.shift_rows()
        state.mix_columns()
        state ^= round_keys[i]

    state.sub_bytes()
    state.shift_rows()
    state ^= round_keys[-1]
    state.transpose()

    return state.to_hex_str()

def decrypt(hash: str, cipher_key: str) -> str:
    """AES decrypt, given input and cipher_key as 128-bit hex number"""

    Nk = 11
    key = State(number=cipher_key)
    round_keys = key_expansion(key, Nk)

    state = State(number=hash)
    state.transpose()
    state ^= round_keys[-1]
    state.inv_shift_rows()
    state.inv_sub_bytes()

    for i in range(Nk - 2, 0, -1):
        state ^= round_keys[i]        
        state.inv_mix_columns()        
        state.inv_shift_rows()
        state.inv_sub_bytes()

    state ^= round_keys[0]
    return state.to_hex_str()