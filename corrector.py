import bitarray as bitarray
import numpy as np
from bitarray import *

# macierz, która spełnia dwa warunki:
# 1. nie ma powtarzających się wierszy
# 2. Każdy wiersz ma unikalną sumę wartości
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
        corrected_byte = bytearray(correct_byte(byte_as_bits).tobytes())

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


# zmieni bitarray na np.array który będzie zawierał int z bitów
def bitarrayToNparray(bits):
    result = []
    for i in range(len(bits)):
        result.append(int(bits[i]))

    return np.array(result)


# obliczy: H_matrix * np.array(coded_byte) % 2
# zwróci kolumnę równą jednej z macierzy matrix_H
# jeśli jest jakiś uszkodzony bit
# jeśli nie, to zwraca kolumnę zer
def calculateSyndrome(coded_byte):
    syndrome_array = bitarrayToNparray(coded_byte)
    result: np.ndarray = H_matrix.dot(syndrome_array)

    return result % 2


# zwraca prawdę jeśli syndrome jest kolumną zer
def checkCodedByte(syndrome):
    return np.count_nonzero(syndrome) == 0


# liczy syndrome i potem próbuje poprawić go
def correct_byte(coded_byte):
    syndrome = calculateSyndrome(coded_byte)
    coded_byte_copy = coded_byte.copy()

    if checkCodedByte(syndrome):
        return coded_byte
    if correctOneBit(coded_byte_copy, syndrome) is not False:
        return correctOneBit(coded_byte_copy, syndrome)
    if correctTwoBits(coded_byte_copy, syndrome) is not False:
        return correctTwoBits(coded_byte_copy, syndrome)
    else:
        print("Something went wrong")
        raise Exception


# sprawdza czy syndrome ma odpowiadającą kolumnę w
# transponowanej macierzy H_matrix
# jeśli tak jest, to zmini bit na pozycji równej numerowi kolumniy
# jeśli nie, to zwróci fałsz, co będzie oznaczało, że
# prawdopodobnie jest więcej uszkodzonych bitów
def correctOneBit(coded_byte, syndrome):
    i = 0
    for column in H_matrix.T:
        # sprawdź czy odpowiadające wartości z syndrome i kolumny
        # są równe
        if np.equal(syndrome, column).all():
            if coded_byte[i] == 1:
                coded_byte[i] = 0
            else:
                coded_byte[i] = 1
            return coded_byte
        i += i

    return False


# dodaje dwa wiersze H_matrix, potem wykonuje sum % 2
# żeby upewnić się, że występują tylko wartości bitowe
# jeśli syndrome i suma sa takie same,
# bity w coded_byte są poprawione na pozycjach column1 i column2
# inaczej zwróci fałsz (prawdopodobnie jest więcej uszkodzonych bitów)
def correctTwoBits(coded_byte, syndrome):
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
