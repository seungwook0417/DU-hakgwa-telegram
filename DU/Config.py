import json

def get_config():
    return json.load(open("config.json", 'r', encoding="utf-8"))

def get_hakgwa():
    return json.load(open("hakgwa.json", 'r', encoding="utf-8"))

def get_user():
    return json.load(open("user.json", 'r', encoding="utf-8"))