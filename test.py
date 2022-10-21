import os
import unittest
import flask_unittest
import main
import testing.mysqld

# prevent generating brand new db every time.  Speeds up tests.
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
############################################# UNIT TESTS ###################################################
############################################################################################################

    def test_404(self, client):
        # test 404
        rv = client.get('/does_not_exist')
        self.assertEqual(rv.status_code, 404)


    def test_foo_with_client(self, client):
        rv = client.get('/user')
        self.assertEqual(rv.status_code, 200)
        response = rv.get_json()
        self.assertEqual(response, 
        [
            [1, 'Hanspeter Peterhans'], 
            [2, 'Werner Würschtli'], 
            [3, 'Chantal Schläppi']
        ])


if __name__ == '__main__':
    unittest.main()
