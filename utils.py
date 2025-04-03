def create_key(dic, key_name):
    if key_name not in dic:
        dic[key_name] = {}
        return True
    return False #이미 존재