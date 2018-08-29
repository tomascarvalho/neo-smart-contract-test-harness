from models import Session, TestCase

session = Session()
test_case = TestCase(contract_hash='f3da12622e9bb2b3f367a650a81fd8c70b2eb495', event_type='SmartContract.Runtime.Log', expected_payload_type='String', expected_payload_value='Contract was called')
session.add(test_case)
session.commit()
