import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, TestCase
from settings import database_url_tests

class TestCaseAssertion(unittest.TestCase):

    engine = create_engine(database_url_tests)
    Session = sessionmaker(bind=engine)
    session = Session()

    sc_event = {
        'event_type': 'SmartContract.Runtime.Log',
        'contract_hash': 'f3da12622e9bb2b3f367a650a81fd8c70b2eb495',
         'event_payload':
            {
                'type': 'String',
                'value': 'Contract was called'
            },
        'execution_success': True,
        'test_mode': False,
        'extra': {'network': 'testnet'}
    }

    def setUp(self):
        Base.metadata.create_all(self.engine)
        # connect to the database
        self.connection = self.engine.connect()

        # begin a non-ORM transaction
        self.trans = self.connection.begin()

        # bind an individual Session to the connection
        self.test_session = self.Session(bind=self.connection)

    def test_test_case_creation(self):
        # use the session in tests.
        test_case = TestCase(contract_hash='f3da12622e9bb2b3f367a650a81fd8c70b2eb495', transaction_hash='c33fd08be47a978778f1c7098804d8339ce6ec4002e8e7de580552785dca80f5' event_type='SmartContract.Runtime.Log', expected_payload_type='String', expected_payload_value='Contract was called')
        self.test_session.add(test_case)
        self.test_session.commit()
        t_case = self.test_session.query(TestCase).filter_by(contract_hash='f3da12622e9bb2b3f367a650a81fd8c70b2eb495', event_type='SmartContract.Runtime.Log').first()
        self.assertEqual(test_case, t_case)


    def tearDown(self):
        self.test_session.close()

        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        self.trans.rollback()

        # return connection to the Engine
        self.connection.close()
        Base.metadata.drop_all(self.engine)

if __name__ == '__main__':
    unittest.main()
