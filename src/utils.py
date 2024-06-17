import re
import json

def clean_string(s):
    if isinstance(s, str):
        return re.sub("[^A-Za-z0-9 ]+", '', s)
    else:
        return s


def re_braces(s):
    if isinstance(s, str):
        return re.sub("[\(\[].*?[\)\]]", "", s)
    else:
        return s


def name_filter(s):
    if isinstance(s, str):
        # Adds space to words that
        s = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', s)
        if 'Mary' not in s and ' State' not in s:
            s = s.replace(' St', ' State')
        if 'University' not in s:
            s = s.replace('Univ', 'University')
        if 'zz' in s or 'zzz' in s or 'zzzz' in s:
            s = s.replace('zzzz', '').replace('zzz', '').replace('zz', '')
        s = clean_string(s)
        s = re_braces(s)
        s = str(s)
        s = s.replace(' ', '').lower()
        return s
    else:
        return s

def get_json_file(path):
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except Exception as e:
        return {}

# Function to save sport league file
def put_json_file(path, data):
    with open(path, 'w') as file:
        json.dump(data, file, indent=4)