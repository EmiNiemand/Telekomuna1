import corrector as c


# read file as bytes and encode
# save result to encoded.txt file
def encode():
    input_file = open("message.txt", 'rb').read()
    encoded_file = c.encode_bytes(bytearray(input_file))
    output_file = open("encoded.txt", 'wb')
    output_file.write(encoded_file)


# read file as bytes, correct bits and decode
# save result to decoded.txt file
def decode():
    input_file = open("encoded.txt", 'rb').read()
    encoded_file = c.correct_bytes(bytearray(input_file))
    encoded_file = c.decode_bytes(encoded_file)
    output_file = open("decoded.txt", 'wb')
    output_file.write(encoded_file)


# INFO
# Input file name must be "message.txt"
# Output file name after encoding is "encoded.txt";
# Output file name after correction and decoding is "decoded.txt"
def main():
    in_string = str(input("Write '1' to encode or '2' to decode."))
    if in_string == '1':
        encode()

    elif in_string == '2':
        decode()


if __name__ == "__main__":
    main()
