import hashlib, os
from urllib.parse import unquote

import requests
from jsonpath_ng import parse


def get_query_param(parsed_query, name, default=''):
    q = parsed_query
    if name in q and len(q[name]):
        return unquote(q[name].pop()) if len(q[name]) == 1 else unquote(q[name])
    else:
        return default


def load_file(filepath):
    with open(filepath, 'rb') as file:
        return file.read()


def get_existing_file(filepath):
    if os.path.exists(filepath):
        return load_file(filepath)
    return None


def get_filepath(filename):
    return f"tmp/{filename}"


def get_filename(params):
    return f"{get_hash_key(params)}.png"


def get_hash_key(key_items):
    hash_obj = hashlib.sha256("|".join(map(lambda s: str(s), key_items)).encode('utf-8'))
    return hash_obj.hexdigest()


def get_json_value(url, json_path):
    json_obj = requests.get(url).json()
    jsonpath_expr = parse(json_path)
    return ", ".join([match.value for match in jsonpath_expr.find(json_obj)])
