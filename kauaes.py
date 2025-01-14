
# Part of EE495 (EE494) Study of Block Ciphers
# Core AES implementaion
# Hesham T. Banafa

from collections import deque

import numpy as np

""" 
AES has the main componants
    - Pre-round transformation
    - Key expantion
    - Round
        - Subbytes
        - ShiftRows
        - MixColumns
        - AddRoundKey   
    - Round Nr 
        - All but MixColumns
"""

class InvalidKeyLength(RuntimeError): ...
class InvalidAESKey(RuntimeError): ...
class IncompleteBlock(RuntimeError): ...


class AESRound:
    
    in_block : list[list[bytes]]
    sub_bytes_state : list[list[bytes]]
    shift_rows_state : list[list[bytes]]
    mix_column_state : list[list[bytes]]
    add_round_key_state: list[list[bytes]]
    key_words : list[list[bytes]]

    def __init__(self, in_block, key_words):
        self.in_block = in_block
        self.key_words = key_words
    
    def set_subbytes_state(self, sub_bytes_state):
        self.sub_bytes_state = sub_bytes_state
    
    def set_shift_rows_state(self, shift_rows_state):
        self.shift_rows_state = shift_rows_state
    
    def set_mix_column_state(self, mix_column_state):
        self.mix_column_state = mix_column_state
    
    def set_add_round_key_state(self, add_round_key_state):
        self.add_round_key_state = add_round_key_state
    
class AES:

    __block_size_bits = 128
    __block_size_bytes = __block_size_bits / 8
    __block_size_words = __block_size_bits / 32

    __sub_bytes = [
        0x63,0x7C,0x77,0x7B,0xF2,0x6B,0x6F,0xC5,0x30,0x01,0x67,0x2B,0xFE,0xD7,0xAB,0x76,
        0xCA,0x82,0xC9,0x7D,0xFA,0x59,0x47,0xF0,0xAD,0xD4,0xA2,0xAF,0x9C,0xA4,0x72,0xC0,
        0xB7,0xFD,0x93,0x26,0x36,0x3F,0xF7,0xCC,0x34,0xA5,0xE5,0xF1,0x71,0xD8,0x31,0x15,
        0x04,0xC7,0x23,0xC3,0x18,0x96,0x05,0x9A,0x07,0x12,0x80,0xE2,0xEB,0x27,0xB2,0x75,
        0x09,0x83,0x2C,0x1A,0x1B,0x6E,0x5A,0xA0,0x52,0x3B,0xD6,0xB3,0x29,0xE3,0x2F,0x84,
        0x53,0xD1,0x00,0xED,0x20,0xFC,0xB1,0x5B,0x6A,0xCB,0xBE,0x39,0x4A,0x4C,0x58,0xCF,
        0xD0,0xEF,0xAA,0xFB,0x43,0x4D,0x33,0x85,0x45,0xF9,0x02,0x7F,0x50,0x3C,0x9F,0xA8,
        0x51,0xA3,0x40,0x8F,0x92,0x9D,0x38,0xF5,0xBC,0xB6,0xDA,0x21,0x10,0xFF,0xF3,0xD2,
        0xCD,0x0C,0x13,0xEC,0x5F,0x97,0x44,0x17,0xC4,0xA7,0x7E,0x3D,0x64,0x5D,0x19,0x73,
        0x60,0x81,0x4F,0xDC,0x22,0x2A,0x90,0x88,0x46,0xEE,0xB8,0x14,0xDE,0x5E,0x0B,0xDB,
        0xE0,0x32,0x3A,0x0A,0x49,0x06,0x24,0x5C,0xC2,0xD3,0xAC,0x62,0x91,0x95,0xE4,0x79,
        0xE7,0xCB,0x37,0x6D,0x8D,0xD5,0x4E,0xA9,0x6C,0x56,0xF4,0xEA,0x65,0x7A,0xAE,0x08,
        0xBA,0x78,0x25,0x2E,0x1C,0xA6,0xB4,0xC6,0xE8,0xDD,0x74,0x1F,0x4B,0xBD,0x8B,0x8A,
        0x70,0x3E,0xB5,0x66,0x48,0x03,0xF6,0x0E,0x61,0x35,0x57,0xB9,0x86,0xC1,0x1D,0x9E,
        0xE1,0xF8,0x98,0x11,0x69,0xD9,0x8E,0x94,0x9B,0x1E,0x87,0xE9,0xCE,0x55,0x28,0xDF,
        0x8C,0xA1,0x89,0x0D,0xBF,0xE6,0x42,0x68,0x41,0x99,0x2D,0x0F,0xB0,0x54,0xBB,0x16
    ]

    __isub_bytes = [
        0x52,0x09,0x6A,0xD5,0x30,0x36,0xA5,0x38,0xBF,0x40,0xA3,0x9E,0x81,0xF3,0xD7,0xFB,
        0x7C,0xE3,0x39,0x82,0x9B,0x2F,0xFF,0x87,0x34,0x8E,0x43,0x44,0xC4,0xDE,0xE9,0xCB,
        0x54,0x7B,0x94,0x32,0xA6,0xC2,0x23,0x3D,0xEE,0x4C,0x95,0x0B,0x42,0xFA,0xC3,0x4E,
        0x08,0x2E,0xA1,0x66,0x28,0xD9,0x24,0xB2,0x76,0x5B,0xA2,0x49,0x6D,0x8B,0xD1,0x25,
        0x72,0xF8,0xF6,0x64,0x86,0x68,0x98,0x16,0xD4,0xA4,0x5C,0xCC,0x5D,0x65,0xB6,0x92,
        0x6C,0x70,0x48,0x50,0xFD,0xED,0xB9,0xDA,0x5E,0x15,0x46,0x57,0xA7,0x8D,0x9D,0x84,
        0x90,0xD8,0xAB,0x00,0x8C,0xBC,0xD3,0x0A,0xF7,0xE4,0x58,0x05,0xB8,0xB3,0x45,0x06,
        0xD0,0x2C,0x1E,0x8F,0xCA,0x3F,0x0F,0x02,0xC1,0xAF,0xBD,0x03,0x01,0x13,0x8A,0x6B,
        0x3A,0x91,0x11,0x41,0x4F,0x67,0xDC,0xEA,0x97,0xF2,0xCF,0xCE,0xF0,0xB4,0xE6,0x73,
        0x96,0xAC,0x74,0x22,0xE7,0xAD,0x35,0x85,0xE2,0xF9,0x37,0xE8,0x1C,0x75,0xDF,0x6E,
        0x47,0xF1,0x1A,0x71,0x1D,0x29,0xC5,0x89,0x6F,0xB7,0x62,0x0E,0xAA,0x18,0xBE,0x1B,
        0xFC,0x56,0x3E,0x4B,0xC6,0xD2,0x79,0x20,0x9A,0xDB,0xC0,0xFE,0x78,0xCD,0x5A,0xF4,
        0x1F,0xDD,0xA8,0x33,0x88,0x07,0xC7,0x31,0xB1,0x12,0x10,0x59,0x27,0x80,0xEC,0x5F,
        0x60,0x51,0x7F,0xA9,0x19,0xB5,0x4A,0x0D,0x2D,0xE5,0x7A,0x9F,0x93,0xC9,0x9C,0xEF,
        0xA0,0xE0,0x3B,0x4D,0xAE,0x2A,0xF5,0xB0,0xC8,0xEB,0xBB,0x3C,0x83,0x53,0x99,0x61,
        0x17,0x2B,0x04,0x7E,0xBA,0x77,0xD6,0x26,0xE1,0x69,0x14,0x63,0x55,0x21,0x0C,0x7D,
    ]

    # Define this as 2D array, to later use with numpy.
    __mix_column_mat = np.array([
        [0x02,0x03,0x01,0x01],
        [0x01,0x02,0x03,0x01],
        [0x01,0x01,0x02,0x03],
        [0x03,0x01,0x01,0x02]
    ])

    __imix_column_mat = np.array([
        [0x0E,0x0B,0x0D,0x09],
        [0x09,0x0E,0x0B,0x0D],
        [0x0D,0x09,0x0E,0x0B],
        [0x0B,0x0D,0x09,0x0E]
    ])

    __rcon_aes128 = [0x01000000,0x02000000,0x04000000,0x08000000,0x10000000,
                     0x20000000,0x40000000,0x80000000,0x1B000000,0x36000000]
    
    # Finite Field for MixCol
    __gfp2 = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40,
              42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72, 74, 76, 78, 80,
              82, 84, 86, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110, 112, 114, 116,
               118, 120, 122, 124, 126, 128, 130, 132, 134, 136, 138, 140, 142, 144, 146, 148,
                150, 152, 154, 156, 158, 160, 162, 164, 166, 168, 170, 172, 174, 176, 178, 180,
                 182, 184, 186, 188, 190, 192, 194, 196, 198, 200, 202, 204, 206, 208, 210, 212,
                  214, 216, 218, 220, 222, 224, 226, 228, 230, 232, 234, 236, 238, 240, 242, 244,
                   246, 248, 250, 252, 254, 27, 25, 31, 29, 19, 17, 23, 21, 11, 9, 15, 13, 3, 1,
                    7, 5, 59, 57, 63, 61, 51, 49, 55, 53, 43, 41, 47, 45, 35, 33, 39, 37, 91, 89,
                     95, 93, 83, 81, 87, 85, 75, 73, 79, 77, 67, 65, 71, 69, 123, 121, 127, 125,
                      115, 113, 119, 117, 107, 105, 111, 109, 99, 97, 103, 101, 155, 153, 159,
                       157, 147, 145, 151, 149, 139, 137, 143, 141, 131, 129, 135, 133, 187, 185,
                        191, 189, 179, 177, 183, 181, 171, 169, 175, 173, 163, 161, 167, 165,
                         219, 217, 223, 221, 211, 209, 215, 213, 203, 201, 207, 205, 195,
                          193, 199, 197, 251, 249, 255, 253, 243, 241, 247, 245, 235, 233,
                           239, 237, 227, 225, 231, 229]

    __gfp3 = [0, 3, 6, 5, 12, 15, 10, 9, 24, 27, 30, 29, 20, 23, 18, 17, 48, 51, 54, 53, 60,
     63, 58, 57, 40, 43, 46, 45, 36, 39, 34, 33, 96, 99, 102, 101, 108, 111, 106, 105, 120,
      123, 126, 125, 116, 119, 114, 113, 80, 83, 86, 85, 92, 95, 90, 89, 72, 75, 78, 77, 68,
       71, 66, 65, 192, 195, 198, 197, 204, 207, 202, 201, 216, 219, 222, 221, 212, 215, 210,
        209, 240, 243, 246, 245, 252, 255, 250, 249, 232, 235, 238, 237, 228, 231, 226, 225,
         160, 163, 166, 165, 172, 175, 170, 169, 184, 187, 190, 189, 180, 183, 178, 177, 144,
          147, 150, 149, 156, 159, 154, 153, 136, 139, 142, 141, 132, 135, 130, 129, 155, 152,
           157, 158, 151, 148, 145, 146, 131, 128, 133, 134, 143, 140, 137, 138, 171, 168, 173,
            174, 167, 164, 161, 162, 179, 176, 181, 182, 191, 188, 185, 186, 251, 248, 253,
             254, 247, 244, 241, 242, 227, 224, 229, 230, 239, 236, 233, 234, 203, 200, 205,
              206, 199, 196, 193, 194, 211, 208, 213, 214, 223, 220, 217, 218, 91, 88, 93, 94,
               87, 84, 81, 82, 67, 64, 69, 70, 79, 76, 73, 74, 107, 104, 109, 110, 103, 100,
                97, 98, 115, 112, 117, 118, 127, 124, 121, 122, 59, 56, 61, 62, 55, 52, 49,
                 50, 35, 32, 37, 38, 47, 44, 41, 42, 11, 8, 13, 14, 7, 4, 1, 2, 19, 16, 21,
                  22, 31, 28, 25, 26]

    __gfp9 = [0, 9, 18, 27, 36, 45, 54, 63, 72, 65, 90, 83, 108, 101, 126, 119, 144,
    153, 130, 139, 180, 189, 166, 175, 216, 209, 202, 195, 252, 245, 238, 231, 59, 50,
    41, 32, 31, 22, 13, 4, 115, 122, 97, 104, 87, 94, 69, 76, 171, 162, 185, 176, 143,
    134, 157, 148, 227, 234, 241, 248, 199, 206, 213, 220, 118, 127, 100, 109, 82, 91, 64,
    73, 62, 55, 44, 37, 26, 19, 8, 1, 230, 239, 244, 253, 194, 203, 208, 217, 174, 167,
    188, 181, 138, 131, 152, 145, 77, 68, 95, 86, 105, 96, 123, 114, 5, 12, 23, 30, 33, 40,
    51, 58, 221, 212, 207, 198, 249, 240, 235, 226, 149, 156, 135, 142, 177, 184, 163, 170,
    236, 229, 254, 247, 200, 193, 218, 211, 164, 173, 182, 191, 128, 137, 146, 155, 124, 117,
    110, 103, 88, 81, 74, 67, 52, 61, 38, 47, 16, 25, 2, 11, 215, 222, 197, 204, 243, 250, 225,
    232, 159, 150, 141, 132, 187, 178, 169, 160, 71, 78, 85, 92, 99, 106, 113, 120, 15, 6,
    29, 20, 43, 34, 57, 48, 154, 147, 136, 129, 190, 183, 172, 165, 210, 219, 192, 201, 246,
    255, 228, 237, 10, 3, 24, 17, 46, 39, 60, 53, 66, 75, 80, 89, 102, 111, 116, 125, 161, 168,
    179, 186, 133, 140, 151, 158, 233, 224, 251, 242, 205, 196, 223, 214, 49, 56, 35, 42, 21,
    28, 7, 14, 121, 112, 107, 98, 93, 84, 79, 70]

    __gfp11 = [0, 11, 22, 29, 44, 39, 58, 49, 88, 83, 78, 69, 116, 127, 98, 105, 176, 187, 166,
    173, 156, 151, 138, 129, 232, 227, 254, 245, 196, 207, 210, 217, 123, 112, 109, 102, 87, 92,
    65, 74, 35, 40, 53, 62, 15, 4, 25, 18, 203, 192, 221, 214, 231, 236, 241, 250, 147, 152,
    133, 142, 191, 180, 169, 162, 246, 253, 224, 235, 218, 209, 204, 199, 174, 165, 184, 179,
    130, 137, 148, 159, 70, 77, 80, 91, 106, 97, 124, 119, 30, 21, 8, 3, 50, 57, 36, 47, 141,
    134, 155, 144, 161, 170, 183, 188, 213, 222, 195, 200, 249, 242, 239, 228, 61, 54, 43, 32,
    17, 26, 7, 12, 101, 110, 115, 120, 73, 66, 95, 84, 247, 252, 225, 234, 219, 208, 205, 198,
    175, 164, 185, 178, 131, 136, 149, 158, 71, 76, 81, 90, 107, 96, 125, 118, 31, 20, 9, 2, 51,
    56, 37, 46, 140, 135, 154, 145, 160, 171, 182, 189, 212, 223, 194, 201, 248, 243, 238, 229,
    60, 55, 42, 33, 16, 27, 6, 13, 100, 111, 114, 121, 72, 67, 94, 85, 1, 10, 23, 28, 45, 38,
    59, 48, 89, 82, 79, 68, 117, 126, 99, 104, 177, 186, 167, 172, 157, 150, 139, 128, 233,
    226, 255, 244, 197, 206, 211, 216, 122, 113, 108, 103, 86, 93, 64, 75, 34, 41, 52, 63, 14,
    5, 24, 19, 202, 193, 220, 215, 230, 237, 240, 251, 146, 153, 132, 143, 190, 181, 168, 163]

    __gfp13 = [0, 13, 26, 23, 52, 57, 46, 35, 104, 101, 114, 127, 92, 81, 70, 75, 208, 221, 202,
    199, 228, 233, 254, 243, 184, 181, 162, 175, 140, 129, 150, 155, 187, 182, 161, 172, 143,
    130, 149, 152, 211, 222, 201, 196, 231, 234, 253, 240, 107, 102, 113, 124, 95, 82, 69, 72,
    3, 14, 25, 20, 55, 58, 45, 32, 109, 96, 119, 122, 89, 84, 67, 78, 5, 8, 31, 18, 49, 60,
    43, 38, 189, 176, 167, 170, 137, 132, 147, 158, 213, 216, 207, 194, 225, 236, 251, 246,
    214, 219, 204, 193, 226, 239, 248, 245, 190, 179, 164, 169, 138, 135, 144, 157, 6, 11,
    28, 17, 50, 63, 40, 37, 110, 99, 116, 121, 90, 87, 64, 77, 218, 215, 192, 205, 238, 227,
    244, 249, 178, 191, 168, 165, 134, 139, 156, 145, 10, 7, 16, 29, 62, 51, 36, 41, 98, 111,
    120, 117, 86, 91, 76, 65, 97, 108, 123, 118, 85, 88, 79, 66, 9, 4, 19, 30, 61, 48, 39, 42,
    177, 188, 171, 166, 133, 136, 159, 146, 217, 212, 195, 206, 237, 224, 247, 250, 183, 186,
    173, 160, 131, 142, 153, 148, 223, 210, 197, 200, 235, 230, 241, 252, 103, 106, 125, 112,
    83, 94, 73, 68, 15, 2, 21, 24, 59, 54, 33, 44, 12, 1, 22, 27, 56, 53, 34, 47, 100, 105,
    126, 115, 80, 93, 74, 71, 220, 209, 198, 203, 232, 229, 242, 255, 180, 185, 174, 163, 128,
    141, 154, 151]

    __gfp14 = [0, 14, 28, 18, 56, 54, 36, 42, 112, 126, 108, 98, 72, 70, 84, 90, 224, 238, 252,
    242, 216, 214, 196, 202, 144, 158, 140, 130, 168, 166, 180, 186, 219, 213, 199, 201, 227,
    237, 255, 241, 171, 165, 183, 185, 147, 157, 143, 129, 59, 53, 39, 41, 3, 13, 31, 17, 75,
    69, 87, 89, 115, 125, 111, 97, 173, 163, 177, 191, 149, 155, 137, 135, 221, 211, 193, 207,
    229, 235, 249, 247, 77, 67, 81, 95, 117, 123, 105, 103, 61, 51, 33, 47, 5, 11, 25, 23, 118,
    120, 106, 100, 78, 64, 82, 92, 6, 8, 26, 20, 62, 48, 34, 44, 150, 152, 138, 132, 174, 160,
    178, 188, 230, 232, 250, 244, 222, 208, 194, 204, 65, 79, 93, 83, 121, 119, 101, 107, 49,
    63, 45, 35, 9, 7, 21, 27, 161, 175, 189, 179, 153, 151, 133, 139, 209, 223, 205, 195, 233,
    231, 245, 251, 154, 148, 134, 136, 162, 172, 190, 176, 234, 228, 246, 248, 210, 220, 206,
    192, 122, 116, 102, 104, 66, 76, 94, 80, 10, 4, 22, 24, 50, 60, 46, 32, 236, 226, 240, 254,
    212, 218, 200, 198, 156, 146, 128, 142, 164, 170, 184, 182, 12, 2, 16, 30, 52, 58, 40, 38,
    124, 114, 96, 110, 68, 74, 88, 86, 55, 57, 43, 37, 15, 1, 19, 29, 71, 73, 91, 85, 127, 113,
    99, 109, 215, 217, 203, 197, 239, 225, 243, 253, 167, 169, 187, 181, 159, 145, 131, 141]

    __Rcon = [0, 1, 2, 4, 8, 16, 32, 64, 128, 27, 54, 108, 216, 171, 77, 154, 47, 94, 188, 99, 198, 151, 53, 106, 212, 179, 125, 250, 239, 197, 145, 57, 114, 228, 211, 189, 97, 194, 159, 37, 74, 148, 51, 102, 204, 131, 29, 58, 116, 232, 203, 141, 1, 2, 4, 8, 16, 32, 64, 128, 27, 54, 108, 216, 171, 77, 154, 47, 94, 188, 99, 198, 151, 53, 106, 212, 179, 125, 250, 239, 197, 145, 57, 114, 228, 211, 189, 97, 194, 159, 37, 74, 148, 51, 102, 204, 131, 29, 58, 116, 232, 203, 141, 1, 2, 4, 8, 16, 32, 64, 128, 27, 54, 108, 216, 171, 77, 154, 47, 94, 188, 99, 198, 151, 53, 106, 212, 179, 125, 250, 239, 197, 145, 57, 114, 228, 211, 189, 97, 194, 159, 37, 74, 148, 51, 102, 204, 131, 29, 58, 116, 232, 203, 141, 1, 2, 4, 8, 16, 32, 64, 128, 27, 54, 108, 216, 171, 77, 154, 47, 94, 188, 99, 198, 151, 53, 106, 212, 179, 125, 250, 239, 197, 145, 57, 114, 228, 211, 189, 97, 194, 159, 37, 74, 148, 51, 102, 204, 131, 29, 58, 116, 232, 203, 141, 1, 2, 4, 8, 16, 32, 64, 128, 27, 54, 108, 216, 171, 77, 154, 47, 94, 188, 99, 198, 151, 53, 106, 212, 179, 125, 250, 239, 197, 145, 57, 114, 228, 211, 189, 97, 194, 159, 37, 74, 148, 51, 102, 204, 131, 29, 58, 116, 232, 203, 141]


    def __init__(self, key: str, data: bytes):
        if not key: raise InvalidAESKey("Key is of type None")
        self.key = key
        self.prep_key()
        self.expanded_key = self.KeyExpantion()
        self.block = self.prep_block(data)
        self.input_block = self.block
        self.pre_round = None
        self.rounds_enc : list[AESRound] = None
        self.rounds_dec : list[AESRound] = None
    
    def __new_null_aes_block(self):
        return [[None for i in range(4)] for j in range(4)]
    
    def prep_block(self, data_block: bytes):
        if len(data_block) != 16:
            # We can add padding here
            raise IncompleteBlock(f'Supplied Block with size {len(data_block)}')
        prepped_block = list()
    
        for i in range(4):
            prepped_block.append(
                [data_block[j*4+i] for j in range(4)]
            )
        return prepped_block
    
    def prep_key(self):
        self.key = [[int(self.key[i*8+j*2:i*8+j*2+2], 16) 
                    for j in range(4)]
                    for i in range(4)]

    def print_block(self):
        for row in self.block:
            print('[', end='')
            for byte in row:
                print(f'{byte}'.center(4), end='')
            print(']')
    
    def get_state_as_hex_string(self):
        hex_out = ''
        for i in range(4):
            for j in range(4):
                t = '' + hex(self.block[j][i])[2:]
                if self.block[j][i] < 16:
                    t = '0' + t
                hex_out += t                    
        return hex_out
    
    def convert_block_to_hex_string(self, block):
        hex_out = ''
        for i in range(4):
            for j in range(4):
                t = '' + hex(block[j][i])[2:]
                if self.block[j][i] < 16:
                    t = '0' + t
                hex_out += t
        return hex_out

    def print_block_square(self, block, hex_out=False):
        if not block: print('None'); return
        for row in block:
            print('[', end='')
            for byte in row:
                byte_t = byte
                if hex_out: byte_t = hex(byte)
                print(f' {byte_t}'.center(4), end=' ')
            print(']')
    
    def print_summary(self):
        print('Pre Round Key Add')
        self.print_block_square(self.pre_round)
        for round_ in self.rounds:
            pass

    def RotWord(self, word: list[bytes]):
        word = deque(word)
        word.rotate(-1)
        return list(word)
    
    def SubWord(self, word: list[bytes]):
        new_word = list()
        for byte in word:
            subbed_byte = self.__sub_bytes[byte]
            new_word.append(subbed_byte)
        return new_word

    def KeyExpantion(self):
        w = []
        for word in self.key:
            w.append(word[:])
        i = 4

        while i < 44:
            temp = w[i-1][:]
            if i % 4 == 0:
                temp = self.SubWord(self.RotWord(temp))
                temp[0] ^= self.__Rcon[(i//4)]
            elif 4 > 6 and i % 4 == 4:
                temp = self.SubWord(temp)

            for j in range(len(temp)):
                temp[j] ^= w[i-4][j]

            w.append(temp[:])

            i += 1
        return w


    def Subbytes(self):
        updated_state = self.__new_null_aes_block()
        for i in range(4):
            for j in range(4):
                updated_state[i][j] = self.__sub_bytes[self.block[i][j]]
        self.block = updated_state
    
    def InvSubBytes(self):
        updated_state = self.__new_null_aes_block()
        for i in range(4):
            for j in range(4):
                updated_state[i][j] = self.__isub_bytes[self.block[i][j]]
        self.block = updated_state

    def ShiftRows(self):
        # Shift block rows left by the mag of it's vertical index
        for i in range(1,4):
            d = deque(self.block[i])
            d.rotate(-i)
            self.block[i] = list(d)
    
    def InvShiftRows(self):
        # Shift block rows left by the mag of it's vertical index
        for i in range(1,4):
            d = deque(self.block[i])
            d.rotate(i)
            self.block[i] = list(d)
    
    def AddRoundKey(self, key):
        updated_state = [[None for i in range(4)] for j in range(4)]

        for i in range(4):
            for j in range(4):
                #print(f'{self.key.master_key[i][j]} XOR {self.block[i][j]}')
                updated_state[i][j] = self.block[i][j] ^ key[i][j]
        self.block = updated_state

    def MixColumns(self):
        n = [word[:] for word in self.block]
        for i in range(4):
            n[i][0] = (self.__gfp2[self.block[i][0]] ^ self.__gfp3[self.block[i][1]]
                    ^ self.block[i][2] ^ self.block[i][3])
            n[i][1] = (self.block[i][0] ^ self.__gfp2[self.block[i][1]]
                    ^ self.__gfp3[self.block[i][2]] ^ self.block[i][3])
            n[i][2] = (self.block[i][0] ^ self.block[i][1]
                    ^ self.__gfp2[self.block[i][2]] ^ self.__gfp3[self.block[i][3]])
            n[i][3] = (self.__gfp3[self.block[i][0]] ^ self.block[i][1]
                    ^ self.block[i][2] ^ self.__gfp2[self.block[i][3]])
        self.block = n
    
    def InvMixColumns(self):
        n = [word[:] for word in self.block]
        for i in range(4):
            n[i][0] = (self.__gfp14[self.block[i][0]] ^ self.__gfp11[self.block[i][1]]
                    ^ self.__gfp13[self.block[i][2]] ^ self.__gfp9[self.block[i][3]])
            n[i][1] = (self.__gfp9[self.block[i][0]] ^ self.__gfp14[self.block[i][1]]
                    ^ self.__gfp11[self.block[i][2]] ^ self.__gfp13[self.block[i][3]])
            n[i][2] = (self.__gfp13[self.block[i][0]] ^ self.__gfp9[self.block[i][1]]
                    ^ self.__gfp14[self.block[i][2]] ^ self.__gfp11[self.block[i][3]])
            n[i][3] = (self.__gfp11[self.block[i][0]] ^ self.__gfp13[self.block[i][1]]
                    ^ self.__gfp9[self.block[i][2]] ^ self.__gfp14[self.block[i][3]])
        self.block = n


    def Encrypt(self):

        self.rounds_enc = list()
        # Pre round
        pre_round = AESRound(self.block, self.expanded_key[:4])
        self.AddRoundKey(self.expanded_key[:4])
        pre_round.set_add_round_key_state(self.block)
        self.rounds_enc.append(pre_round)
        self.pre_round = self.block

        for round_ in range(1, 10): # All except last round
            key = self.expanded_key[round_*4:(round_+1)*4]
            round_snapshot = AESRound(self.block, key)
            self.Subbytes()
            round_snapshot.set_subbytes_state(self.block)
            self.ShiftRows()
            round_snapshot.set_shift_rows_state(self.block)
            self.MixColumns()
            round_snapshot.set_mix_column_state(self.block)
            self.AddRoundKey(key)
            round_snapshot.set_add_round_key_state(self.block)
            self.rounds_enc.append(round_snapshot)
        key = self.expanded_key[40:44]
        round_snapshot = AESRound(self.block, key)
        self.Subbytes()
        round_snapshot.set_subbytes_state(self.block)
        self.ShiftRows()
        round_snapshot.set_shift_rows_state(self.block)
        self.AddRoundKey(key)
        round_snapshot.set_add_round_key_state(self.block)
        round_snapshot.set_mix_column_state(None)
        self.rounds_enc.append(round_snapshot)
    
    def Decrypt(self):
        self.rounds_dec = list()
        self.AddRoundKey(self.expanded_key[40:44])
        
        for round_ in range(9, 0, -1): # All but 'first' round
            key = self.expanded_key[round_*4:(round_+1)*4]
            self.InvShiftRows()
            self.InvSubBytes()
            self.AddRoundKey(key)
            self.InvMixColumns()
        
        self.InvShiftRows()
        self.InvSubBytes()
        self.AddRoundKey(self.expanded_key[:4])
        

def test():
    k = "ff000000ff00ff00000000ffff000000"
    a = AES(k, "ee495teachesusse".encode('ascii'))
    a.print_block()
    a.AddRoundKey(a.expanded_key[:4])
    print('\n')
    a.print_block()
    print('\n')
    a.Subbytes()
    a.print_block()
    print('\n')
    a.ShiftRows()
    a.print_block()
    print('\n')
    a.MixColumns()
    a.print_block()
    print('\n')
    a.AddRoundKey(a.expanded_key[4:8])
    a.print_block()
    exit(0)
    
def test2():
    k = "ff000000ff00ff00000000ffff000000"
    print(len(k))
    a = AES(k, "ee495teachesusse".encode('ascii'))
    print()
    a.print_block()
    a.Encrypt()
    print()
    a.print_block()
    a.Decrypt()
    print()
    a.print_block()
    print(a.get_state_as_hex_string().replace('0x',''))

if __name__ == '__main__':
    exit(test2())
