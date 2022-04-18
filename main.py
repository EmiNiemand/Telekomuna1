import corrector as c


# wczytuje plik jako bajty i zakoduje
# zapisuje wynik do encoded.txt
def encode():
    input_file = open("message.txt", 'rb').read()
    encoded_file = c.encodeBytes(bytearray(input_file))
    output_file = open("encoded.txt", 'wb')
    output_file.write(encoded_file)


# wczytuje plik jako bajty, poprawia bity i dekoduje
# zapisuje wynik jako decoded,txt
def decode():
    input_file = open("encoded.txt", 'rb').read()
    encoded_file = c.correctBytes(bytearray(input_file))
    encoded_file = c.decodeBytes(encoded_file)
    output_file = open("decoded.txt", 'wb')
    output_file.write(encoded_file)


# plik wejściowy musi mieć nazwę "message.txt"
# po zakodowaniu plik wejściowy będzie miał nazwę "encoded.txt";
# po korekcji bitów i zdekodowaniu plik będzie miał nazwę "decoded.txt"
def main():
    in_string = str(input("Write '1' to encode or '2' to decode."))
    if in_string == '1':
        encode()

    elif in_string == '2':
        decode()


if __name__ == "__main__":
    main()
