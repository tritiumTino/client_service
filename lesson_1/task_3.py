def check_byte_convert(word_list):
    for word in word_list:
        try:
            word.encode('ascii')
        except UnicodeEncodeError:
            print(f'word "{word}" cannot be represented in bytes')


def main():
    word_list = ('attribute', 'класс', 'функция', 'type')
    check_byte_convert(word_list)


if __name__ == '__main__':
    main()
