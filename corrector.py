import bitarray as bitarray
import numpy as np
from bitarray import *

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


# czyta bajty i szyfruje każdy z nich (encode_byte)
def encodeBytes(bytes):
    result = bytearray()
    for byte in bytes:
        bits = byteToBits(byte)
        encoded_byte = bytearray(encodeByte(bits).tobytes())
        result.append(encoded_byte[0])
        result.append(encoded_byte[1])

    return result


# czyta co drugi bajt
def decodeBytes(encoded_bytes):
    return encoded_bytes[::2]


# odczyta dwa bajty - bajt informacji i bajt chroniący
# łączy to w bitarray
# poprawi uszkodzone bity w bitarray (correct_byte)
# i doda je na koniec wyniku
def correctBytes(encoded_bytes):
    result = bytearray()
    for i in range(0, len(encoded_bytes), 2):
        byte_as_bits = encodedByteToBits(encoded_bytes[i], encoded_bytes[i + 1])
        corrected_byte = bytearray(correctByte(byte_as_bits).tobytes())

        result.append(corrected_byte[0])
        result.append(corrected_byte[1])

    return result


# zmieni bajty na bity
def byteToBits(byte):
    result = ''
    for i in range(8):
        result += str(byte % 2)
        byte = int(np.floor(byte / 2))
    return bitarray(result[::-1])


# zmieni dwa bajty na jeden bitarray
def encodedByteToBits(byte_one, byte_two):
    byte_as_bits = bitarray()

    bits_one = byteToBits(byte_one)
    bits_two = byteToBits(byte_two)

    for j in range(8):
        byte_as_bits.append(bits_one[j])

    for j in range(8):
        byte_as_bits.append(bits_two[j])

    return byte_as_bits


# zaszyfruje bajty poprzez dodanie bitu parzystości:
# weźmie tyle wierszyz H_matrix ile jest bitów parzystości
# i stworzy z nich nową macierz
# new_array jest tablicą bitów(zmienionych z tablicy bitów)
# liczy bit parzystości:
#   (new_matrix * T(new_array)) % 2
# na koniec łączy oryginalny bajt z bitem parzystości
def encodeByte(one_byte):
    new_matrix = H_matrix[0:, :8]
    new_array = bitarrayToNparray(one_byte)

    parity_byte = new_matrix.dot(new_array.T)
    parity_byte %= 2

    encoded_byte = bitarray()
    for i in range(8):
        encoded_byte.append(new_array[i])

    for i in range(8):
        encoded_byte.append(parity_byte[i])

    return encoded_byte


# zmieni bitarray na np.array który będzie zawierał int zamiast bitów
def bitarrayToNparray(bits):
    result = []
    for i in range(len(bits)):
        result.append(int(bits[i]))

    return np.array(result)


# zwraca prawdę jeśli error_matrix jest kolumną zer
def checkCodedByte(error_matrix):
    return np.count_nonzero(error_matrix) == 0


# liczy: H_matrix * np.array(coded_byte) % 2
# zwróci kolumnę równą jednej z macierzy matrix_H
# jeśli jest jakiś uszkodzony bit
# jeśli nie, to zwraca kolumnę zer
# potem próbuje poprawić error_matrix
def correctByte(coded_byte):
    error_array = bitarrayToNparray(coded_byte)
    error_matrix: np.ndarray = H_matrix.dot(error_array) % 2

    coded_byte_copy = coded_byte.copy()

    if checkCodedByte(error_matrix):
        return coded_byte
    if correctOneBit(coded_byte_copy, error_matrix) is not False:
        return correctOneBit(coded_byte_copy, error_matrix)
    if correctTwoBits(coded_byte_copy, error_matrix) is not False:
        return correctTwoBits(coded_byte_copy, error_matrix)
    else:
        print("Something went wrong")
        raise Exception


# sprawdza czy error_matrix ma odpowiadającą kolumnę w
# transponowanej macierzy H_matrix
# jeśli tak jest, to zmini bit na pozycji równej numerowi kolumniy
# jeśli nie, to zwróci fałsz, co będzie oznaczało, że
# prawdopodobnie jest więcej uszkodzonych bitów
def correctOneBit(coded_byte, error_matrix):
    i = 0
    for column in H_matrix.T:
        # sprawdź czy odpowiadające wartości z error_matrix i kolumny
        # są równe
        if np.equal(error_matrix, column).all():
            if coded_byte[i] == 1:
                coded_byte[i] = 0
            else:
                coded_byte[i] = 1
            return coded_byte
        i += i

    return False


# dodaje dwa wiersze H_matrix, potem wykonuje sum % 2
# żeby upewnić się, że występują tylko wartości bitowe
# jeśli error_matrix i suma sa takie same,
# bity w coded_byte są poprawione na pozycjach column1 i column2
# inaczej zwróci fałsz (prawdopodobnie jest więcej uszkodzonych bitów)
def correctTwoBits(coded_byte, error_matrix):
    i = 0
    j = 0
    for column1 in H_matrix.T:
        for column2 in H_matrix.T:
            if i == j:
                continue

            sum = (column1 + column2) % 2
            if np.equal(sum, error_matrix).all():
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
