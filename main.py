import encode_decode as ed

# INFO
# Input file name must be "message.txt"
# Output file name after encoding is "encoded.txt";
# Output file name after correction and decoding is "decoded.txt"
def main():
        user = str(input("Write e to encode or d to decode."))
        if user == 'e':
            ed.encode()

        elif user == 'd':
            ed.decode()


if __name__ == "__main__":
    main()