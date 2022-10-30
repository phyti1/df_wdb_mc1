import os
import unittest
import flask_unittest
import main
import testing.mysqld
import requests
import threading

# prevent generating brand new db every time. Speeds up tests.
MYSQLD_FACTORY = testing.mysqld.MysqldFactory(cache_initialized_db=True, my_cnf={'port': 7531})

class MainTests(flask_unittest.ClientTestCase):
    # Assign the `Flask` app object
    app = main.app

    # execute multi line sql statement, for test setup and teardown
    def execute_file(self, filename):
        conn = self.db_conn.connect()
        
        with open(filename, 'r') as f:
            for statement in f.read().split(';'):
                if len(statement.strip()) > 0:
                    cursor = conn.cursor()
                    cursor.execute(statement + ';')
                    cursor.close()
        
        result = conn.commit()
        conn.close()

    @classmethod
    def setUpClass(cls):
        # initialize mock database
        cls.mysql = MYSQLD_FACTORY()
        # create connection to mock database
        cls.db_conn = main.init_flask('127.0.0.1', cls.mysql.my_cnf['port'], cls.mysql.settings['user'], cls.mysql.settings['passwd'], 'test')
        
        # setup webserver for integration tests
        cls.app_thread = threading.Thread(target=lambda: cls.app.run(debug=True, use_reloader=False))
        # configure to close if parent thread (this) is being closed
        cls.app_thread.setDaemon(True)
        # start webserver in background
        cls.app_thread.start()


    def setUp(self, flask_app):
        # Perform set up before each test, using client
        self.mysql.start()
        # read content of structure.sql and load it into mock
        self.execute_file('./src/sql/setup.sql')

    def tearDown(self, flask_app):
        # Perform tear down after each test, using client
        # drop all tables from mock db in correct order to not violate foreign key constraints
        self.execute_file('./src/sql/teardown.sql')

    @classmethod
    def tearDownClass(cls):
        # stops the mysqld instance, kills the pid, drops the tmp directory
        cls.mysql.stop()
        

############################################################################################################
########################################## INTEGRATION TESTS ###############################################
############################################################################################################

    def test_get_all_users_integration(self, client):
        # Act
        rv = requests.get("http://localhost:5000/user")
        response = rv.json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
        [
            [1, 'Hanspeter Peterhans'], 
            [2, 'Werner Würschtli'], 
            [3, 'Chantal Schläppi']
        ])

    def test_get_specific_user_not_found_integration(self, client):
        # Act
        rv = requests.get("http://localhost:5000/user/99")
        response = rv.json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, None)

    def test_404_integration(self, client):
        # Act
        rv = requests.get("http://localhost:5000/does_not_exist")
        response = rv.json()

        # Assert
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(response, 
        {
            'message': 'Record not found: http://localhost:5000/does_not_exist', 
            'status': 404
        })

############################################################################################################
############################################# UNIT TESTS ###################################################
############################################################################################################

    def test_404(self, client):
        # Act
        rv = client.get('/does_not_exist')

        # Assert
        self.assertEqual(rv.status_code, 404)

############################################################################################################
################################################# USER #####################################################
############################################################################################################

    def test_get_all_users(self, client):
        # Act
        rv = client.get('/user')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
        [
            [1, 'Hanspeter Peterhans'], 
            [2, 'Werner Würschtli'], 
            [3, 'Chantal Schläppi']
        ])


    def test_get_specific_user_success(self, client):
        # Act
        rv = client.get('/user/1')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            [1, 'Hanspeter Peterhans']
        )


    def test_get_specific_user_not_found(self, client):
        # Act
        rv = client.get('/user/99')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            None
        )

    def test_create_user_success(self, client):
        # Act
        rv = client.post('/user', json={'name': 'John Doe'})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            4
        )

    def test_create_user_unsuccesful(self, client):
        # Act
        rv = client.post('/user', json={})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(response, 'Invalid request. Name is required.'
        )

    def test_update_user_success(self, client):
        # Act
        rv = client.put('/user/1', json={'name': 'John Doe'})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
        
            'User updated successfully.'
        )

    def test_update_user_unsuccesful(self, client):
        # Act
        rv = client.put('/user/1', json={})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(response, 'Invalid request. Name is required.'
        )

    def test_delete_user_success(self, client):
        # Act
        rv = client.delete('/user/1')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)    
        
        
    def test_get_ratings_of_user_success(self, client):
        # Act
        rv = client.get('/user/1/ratings')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            [
                [1, 1, 93.0], 
                [1, 4, 67.0]
            ]
        )

    def test_get_ratings_of_user_not_found(self, client):
        # Act
        rv = client.get('/user/99/ratings')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            []
        )

    def test_get_movies_of_user_success(self, client):
        # Act
        rv = client.get('/user/1/ratings/movies')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            [
                [1, 'The Dark Knight', 'Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets.', 85, 3716, 2008],
                [4, 'The Godfather', 'Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone barely survives an attempt on his life, his youngest son, Michael steps in to take care.', 87, 2184, 1972],
            ])

    def test_get_movies_of_user_not_found(self, client):
        # Act
        rv = client.get('/user/99/ratings/movies')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            []
        )

############################################################################################################
############################################### MOVIES #####################################################
############################################################################################################

    def test_get_all_movies(self, client):
        # Act
        rv = client.get('/movie')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(len(response), 5)
    
    def test_get_specific_movie_success(self, client):
        # Act
        rv = client.get('/movie/1')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            [1, 'The Dark Knight', 'Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets.', 85, 3716, 2008]
        )

    def test_get_specific_movie_not_found(self, client):
        # Act
        rv = client.get('/movie/99')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            None
        )

    def test_get_movies_with_title(self, client):
        # Act
        rv = client.get('/movie?title=Knight')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)

        self.assertEqual(response, 
            [
                {'description': 'Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets.', 'movie_id': 1, 'title': 'The Dark Knight', 'vote_average': 85.0, 'vote_count': 3716, 'year': 2008}                
            ]
        )

    def test_get_movies_with_title_not_found(self, client):
        # Act
        rv = client.get('/movie?title=NotFound')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            []
        )

    def test_get_movies_with_limit(self, client):
        # Act
        rv = client.get('/movie?limit=2')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            [{'description': 'Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone barely survives an attempt on his life, his youngest son, Michael steps in to take care.', 'movie_id': 4, 'title': 'The Godfather', 'vote_average': 87.0, 'vote_count': 2184, 'year': 1972}, {'description': 'Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets.', 'movie_id': 1, 'title': 'The Dark Knight', 'vote_average': 85.0, 'vote_count': 3716, 'year': 2008}]  
        )

    def test_create_movie_success(self, client):
        # Act
        rv = client.post('/movie', json={'title': 'Harry Potter', 'description': 'Wizards messing around', 'vote_average': 85, 'vote_count': 120, 'year': 2000})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            6
        )

    def test_create_movie_unsuccesful(self, client):
        # Act
        rv = client.post('/movie', json={})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(response, 'Invalid request. Title, description, vote_average, vote_count and year are required.'
        )

    def test_update_movie_success(self, client):
        # Act
        rv = client.put('/movie/1', json={'title': 'Harry Potter', 'description': 'Wizards messing around', 'vote_average': 85, 'vote_count': 120, 'year': 2000})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            'Movie updated successfully.'
        )

    def test_update_movie_unsuccesful(self, client):
        # Act
        rv = client.put('/movie/1', json={})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(response, 'Invalid request. Title, description, vote_average, vote_count and year are required.'
        )

    def test_delete_movie_success(self, client):
        # Act
        rv = client.delete('/movie/1')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)


############################################################################################################
############################################### RATINGS ####################################################
############################################################################################################

    def test_create_rating_success(self, client):
        # Act
        rv = client.post('/rating', json={'user_id': 3, 'movie_id': 1, 'rating': 83})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            7
        )

    def test_create_rating_unsuccesful(self, client):
        # Act
        rv = client.post('/rating', json={})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(response, 'Invalid request. user_id, movie_id and rating are required.'
        )

    def test_update_rating_success(self, client):
        # Act
        rv = client.put('/rating/1', json={'user_id': 3, 'movie_id': 1, 'rating': 83})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
        
            'Rating updated successfully.'
        )

    def test_update_rating_unsuccesful(self, client):
        # Act
        rv = client.put('/rating/1', json={})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(response, 'Invalid request. user_id, movie_id and rating are required.'
        )

    def test_delete_rating_success(self, client):
        # Act
        rv = client.delete('/rating/1')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()
