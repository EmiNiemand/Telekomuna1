import corrector as c

# read file as bytes and encode
# save result to a encoded.txt file
def encode():
    input_file = open("message.txt", 'rb').read()
    encoded_file = c.encode_bytes(bytearray(input_file))
    output_file = open("encoded.txt", 'wb')
    output_file.write(encoded_file)

# read file as bytes, correct bits and decode
# save result to a decoded.txt file
def decode():
    input_file = open("encoded.txt", 'rb').read()
    encoded_file = c.correct_bytes(bytearray(input_file))
    encoded_file = c.decode_bytes(encoded_file)
    output_file = open("decoded.txt", 'wb')
    output_file.write(encoded_file)