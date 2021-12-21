import json


def write_order_to_json(item, quantity, price, buyer, date):
    with open('orders.json') as orders:
        orders_dict = json.load(orders)
    orders_dict['orders'].append(
        {
            'item': item,
            'quantity': quantity,
            'price': price,
            'buyer': buyer,
            'date': date
        }
    )
    with open('orders.json', 'w') as orders:
        json.dump(orders_dict, orders, indent='\t')


def main():
    write_order_to_json('plate', 3, 2100.50, 'tritium', '2020-12-21')


if __name__ == '__main__':
    main()
