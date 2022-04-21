import random

import bitarray as bitarray
import numpy as np
from bitarray import *

# stałe
number_of_parity_bits = 8
number_of_bits_in_byte = 8

# macierz, która spełnia dwa warunki:
# 1. nie ma powtarzających się wierszy
# 2. żaden wiersz nie jest równy sumie dwóch innych wierszy
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


class CorrectingError(Exception):
    pass


# czyta bajty i szyfruje każdy z nich (encode_byte)
def encodeBytes(byte_array: bytearray):
    result = bytearray()
    for byte in byte_array:
        byte_as_bit_array = byteToBitArray(byte)
        encoded_byte = bytearray(encodeByte(byte_as_bit_array).tobytes())
        result.append(encoded_byte[0])
        result.append(encoded_byte[1])
    return result


# czyta co drugi bajt
def decodeBytes(encoded_byte_array: bytearray):
    return encoded_byte_array[::2]


# odczyta dwa bajty - bajt informacji i bajt chroniący
# łączy to w bitarray
# poprawi uszkodzone bity w bitarray (correct_byte)
# i doda je na koniec wyniku
def correctBytes(encoded_byte_array: bytearray):
    result = bytearray()
    for i in range(0, len(encoded_byte_array), 2):
        byte_as_bit_array = encodedByteToBitArray(encoded_byte_array[i], encoded_byte_array[i + 1])
        corrected_byte = bytearray(correctByte(byte_as_bit_array).tobytes())

        result.append(corrected_byte[0])
        result.append(corrected_byte[1])
    return result


# zmieni bajty na bity
def byteToBitArray(byte: int) -> bitarray:
    result = ''
    for i in range(number_of_bits_in_byte):
        result += str(byte % 2)
        byte = int(np.floor(byte / 2))
    return bitarray(result[::-1])


# zmieni dwa bajty na jeden bitarray
def encodedByteToBitArray(byte_one, byte_two) -> bitarray:
    byte_as_bit_array = bitarray()

    for j in range(number_of_bits_in_byte):
        byte_as_bit_array.append(byteToBitArray(byte_one)[j])

    for j in range(number_of_parity_bits):
        byte_as_bit_array.append(byteToBitArray(byte_two)[j])

    return byte_as_bit_array


# zaszyfruje bajty poprzez dodanie bitu parzystości:
# weźmie tyle wierszyz H_matrix ile jest bitów parzystości
# i stworzy z nich nową macierz
# new_array jest tablicą bitów(zmienionych z tablicy bitów)
# liczy bit parzystości:
#   (new_matrix * T(new_array)) % 2
# na koniec łączy oryginalny bajt z bitem parzystości
def encodeByte(one_byte: bitarray) -> bitarray:
    hamming_matrix = H_matrix[0:, :number_of_parity_bits]
    word_array = bitArrayToVector(one_byte)

    parity_byte = hamming_matrix.dot(word_array.T)
    parity_byte %= 2

    encoded_byte = bitarray()
    for i in range(number_of_bits_in_byte):
        encoded_byte.append(word_array[i])

    for i in range(number_of_parity_bits):
        encoded_byte.append(parity_byte[i])

    return encoded_byte


# zmieni bitarray na np.array który będzie zawierał int zamiast bitów
def bitArrayToVector(bits: bitarray) -> np.ndarray:
    result = []
    for i in range(len(bits)):
        result.append(int(bits[i]))
    return np.array(result)


def calculateError(coded_byte) -> np.ndarray:
    error_array = bitArrayToVector(coded_byte)
    result: np.ndarray = H_matrix.dot(error_array)
    return result % 2


# zwraca prawdę jeśli error_matrix jest kolumną zer
def checkCodedByte(error_array: np.ndarray) -> bool:
    return np.count_nonzero(error_array) == 0


# liczy: H_matrix * np.array(coded_byte) % 2
# zwróci kolumnę równą jednej z macierzy matrix_H
# jeśli jest jakiś uszkodzony bit
# jeśli nie, to zwraca kolumnę zer
# potem próbuje poprawić error_matrix
def correctByte(coded_byte: bitarray):
    error_array = calculateError(coded_byte)
    coded_byte_copy = coded_byte.copy()

    if checkCodedByte(error_array):
        return coded_byte

    try:
        return tryCorrectOneBit(coded_byte_copy, error_array)
    except CorrectingError:
        pass
    try:
        return tryCorrectTwoBits(coded_byte_copy, error_array)
    except CorrectingError:
        raise CorrectingError()


# sprawdza czy error_matrix ma odpowiadającą kolumnę w
# transponowanej macierzy H_matrix
# jeśli tak jest, to zmini bit na pozycji równej numerowi kolumniy
# jeśli nie, to zwróci fałsz, co będzie oznaczało, że
# prawdopodobnie jest więcej uszkodzonych bitów
def tryCorrectOneBit(coded_byte: bitarray, error_array: np.ndarray):
    i = 0
    for column in H_matrix.T:
        # check if corresponding values of syndrome and column
        # are equal to each other
        if np.equal(error_array, column).all():
            coded_byte[i] ^= 1
            return coded_byte
        i += i

    raise CorrectingError()


# dodaje dwa wiersze H_matrix, potem wykonuje sum % 2
# żeby upewnić się, że występują tylko wartości bitowe
# jeśli error_matrix i suma sa takie same,
# bity w coded_byte są poprawione na pozycjach column1 i column2
# inaczej zwróci fałsz (prawdopodobnie jest więcej uszkodzonych bitów)
def tryCorrectTwoBits(coded_byte: bitarray, error_array: np.ndarray):
    i = 0
    j = 0
    for column in H_matrix.T:
        for column2 in H_matrix.T:
            if i == j:
                continue

            sum_of_two_columns = (column + column2) % 2
            if np.equal(sum_of_two_columns, error_array).all():
                coded_byte[i] ^= 1
                coded_byte[j] ^= 1
                return coded_byte
            j += 1
        i += 1
        j = 0

    raise CorrectingError()


# zwraca pierwsze 8 bitów arraya
def decodeByte(coded_byte: bitarray) -> bitarray:
    return coded_byte[:8]
