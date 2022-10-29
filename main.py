import pymysql
from app import app
import connector
from flask import jsonify
from flask import flash, request
from flaskext.mysql import MySQL


mysql = None

def init_flask(host, port, user, password, db):
    global mysql

    mysql = MySQL()
    app.config['MYSQL_DATABASE_HOST'] = host
    app.config['MYSQL_DATABASE_PORT'] = port
    app.config['MYSQL_DATABASE_USER'] = user
    app.config['MYSQL_DATABASE_PASSWORD'] = password
    app.config['MYSQL_DATABASE_DB'] = db
    mysql.init_app(app)
    
    return mysql

@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    response = jsonify(message)
    response.status_code = 404
    return response


############################################################################################################
############################################# USER #########################################################
############################################################################################################

# get all users
@app.route('/user', methods=['GET'])
def get_users():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name FROM user")
        users = cursor.fetchall()
        response = jsonify(users)
        response.status_code = 200
        cursor.close() 
        conn.close() 
        return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response

# get a specific user
@app.route('/user/<string:user_id>', methods=['GET'])
def get_specific_user(user_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, name FROM user WHERE user_id = %s", (user_id))
        user = cursor.fetchone()
        response = jsonify(user)
        response.status_code = 200
        cursor.close()
        conn.close()
        return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response

# create a new user
@app.route('/user', methods=['POST'])
def create_user():
    try:
        _json = request.json
        if 'name' in _json:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "INSERT INTO user (name) VALUES(%s)"
            bindData = (_json['name'])
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            user_id = cursor.lastrowid
            response = jsonify(user_id)
            response.status_code = 200
            cursor.close()
            conn.close()
            return response
        else:
            response = jsonify('Invalid request. Name is required.')
            response.status_code = 400
            return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response

# update a user
@app.route('/user/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        _json = request.json
        if 'name' in _json:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "UPDATE user SET name = %s WHERE user_id = %s"
            bindData = (_json['name'], user_id)
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            response = jsonify('User updated successfully.')
            response.status_code = 200
            cursor.close()
            conn.close()
        else:
            response = jsonify('Invalid request. Name is required.')
            response.status_code = 400
        return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response

# delete a user
@app.route('/user/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE user_id =%s", (user_id))
        conn.commit()
        response = jsonify('User deleted successfully!')
        response.status_code = 200
        cursor.close()
        conn.close()
        return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response

# get ratings of a specific user
@app.route('/user/<string:user_id>/ratings', methods=['GET'])
def get_ratings_from_user(user_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rating_id, movie_id, rating FROM user_rating WHERE user_id = %s", (user_id))
        ratings = cursor.fetchall()
        response = jsonify(ratings)
        response.status_code = 200
        cursor.close()
        conn.close()
        return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response

# get all movies which a specific user rated
@app.route('/user/<string:user_id>/ratings/movies', methods=['GET'])
def get_movies_from_user(user_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT movie_id, title, description, vote_average, vote_count, year FROM TMDB_movie_infos WHERE movie_id IN (SELECT movie_id FROM user_rating WHERE user_id = %s)", (user_id))
        ratings = cursor.fetchall()
        response = jsonify(ratings)
        response.status_code = 200
        cursor.close()
        conn.close()
        return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response


############################################################################################################
############################################# MOVIE ########################################################
############################################################################################################

# get all movies matching params
@app.route('/movies', methods=['GET'])
def get_movies():
    try:
        args = request.args
        title = args.get('title')
        limit = args.get('limit')
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        sqlQuery = "SELECT movie_id, title, description, vote_average, vote_count, year FROM TMDB_movie_infos"
        bindData = []

        if title:
            sqlQuery += " WHERE title LIKE %s"
            bindData.append(title)

        if limit:
            sqlQuery += " LIMIT %s"
            bindData.append(limit)

        sqlQuery += " ORDER BY vote_average DESC"

        cursor.execute(sqlQuery, bindData)
        movies = cursor.fetchall()
        response = jsonify(movies)
        response.status_code = 200
        cursor.close()
        conn.close()
        return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response

# get a specific movie
@app.route('/movie/<string:movie_id>', methods=['GET'])
def get_specific_movie(movie_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT movie_id, title, description, vote_average, vote_count, year FROM TMDB_movie_infos WHERE movie_id = %s", (movie_id))
        movie = cursor.fetchone()
        response = jsonify(movie)
        response.status_code = 200
        cursor.close()
        conn.close()
        return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response

# create a new movie
@app.route('/movie', methods=['POST'])
def create_movie():
    try:
        _json = request.json
        if 'title' in _json and 'description' in _json and 'vote_average' in _json and 'vote_count' in _json and 'year' in _json:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "INSERT INTO TMDB_movie_infos (title, description, vote_average, vote_count, year) VALUES(%s)"
            bindData = (_json['title'], _json['description'], _json['vote_average'], _json['vote_count'], _json['year'])
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            movie_id = cursor.lastrowid
            response = jsonify(movie_id)
            response.status_code = 200
            cursor.close()
            conn.close()
            return response
        else:
            response = jsonify('Invalid request. Title, description, vote_average, vote_count and year are required.')
            response.status_code = 400
            return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response

# update a movie
@app.route('/movie/<string:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    try:
        _json = request.json
        if 'title' in _json and 'description' in _json and 'vote_average' in _json and 'vote_count' in _json and 'year' in _json:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "UPDATE TMDB_movie_infos SET title = %s, description = %s, vote_average = %s, vote_count = %s, year = %s WHERE movie_id = %s"
            bindData = (_json['title'], _json['description'], _json['vote_average'], _json['vote_count'], _json['year'], movie_id)
            cursor.execute(sqlQuery, bindData)
            user = cursor.fetchall()
            conn.commit()
            response = jsonify('Movie updated successfully.')
            response.status_code = 200
            cursor.close()
            conn.close()
            return response
        else:
            response = jsonify('Invalid request. Title, description, vote_average, vote_count and year are required.')
            response.status_code = 400
            return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response

# delete a movie
@app.route('/movie/<string:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM TMDB_movie_infos WHERE movie_id = %s", (movie_id))
        conn.commit()
        response = jsonify('Movie deleted successfully!')
        response.status_code = 200
        cursor.close()
        conn.close()
        return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response


############################################################################################################
############################################# RATING #######################################################
############################################################################################################

# create a rating
@app.route('/rating', methods=['POST'])
def create_rating():
    try:
        _json = request.json
        if 'user_id' in _json and 'movie_id' in _json and 'rating' in _json:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "INSERT INTO user_rating (user_id, movie_id, rating) VALUES(%s)"
            bindData = (_json['user_id'], _json['movie_id'], _json['rating'])
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            rating_id = cursor.lastrowid
            response = jsonify(rating_id)
            response.status_code = 200
            cursor.close()
            conn.close()
            return response
        else:
            response = jsonify('Invalid request. user_id, movie_id and rating are required.')
            response.status_code = 400
            return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response

# update a rating
@app.route('/rating/<string:rating_id>', methods=['PUT'])
def update_rating(rating_id):
    try:
        _json = request.json
        if 'user_id' in _json and 'movie_id' in _json and 'rating' in _json:
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            sqlQuery = "UPDATE user_rating SET user_id = %s, movie_id = %s, rating = %s WHERE rating_id = %s"
            bindData = (_json['user_id'], _json['movie_id'], _json['rating'], rating_id)
            cursor.execute(sqlQuery, bindData)
            conn.commit()
            response = jsonify('Rating updated successfully.')
            response.status_code = 200
            cursor.close()
            conn.close()
            return response
        else:
            response = jsonify('Invalid request. user_id, movie_id and rating are required.')
            response.status_code = 400
            return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response

# delete a rating
@app.route('/rating/<string:rating_id>', methods=['DELETE'])
def delete_rating(rating_id):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_rating WHERE rating_id = %s", (rating_id))
        conn.commit()
        response = jsonify('Rating deleted successfully!')
        response.status_code = 200
        cursor.close()
        conn.close()
        return response
    except Exception as e:
        response = jsonify(str(e))
        response.status_code = 400
        return response


if __name__ == "__main__":
    host, port, user, password, db = connector.get_credentials()
    init_flask(host, port, user, password, db)
    app.run()
