def encode_decode(word_list):
    for word in word_list:
        word_bytes = word.encode("utf-8")
        print(f'{word_bytes}: {word_bytes.decode("utf-8")}')


def main():
    word_list = ('разработка', 'администрирование', 'protocol', 'standard')
    encode_decode(word_list)


if __name__ == '__main__':
    main()
