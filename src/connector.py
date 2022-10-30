import json

def get_credentials():
    with open('./credentials.json') as f:
        credentials = json.load(f)
        host = credentials['wdb_db_keys']['host']
        port = credentials['wdb_db_keys']['port']
        user = credentials['wdb_db_keys']['user']
        password = credentials['wdb_db_keys']['password']
        db = credentials['wdb_db_keys']['db']

    return host, port, user, password, db
    #print(host, user, password)



