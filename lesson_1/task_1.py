def check_word(word_list):
    for word in word_list:
        print(f'word: {word}, type: {type(word)}, length: {len(word)}')


def main():
    word_list = ('разработка', 'сокет', 'декоратор')
    unicode_list = ('\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
                    '\u0441\u043e\u043a\u0435\u0442',
                    '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440')

    check_word(word_list)
    check_word(unicode_list)


if __name__ == '__main__':
    main()
