import json


def load_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data


def convert_json_to_obj(json_obj):
    return json.loads(json_obj)


def convert_obj_to_json(obj):
    return json.dumps(obj)


def print_json(json_data):
    json_object = json.loads(json_data)
    pair = json_object.items()
    for key, value in pair:
        print("{} = {}".format(key, value))


def sort_indent(data):
    return json.dumps(data, indent=4, sort_keys=True)


def remove_feature_json(json_data, features_to_remove):
    for key, value in enumerate(json_data['states']):
        del value['area_codes']
    return json_data


def write_json(json_d):
    print(json_d)
    with open('./data/data.json', 'w') as outfile:
        json.dump(json_d, outfile,indent=4,sort_keys=True)


if __name__ == '__main__':
    # json_obj = '{"Name ": " David", "Class ": "I", "Age": 6}'
    data_json = load_json('./data/states.json')
    # print(data_json)
    # py_obj = convert_json_to_obj(json_obj)
    # print(py_obj)
    # json_data = convert_obj_to_json(py_obj)
    # print(json_data)
    # print_json(json_data)
    # print(sort_indent(py_obj))
    print(data_json)
    d = remove_feature_json(data_json, ['area_code'])
    print(d)
    write_json(d)
