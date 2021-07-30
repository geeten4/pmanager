import numpy as np
from aes.s_box import sbox, inv_sbox
from aes.multiplication import m2, m3, m9, m11, m13, m14

class State:
    # represents 128bit numbers as np.array (4x4)

    value: np.array

    def __init__(self, matrix: np.array = None, number: str = None, horizontal = False):
        
        if matrix is not None:
            self.value = matrix
        
        else:
            # int v hexu konvertovat na 4x4 matici
            sh_arr = [number[i: i+2] for i in range(0, len(number), 2)]
            sh_arr = list(map(lambda x: int(x, 16), sh_arr))
            sh_matrix = np.fromiter(sh_arr, dtype=np.ubyte).reshape((4, 4))

            self.value = sh_matrix if horizontal else sh_matrix.T
    
    def sub_bytes(self):
        sbox_map = np.vectorize(lambda x: sbox[x])
        self.value = sbox_map(self.value)

    def inv_sub_bytes(self):
        inv_sbox_map = np.vectorize(lambda x: inv_sbox[x])
        self.value = inv_sbox_map(self.value)
    
    def shift_rows(self):
        matrix = self.value
        for i in range(4):
            matrix[i] = np.roll(self.value[i], -i)
        self.value = matrix
    
    def inv_shift_rows(self):
        matrix = self.value
        for i in range(4):
            matrix[i] = np.roll(self.value[i], i)
        self.value = matrix
    
    def mix_columns(self):
        zeros = np.zeros((4, 4), dtype=np.ubyte)
        w = self.value
        for c in range(4):
            zeros[0][c] = m2[w[0][c]] ^ m3[w[1][c]] ^ w[2][c]     ^ w[3][c]
            zeros[1][c] = w[0][c]     ^ m2[w[1][c]] ^ m3[w[2][c]] ^ w[3][c]
            zeros[2][c] = w[0][c]     ^ w[1][c]     ^ m2[w[2][c]] ^ m3[w[3][c]]
            zeros[3][c] = m3[w[0][c]] ^ w[1][c]     ^ w[2][c]     ^ m2[w[3][c]]
        
        self.value = zeros
    
    def inv_mix_columns(self):
        zeros = np.zeros((4, 4), dtype=np.ubyte)
        w = self.value
        for c in range(4):
            zeros[0][c] = m14[w[0][c]] ^ m11[w[1][c]] ^ m13[w[2][c]] ^ m9[w[3][c]]
            zeros[1][c] = m9[w[0][c]]  ^ m14[w[1][c]] ^ m11[w[2][c]] ^ m13[w[3][c]]
            zeros[2][c] = m13[w[0][c]] ^ m9[w[1][c]]  ^ m14[w[2][c]] ^ m11[w[3][c]]
            zeros[3][c] = m11[w[0][c]] ^ m13[w[1][c]] ^ m9[w[2][c]]  ^ m14[w[3][c]]
        
        self.value = zeros

    def transpose(self):
        self.value = self.value.T
    
    def copy(self):
        return State(self.value)
    
    def to_hex_str(self):
        s = []
        for i in range(4):
            for j in range(4):
                char = str(hex(self.value[j][i])).replace('0x', '')
                if len(char) == 1:
                    char = '0' + char
                s.append(char)
        return ''.join(s)

    def __xor__(self, other):
        return State(matrix=self.value ^ other.value)
    
    def __getitem__(self, key: int):
        return self.value[key]

    def __str__(self):
        s = ''
        for line in self.value:
            line_chars = []
            for number in line:
                char = str(hex(number)).replace('0x', '')
                if len(char) == 1:
                    char = '0' + char
                line_chars.append(char)
            s += ' '.join(line_chars) + '\n'
        return s
