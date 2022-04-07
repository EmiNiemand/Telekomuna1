import bitarray as bitarray
import numpy as np
from bitarray import *

# const values
parity_bits = 8
bits_in_byte = 8

# Matrix which satisfies two conditions:
# 1. No repeating rows
# 2. Each row has unique sum of all of its values
H_matrix = np.array((
    [1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]
))

#===============Main functions=====================

# read bytes and encode each byte
# using encode_byte()
def encode_bytes(bytes):
    result = bytearray()
    for byte in bytes:
        bits = byte_to_bits(byte)
        encoded_byte = bytearray(encode_byte(bits).tobytes())
        result.append(encoded_byte[0])
        result.append(encoded_byte[1])

    return result


# read every second byte
def decode_bytes(encoded_bytes):
    return encoded_bytes[::2]


# read every second byte info byte and guard byte
# combine them together to bitarray
# correct corrupted bit/bits in bitarray using correct_byte() function
# and append these bytes at the end of a result
def correct_bytes(encoded_bytes):
    result = bytearray()
    for i in range(0, len(encoded_bytes), 2):
        byte_as_bits = encoded_byte_to_bits(encoded_bytes[i], encoded_bytes[i + 1])
        corrected_byte = bytearray(correct_byte(byte_as_bits).tobytes())

        result.append(corrected_byte[0])
        result.append(corrected_byte[1])

    return result


#==============Other functions====================

# convert byte to bits
def byte_to_bits(byte):
    result = ''
    for i in range(bits_in_byte):
        result += str(byte % 2)
        byte = int(np.floor(byte / 2))
    return bitarray(result[::-1])


# convert two bytes to a single bitarray
def encoded_byte_to_bits(byte_one, byte_two):
    byte_as_bits = bitarray()

    bits_one = byte_to_bits(byte_one)
    bits_two = byte_to_bits(byte_two)

    for j in range(bits_in_byte):
        byte_as_bits.append(bits_one[j])

    for j in range(parity_bits):
        byte_as_bits.append(bits_two[j])

    return byte_as_bits


# encode byte by adding parity byte:
# get(number of parity bits) rows of H_matrix = new_matrix
# new_array is just np.array of bits(converted from bitarray)
# calculate parity byte:
#   (new_matrix * T(new_array)) % 2
# and finally combine original byte and parity byte
def encode_byte(one_byte):
    new_matrix = H_matrix[0:, :parity_bits]
    new_array = bitarray_to_nparray(one_byte)

    parity_byte = new_matrix.dot(new_array.T)
    parity_byte %= 2

    encoded_byte = bitarray()
    for i in range(bits_in_byte):
        encoded_byte.append(new_array[i])

    for i in range(parity_bits):
        encoded_byte.append(parity_byte[i])

    return encoded_byte

# convert bitarray to np.array containing int from bits
def bitarray_to_nparray(bits):
    result = []
    for i in range(len(bits)):
        result.append(int(bits[i]))

    return np.array(result)


# calculate: H_matrix * np.array(coded_byte) % 2
# return column equal
# to one of the matrix_H column (if there is corrupted bit/bits)
# otherwise return column of 0s
def calculate_syndrome(coded_byte):
    syndrome_array = bitarray_to_nparray(coded_byte)
    result: np.ndarray = H_matrix.dot(syndrome_array)

    return result % 2

# returns true if syndrome is column of 0s
def check_coded_byte(syndrome):
    return np.count_nonzero(syndrome) == 0


# calculates syndrome and then
# tries to correct it
def correct_byte(coded_byte):
    syndrome = calculate_syndrome(coded_byte)
    coded_byte_copy = coded_byte.copy()

    if check_coded_byte(syndrome):
        return coded_byte
    if correct_one_bit(coded_byte_copy, syndrome) is not False:
        return correct_one_bit(coded_byte_copy, syndrome)
    if correct_two_bits(coded_byte_copy, syndrome) is not False:
        return correct_two_bits(coded_byte_copy, syndrome)
    else:
        print("Something went wrong")
        raise Exception

# checks if syndrome has
# corresponding column in transformed H_matrix
# if so, change bit on position equal to column number
# else return false (probably there are more corrupted bits)
def correct_one_bit(coded_byte, syndrome):
    i = 0
    for column in H_matrix.T:
        # check if corresponding values of syndrome and column
        # are equal to each other
        if np.equal(syndrome, column).all():
            if coded_byte[i] == 1:
                coded_byte[i] = 0
            else:
                coded_byte[i] = 1
            return coded_byte
        i += i

    return False


# function sums two different rows of H_matrix,
# then sum % 2 to make sure there's only bit values
# if the syndrome and sum are identical,
#  bits of coded_byte get corrected on positions of column1 and column2
# else return false (probably there are more corrupted bits)
def correct_two_bits(coded_byte, syndrome):
    i = 0
    j = 0
    for column1 in H_matrix.T:
        for column2 in H_matrix.T:
            if i == j:
                continue

            sum = (column1 + column2) % 2
            if np.equal(sum, syndrome).all():
                if coded_byte[i] == 1:
                    coded_byte[i] = 0
                else:
                    coded_byte[i] = 1
                if coded_byte[j] == 1:
                    coded_byte[j] = 0
                else:
                    coded_byte[j] = 1
                return coded_byte
            j += 1
        i += 1
        j = 0

    return False

