with open('test_file.txt') as f_obj:
    print(f'standard encoding: {f_obj.encoding}')

with open('test_file.txt', encoding='utf-8') as f_obj:
    for el_str in f_obj:
        print(el_str, end='')
