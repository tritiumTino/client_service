import yaml

test_dict = {'one': ['one', 'two'], 'two': 2, 'three': {'€': 8364}}

with open('file.yaml', 'w') as f_yaml:
    yaml.dump(test_dict, f_yaml, default_flow_style=False, allow_unicode=True)
