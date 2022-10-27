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
        # close if parent thread (this) is being closed
        cls.app_thread.setDaemon(True)
        cls.app_thread.start()


    def setUp(self, flask_app):
        # Perform set up before each test, using client
        self.mysql.start()
        # read content of structure.sql and load it into mock
        self.execute_file('./sql/setup.sql')

    def tearDown(self, flask_app):
        # Perform tear down after each test, using client
        # drop all tables from mock
        self.execute_file('./sql/teardown.sql')

    @classmethod
    def tearDownClass(cls):
        # stops the mysqld instance, kills the pid, drops the tmp directory
        cls.mysql.stop()
        

############################################################################################################
########################################## INTEGRATION TESTS ###############################################
############################################################################################################

    def test_connection(self, client):
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

    def test_invlaid_url(self, client):
        # Act
        url = "http://localhost:5000/invalid_url"
        rv = requests.get(url)
        response = rv.json()['message']

        # Assert
        self.assert_equal(rv.status_code, 404)
        self.assert_equal(response, f"Record not found: {url}")

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
        
            [1, 'John Doe']
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
                [1, 93, 1],
                [1, 67, 4],
                [1, 81, 3]
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
        rv = client.get('/user/1/movies')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            [
                [1, 'The Dark Knight', 'Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets.', 85, 3716, 2008],
                [4, 'The Godfather', 'Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone barely survives an attempt on his life, his youngest son, Michael steps in to take care.', 87, 2184, 1972],
            [3, 'Pulp Fiction', 'A burger-loving hit man, his philosophical partner, a drug-addled gangsters moll and a washed-up boxer converge in this sprawling, comedic crime caper. Their adventures unfurl in three stories that ingeniously trip back and forth in time.', 84, 6213, 1994],
            ])

    def test_get_movies_of_user_not_found(self, client):
        # Act
        rv = client.get('/user/99/movies')
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
        self.assertEqual(response, 
        [
            [1, 'The Dark Knight', 'Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets.', 85, 3716, 2008],
            [2, 'The Matrix', 'Set in the 22nd century, The Matrix tells the story of a computer hacker who joins a group of underground insurgents fighting the vast and powerful computers who now rule the earth.', 82, 2179, 1999],
            [3, 'Pulp Fiction', 'A burger-loving hit man, his philosophical partner, a drug-addled gangsters moll and a washed-up boxer converge in this sprawling, comedic crime caper. Their adventures unfurl in three stories that ingeniously trip back and forth in time.', 84, 6213, 1994],
            [4, 'The Godfather', 'Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone barely survives an attempt on his life, his youngest son, Michael steps in to take care.', 87, 2184, 1972],
            [5, 'Scarface', 'After getting a green card in exchange for assassinating a Cuban government official, Tony Montana stakes a claim on the drug trade in Miami. Viciously murdering anyone who stands in his way, Tony eventually becomes the biggest drug lord in the state.', 81, 987, 1983] 
        ])
    
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
            []
        )

    def test_get_movies_with_title(self, client):
        # Act
        rv = client.get('/movie?title=Knight')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
            [
                [1, 'The Dark Knight', 'Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets.', 85, 3716, 2008]
                
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
            [
            [4, 'The Godfather', 'Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone barely survives an attempt on his life, his youngest son, Michael steps in to take care.', 87, 2184, 1972],
                [1, 'The Dark Knight', 'Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets.', 85, 3716, 2008]
            ]
        )

    def test_create_movie_success(self, client):
        # Act
        rv = client.post('/movie', json={'title': 'Harry Potter', 'description': 'Wizards messing around', 'vote_average': 85, 'vote_count': 120, 'year': 2000})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
        
            [6]
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
        
            [1, 'Harry Potter', 'Wizards messing around', 85, 120, 2000]
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

    def test_delete_movie_unsuccesful(self, client):
        # Act
        rv = client.delete('/movie/99')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(response, 'Movie not found.'
        )

    def test_create_rating_success(self, client):
        # Act
        rv = client.post('/rating', json={'user_id': 3, 'movie_id': 1, 'rating': 83})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
        
            [1]
        )

    def test_create_rating_unsuccesful(self, client):
        # Act
        rv = client.post('/rating', json={})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(response, 'Invalid request. User_id, movie_id and rating are required.'
        )

    def test_update_rating_success(self, client):
        # Act
        rv = client.put('/rating/1', json={'user_id': 3, 'movie_id': 1, 'rating': 83})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(response, 
        
            [1, 3, 1, 83]
        )

    def test_update_rating_unsuccesful(self, client):
        # Act
        rv = client.put('/rating/1', json={})
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(response, 'Invalid request. User_id, movie_id and rating are required.'
        )

    def test_delete_rating_success(self, client):
        # Act
        rv = client.delete('/rating/1')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 200)

    def test_delete_rating_unsuccesful(self, client):
        # Act
        rv = client.delete('/rating/99')
        response = rv.get_json()

        # Assert
        self.assertEqual(rv.status_code, 404)
        self.assertEqual(response, 'Rating not found.'
        )


if __name__ == '__main__':
    unittest.main()
