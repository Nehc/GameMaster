import json
from vedis import Vedis

def get_current_state(user_id):
    with Vedis(f'./pl_data/{user_id}') as db:
        return db['state'].decode()

def get_db_fild(user_id, fild):
    with Vedis(f'./pl_data/{user_id}') as db:
        return db[fild].decode()

def set_db_fild(user_id, fild, value):
    with Vedis(f'./pl_data/{user_id}') as db:
        db[fild] = value

def get_db_list(user_id, fild):
    with Vedis(f'./pl_data/{user_id}') as db:
        try:
            return json.loads(db[fild].decode()) 
        except KeyError:  
            return []

def set_db_list(user_id, fild, value):
    with Vedis(f'./pl_data/{user_id}') as db:
        try:
            l =  json.loads(db[fild].decode()) 
            l[-1] = value
        except KeyError:  
            l = []; l.append(value)
        db[fild] = json.dumps(l)

def clr_db_list(user_id, fild, value=None):
    l = []
    if value: l.append(value)
    with Vedis(f'./pl_data/{user_id}') as db:
        db[fild] = json.dumps(l)

def app_db_list(user_id, fild, value):
    with Vedis(f'./pl_data/{user_id}') as db:
        try:
            l =  json.loads(db[fild].decode()) 
        except KeyError:  
            l = []
        l.append(value); db[fild] = json.dumps(l)