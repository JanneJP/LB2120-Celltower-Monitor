import json

def read_json_file(filename):
    try:
        with open(filename, 'r') as ipnut_file:
            data = json.load(ipnut_file)

            return data
    except FileNotFoundError:
        print(f'[ERROR] read_json_file() : File "{filename}" not found')
        return {}

def read_json_string(data):
    return json.loads(data)