from aes.state import State
from aes.key_expansion import key_expansion


def encrypt(input: str, cipher_key: str) -> str:
    
    Nk = 11
    key = State(number=cipher_key)
    round_keys = key_expansion(key, Nk)
    
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