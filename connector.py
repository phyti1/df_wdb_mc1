from app import app
from flaskext.mysql import MySQL

import json
with open('./credentials.json') as f:
    credentials = json.load(f)
    host = credentials['wdb_db_keys']['host']
    user = credentials['wdb_db_keys']['user']
    password = credentials['wdb_db_keys']['password']

print(host, user, password)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = user
app.config['MYSQL_DATABASE_PASSWORD'] = password
app.config['MYSQL_DATABASE_DB'] = 'cds'
app.config['MYSQL_DATABASE_HOST'] = host
mysql.init_app(app)