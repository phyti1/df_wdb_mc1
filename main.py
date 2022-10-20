import pymysql
from app import app
import connector
from flask import jsonify
from flask import flash, request
import uuid
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy


mysql = None

def init_flask(conn_str):
    global mysql
    db = SQLAlchemy()
    app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
    mysql = create_engine(conn_str).connect()
    
    db.init_app(app)




############################################################################################################
############################################# USER #########################################################
############################################################################################################

# get all users
@app.route('/user', methods=['GET'])
def get_user():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT user_id, name FROM user")
        users = cursor.fetchall()
        cursor.close() 
        conn.close() 
        respone = jsonify(users)
        respone.status_code = 200
        return respone
    except Exception as e:
        raise e


# create a new user
@app.route('/user', methods=['POST'])
def create_user():
    try:        
        _json = request.json
        _name = _json['name']
        _password = _json['password']
        user_id = str(uuid.uuid4())
        if _name and _password and request.method == 'POST':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)		
            sqlQuery = "INSERT INTO user(name, password, user_id) VALUES(%s, %s, %s)"
            bindData = (_name, _password, user_id)            
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            response = jsonify(user_id)
            response.status_code = 200
            return response
        else:
            return showMessage()
    except Exception as e:
        raise e
    finally:
        cursor.close() 
        conn.close()

# update a user
@app.route('/user/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        _json = request.json
        _name = _json['name']
        _password = _json['password']
        if _name and _password and user_id and request.method == 'PUT':
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "UPDATE user SET name=%s, password =%s WHERE user_id=%s"
            bindData = (_name, _password, user_id)
            cursor.execute(sqlQuery, bindData)
            user = cursor.fetchall()
            conn.commit()
            respone = jsonify(user)
            respone.status_code = 200
            return respone
        else:
            return showMessage()
    except Exception as e:
        raise e
    finally:
        cursor.close() 
        conn.close()

# delete a user
@app.route('/user/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM user WHERE user_id =%s", (user_id))
		conn.commit()
		respone = jsonify('User deleted successfully!')
		respone.status_code = 200
		return respone
	except Exception as e:
		raise e
	finally:
		cursor.close() 
		conn.close()

       
@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone


if __name__ == "__main__":
    host, user, password = connector.get_credentials()
    init_flask(f"mysql+pymysql://{user}:{password}@{host}/wdb?charset=utf8mb4")
    app.run()
