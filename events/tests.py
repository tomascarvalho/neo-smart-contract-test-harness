import unittest
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, TestCase
from settings import database_url_tests
from tasks import handle_event

class TestCaseAssertion(unittest.TestCase):
    # uses test database
    engine = create_engine(database_url_tests)
    Session = sessionmaker(bind=engine)
    session = Session()

    # skeleton to be used in the tests   
    generic_sc_event = {
        'event_type': '',
        'contract_hash': '',
        'block_number': 12592,

        'tx_hash': '',
         'event_payload':
            {
                'type': '',
                'value': ''
            },
        'execution_success': True,
        'test_mode': False,
        'extra': {'network': 'privnet'}
    }

    def setUp(self):
        """
        setUp is called when tests start to setup the database
        """
        Base.metadata.create_all(self.engine)
        # connect to the database
        self.connection = self.engine.connect()

        # begin a non-ORM transaction
        self.trans = self.connection.begin()

        # bind an individual Session to the connection
        self.test_session = self.Session(bind=self.connection)

    def test_test_case_creation(self):
        # directly create test into the database
        test_case = TestCase(contract_hash='f3da12622e9bb2b3f367a650a81fd8c70b2eb495', 
                transaction_hash='c33fd08be47a978778f1c7098804d8339ce6ec4002e8e7de580552785dca80f5', 
                event_type='SmartContract.Runtime.Log', 
                expected_payload_type='String', 
                expected_payload_value='Contract was called',
                active= True
            )
        self.test_session.add(test_case)
        self.test_session.commit()
        t_case = self.test_session.query(TestCase).filter_by(contract_hash='f3da12622e9bb2b3f367a650a81fd8c70b2eb495', event_type='SmartContract.Runtime.Log').first()
        self.assertEqual(test_case, t_case)

    def test_find_related_test_case(self):
        # simulate test_case creation
        test_case = TestCase(contract_hash='f3da12622e9bb2b3f367a650a81fd8c70b2eb495', 
                transaction_hash='c33fd08be47a978778f1c7098804d8339ce6ec4002e8e7de580552785dca80f5', 
                event_type='SmartContract.Runtime.Log', 
                expected_payload_type='String', 
                expected_payload_value='Contract was called',
                active= True
            )
        self.test_session.add(test_case)
        self.test_session.commit()

        # simulate receiving a sc_event
        sc_event = self.generic_sc_event
        sc_event['tx_hash'] = 'c33fd08be47a978778f1c7098804d8339ce6ec4002e8e7de580552785dca80f5'
        sc_event['contract_hash'] = 'f3da12622e9bb2b3f367a650a81fd8c70b2eb495'
        sc_event['event_type'] = 'SmartContract.Runtime.Log'
        sc_event['event_payload']['type'] = 'String'
        sc_event['event_payload']['value'] = 'Contract was called'

        found_test_case = self.test_session.query(TestCase). \
            filter_by(contract_hash=sc_event['contract_hash'], transaction_hash=sc_event['tx_hash'],
                      event_type=sc_event['event_type'], active=True).first()

        self.assertEqual(test_case, found_test_case)
    
    def test_assess_should_eql_true(self):
        # simulate test_case creation
        t_case = TestCase(contract_hash='f3da12622e9bb2b3f367a650a81fd8c70b2eb495', 
                transaction_hash='c33fd08be47a978778f1c7098804d8339ce6ec4002e8e7de580552785dca80f5', 
                event_type='SmartContract.Runtime.Log', 
                expected_payload_type='String', 
                expected_payload_value='Contract was called',
                active= True
            )
        self.test_session.add(t_case)
        self.test_session.commit()

        # simulate receiving a sc_event
        sc_event = self.generic_sc_event
        sc_event['tx_hash'] = 'c33fd08be47a978778f1c7098804d8339ce6ec4002e8e7de580552785dca80f5'
        sc_event['contract_hash'] = 'f3da12622e9bb2b3f367a650a81fd8c70b2eb495'
        sc_event['event_type'] = 'SmartContract.Runtime.Log'
        sc_event['event_payload']['type'] = 'String'
        sc_event['event_payload']['value'] = 'Contract was called'
        
        # simulates handle event function from tasks
        found_test_case = self.test_session.query(TestCase). \
            filter_by(contract_hash=sc_event['contract_hash'], transaction_hash=sc_event['tx_hash'],
                      event_type=sc_event['event_type'], active=True).first()

        # simulates evaluate function from tasks
        test_case = self.test_session.query(TestCase).get(found_test_case.id)
        if not test_case.success:
            sc_event_payload = sc_event['event_payload']

            if sc_event['event_type'] == test_case.event_type.value and sc_event_payload['type'] == test_case.\
                    expected_payload_type.value:
                if str(sc_event_payload['value']) == test_case.expected_payload_value:
                    test_case.sc_event = json.dumps(sc_event)
                    test_case.active = False
                    test_case.success = True
                else:
                    test_case.sc_event = json.dumps(sc_event)
                    test_case.active = False
                    test_case.success = False

        self.assertEqual(test_case.active, False)
        self.assertEqual(test_case.success, True)

    def test_assess_should_eql_false(self):
        # simulate test_case creation
        t_case = TestCase(contract_hash='f3da12622e9bb2b3f367a650a81fd8c70b2eb495', 
                transaction_hash='c33fd08be47a978778f1c7098804d8339ce6ec4002e8e7de580552785dca80f5', 
                event_type='SmartContract.Runtime.Log', 
                expected_payload_type='String', 
                expected_payload_value='Contract was called',
                active= True
            )
        self.test_session.add(t_case)
        self.test_session.commit()

        # simulate receiving a sc_event
        sc_event = self.generic_sc_event
        sc_event['tx_hash'] = 'c33fd08be47a978778f1c7098804d8339ce6ec4002e8e7de580552785dca80f5'
        sc_event['contract_hash'] = 'f3da12622e9bb2b3f367a650a81fd8c70b2eb495'
        sc_event['event_type'] = 'SmartContract.Runtime.Log'
        sc_event['event_payload']['type'] = 'String'
        sc_event['event_payload']['value'] = 'This is not what is expected'
        
        # simulates handle event function from tasks
        found_test_case = self.test_session.query(TestCase). \
            filter_by(contract_hash=sc_event['contract_hash'], transaction_hash=sc_event['tx_hash'],
                      event_type=sc_event['event_type'], active=True).first()

        # simulates evaluate function from tasks
        test_case = self.test_session.query(TestCase).get(found_test_case.id)
        if not test_case.success:
            sc_event_payload = sc_event['event_payload']

            if sc_event['event_type'] == test_case.event_type.value and sc_event_payload['type'] == test_case.\
                    expected_payload_type.value:
                if str(sc_event_payload['value']) == test_case.expected_payload_value:
                    test_case.sc_event = json.dumps(sc_event)
                    test_case.active = False
                    test_case.success = True
                else:
                    test_case.sc_event = json.dumps(sc_event)
                    test_case.active = False
                    test_case.success = False

        self.assertEqual(test_case.active, False)
        self.assertEqual(test_case.success, False)

    def test_should_find_test_case(self):
        # simulate test_case creation
        t_case = TestCase(contract_hash='f3da12622e9bb2b3f367a650a81fd8c70b2eb495', 
                transaction_hash='c33fd08be47a978778f1c7098804d8339ce6ec4002e8e7de580552785dca80f5', 
                event_type='SmartContract.Runtime.Log', 
                expected_payload_type='String', 
                expected_payload_value='Contract was called',
                active= True
            )
        self.test_session.add(t_case)
        self.test_session.commit()

        # simulate receiving a sc_event
        sc_event = self.generic_sc_event
        sc_event['tx_hash'] = 'c33fd08be47a978778f1c7098804d8339ce6ec4002e8e7de580552785dca80f5'
        sc_event['contract_hash'] = 'f3da12622e9bb2b3f367a650a81fd8c70b2eb495'
        sc_event['event_type'] = 'SmartContract.Runtime.Notify'
        sc_event['event_payload']['type'] = 'String'
        sc_event['event_payload']['value'] = 'Contract was called'
        
        # simulates handle event function from tasks
        found_test_case = self.test_session.query(TestCase). \
            filter_by(contract_hash=sc_event['contract_hash'], transaction_hash=sc_event['tx_hash'],
                      event_type=sc_event['event_type'], active=True).first()
                    
        self.assertEqual(found_test_case, None)




    def tearDown(self):
        """
        tearDown is called when tests end to clean reset database
        """
        self.test_session.close()
        # rollback - everything that happened with the
        # Session above (including calls to commit())
        # is rolled back.
        self.trans.rollback()
        # return connection to the Engine
        self.connection.close()
        Base.metadata.drop_all(self.engine)