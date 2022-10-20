import json

def get_credentials():
    with open('./credentials.json') as f:
        credentials = json.load(f)
        host = credentials['wdb_db_keys']['host']
        user = credentials['wdb_db_keys']['user']
        password = credentials['wdb_db_keys']['password']

    return host, user, password
    #print(host, user, password)



