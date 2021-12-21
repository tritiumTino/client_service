import csv
import re


producer_template = r'Изготовитель системы:\s+\w+'
os_name_template = r'Название ОС:\s+\w+'
code_template = r'Код продукта:\s+[-\w]+'
os_type_template = r'Тип системы:\s+[-\w]+\s\w+'
os_prod_list, os_name_list, os_code_list, os_type_list = [], [], [], []


def get_data_from_file(f_txt):
    with open(f_txt) as f_obj:
        f_text = f_obj.read()
        os_prod_list.append(re.search(producer_template, f_text).group(0).split(':')[1].strip())
        os_name_list.append(re.search(os_name_template, f_text).group(0).split(':')[1].strip())
        os_code_list.append(re.search(code_template, f_text).group(0).split(':')[1].strip())
        os_type_list.append(re.search(os_type_template, f_text).group(0).split(':')[1].strip())


def get_data():
    for i in range(len(os_prod_list)):
        yield os_prod_list[i], os_name_list[i], os_code_list[i], os_type_list[i]


def write_data_to_csv():
    headers = ('Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы')
    with open('main_data.csv', 'w') as csv_f:
        writer = csv.writer(csv_f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        writer.writerows(get_data())


def main():
    file_list = ('info_1.txt', 'info_2.txt', 'info_3.txt',)
    for file_txt in file_list:
        get_data_from_file(file_txt)
    write_data_to_csv()


if __name__ == '__main__':
    main()
