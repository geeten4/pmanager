import numpy as np
from typing import List
from aes.s_box import sbox
from aes.state import State

def key_expansion(cipher_key: State, N: int) -> List[State]:
    # https://en.wikipedia.org/wiki/AES_key_schedule
    # generates round keys

    rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36, 0x6c]

    key = cipher_key.copy()
    key.transpose()
    W = [key[i] for i in range(4)]

    for i in range(4, 4*N + 4):

        new_word: np.array = np.copy(W[i - 1])
        if i % 4 == 0:
            # new block starts

            new_word = np.roll(new_word, -1)
            new_word = np.vectorize(lambda x: sbox[x])(new_word)

            new_word[0] ^= rcon[(i // 4) - 1] 
        
        # xor with first word from last block and add as new
        new_word ^= W[i - 4]

        W.append(new_word)

    keys = [State(matrix=np.array(W[4*i:4*i+4])) for i in range(N)]
    for key in keys:
        key.transpose()
    return keys
