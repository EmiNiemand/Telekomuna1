import random
import bitarray as bitarray
import numpy as np
from bitarray import *

# constant values, provides better readability
parity_bits = 8
bits_in_byte = 8

# Matrix which satisfies two conditions:
# 1. No repeating rows
# 2. Each row has unique sum of all of its values
Hamming_matrix = np.array((
    [1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]
))

class CorrectionError(Exception):
    pass

#===============Main functions=====================

# read bytes and encode each byte
# using encode_byte()
# and append first two bits
def encode_bytes(bytes: bytearray):
    result = bytearray()
    for byte in bytes:
        bits = byte_to_bits(byte)
        encoded_byte = bytearray(encode_byte(bits).tobytes())
        result.append(encoded_byte[0])
        result.append(encoded_byte[1])
    return result


# read every second byte from encoded_bytes
def decode_bytes(encoded_bytes: bytearray):
    return encoded_bytes[::2]


# read every second byte from encoded_bytes
# combine info byte and guard byte together as bitarray
# correct resulting bitarray via correct_byte()
# and append first two bits at the end
def correct_bytes(encoded_bytes: bytearray):
    result = bytearray()
    for i in range(0, len(encoded_bytes), 2):
        byte_as_bits = encoded_byte_to_bits(encoded_bytes[i], encoded_bytes[i + 1])
        corrected_byte = bytearray(correct_byte(byte_as_bits).tobytes())

        result.append(corrected_byte[0])
        result.append(corrected_byte[1])
    return result


#==============Other functions====================

# convert byte to bits
def byte_to_bits(byte: int) -> bitarray:
    result = ''
    for i in range(bits_in_byte):
        result += str(byte % 2)
        byte = int(np.floor(byte / 2))
    return bitarray(result[::-1])


# convert two bytes to a single bitarray
#   [a, b, c], [d, e, f] -> [a, b, c, d, e, f]
def encoded_byte_to_bits(byte_one, byte_two) -> bitarray:
    byte_as_bits = bitarray()

    for j in range(bits_in_byte):
        byte_as_bits.append(byte_to_bits(byte_one)[j])

    for j in range(parity_bits):
        byte_as_bits.append(byte_to_bits(byte_two)[j])

    return byte_as_bits


# encode byte by adding parity byte:
# slice hamming_matrix to have number of rows equal to number_of_parity_bits
# calculate parity byte:
#   (hamming_matrix * T(word_array)) % 2
# and finally combine information and parity byte:
#   [a, b, c], [d, e, f] -> [a, b, c, d, e, f]
def encode_byte(one_byte: bitarray) -> bitarray:
    hamming_matrix = Hamming_matrix[0:, :parity_bits]
    word_array = bitarray_to_nparray(one_byte)

    parity_byte = hamming_matrix.dot(word_array.T)
    parity_byte %= 2

    encoded_byte = bitarray()
    for i in range(bits_in_byte):
        encoded_byte.append(word_array[i])

    for i in range(parity_bits):
        encoded_byte.append(parity_byte[i])

    return encoded_byte

# convert bitarray to np.array containing int from bits
def bitarray_to_nparray(bits: bitarray) -> np.ndarray:
    result = []
    for i in range(len(bits)):
        result.append(int(bits[i]))
    return np.array(result)


# calculate: matrix_H * np.array(coded_byte) % 2
# returns column that should be equal
# to one of the matrix_H column
def calculate_syndrome(coded_byte) -> np.ndarray:
    syndrome_array = bitarray_to_nparray(coded_byte)
    result: np.ndarray = Hamming_matrix.dot(syndrome_array)
    return result % 2

# returns true if there are no 1's in array
def check_coded_byte(syndrome: np.ndarray) -> bool:
    return np.count_nonzero(syndrome) == 0


# calculates coded_byte syndrome and then
# tries to correct it
def correct_byte(coded_byte: bitarray):
    syndrome = calculate_syndrome(coded_byte)
    coded_byte_copy = coded_byte.copy()

    if check_coded_byte(syndrome):
        return coded_byte

    try:
        return try_correct_one_bit(coded_byte_copy, syndrome)
    except CorrectionError:
        pass
    try:
        return try_correct_two_bits(coded_byte_copy, syndrome)
    except CorrectionError:
        raise CorrectionError()


# checks if syndrome array has
# corresponding column in transformed matrix_H
# if so, flip the bit on position equal to column number
# else raise error (there was more than one corrupted bit)
def try_correct_one_bit(coded_byte: bitarray, syndrome: np.ndarray):
    i = 0
    for column in Hamming_matrix.T:
        # check if corresponding values of syndrome and column
        # are equal to each other
        if np.equal(syndrome, column).all():
            coded_byte[i] ^= 1
            return coded_byte
        i += i

    raise CorrectionError()


# function sums two different rows of matrix_H,
#  making sure each element has either 0 or 1 as value
# if the syndrom and sum are identical, bits of coded_byte
#  on positions of rows in sum are corrected
# else raise error (there was more than two corrupted bits)
def try_correct_two_bits(coded_byte: bitarray, syndrome: np.ndarray):
    i = 0
    j = 0
    for column in Hamming_matrix.T:
        for column2 in Hamming_matrix.T:
            if i == j:
                continue

            sum_of_two_columns = (column + column2) % 2
            if np.equal(sum_of_two_columns, syndrome).all():
                coded_byte[i] ^= 1
                coded_byte[j] ^= 1
                return coded_byte
            j += 1
        i += 1
        j = 0

    raise CorrectionError()

# return first 8 bits of bitarray
def decode_byte(coded_byte: bitarray) -> bitarray:
    return coded_byte[:8]

