
import unittest
import flask_unittest
import main
import testing.mysqld
from sqlalchemy import create_engine

# prevent generating brand new db every time.  Speeds up tests.
MYSQLD_FACTORY = testing.mysqld.MysqldFactory(cache_initialized_db=True, port=7531)

class MainTests(flask_unittest.ClientTestCase):
    # Assign the `Flask` app object
    app = main.app

    def execute_file(self, filename):
        with open(filename, 'r') as f:
            for statement in f.read().split(';'):
                if len(statement.strip()) > 0:
                    self.db_conn.execute(statement + ';')

    @classmethod
    def setUpClass(cls):
        cls.mysql = MYSQLD_FACTORY()
        cls.db_conn = create_engine(cls.mysql.url()).connect()

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
        cls.mysql.stop()  # from source code we can see this kills the pid
        

    def test_404(self, client):
        rv = client.get('/does_not_exist')
        self.assertEqual(rv.status_code, 404)

    def test_foo_with_client(self, client):
        rv = client.get('/user')
        self.assertInResponse(bytes('{"message":"Hello, World!"}', 'utf8'), rv)
        #self.assertInResponse(rv, 'hello world!')


if __name__ == '__main__':
    unittest.main()
