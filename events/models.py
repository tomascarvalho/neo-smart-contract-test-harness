from sqlalchemy import create_engine, Column, String, Integer, Sequence, Boolean, DateTime
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import database_url
from datetime import datetime

Base = declarative_base()


class TestCase(Base):
    DATA_TYPES = [
        ('Signature', 'Signature'),
        ('Boolean', 'Boolean'),
        ('Integer', 'Integer'),
        ('Hash160', 'Hash160'),
        ('Hash256', 'Hash256'),
        ('ByteArray', 'ByteArray'),
        ('PublicKey', 'PublicKey'),
        ('String', 'String'),
        ('Array', 'Array'),
        ('InteropInterface', 'InteropInterface'),
        ('Void', 'Void')
    ]

    EVENT_TYPES = [
        ('SmartContract.Runtime.Notify', 'SmartContract.Runtime.Notify'),
        ('SmartContract.Runtime.Log', 'SmartContract.Runtime.Log'),
        ('SmartContract.Execution.*', 'SmartContract.Execution.*'),
        ('SmartContract.Execution.Invoke', 'SmartContract.Execution.Invoke'),
        ('SmartContract.Execution.Success', 'SmartContract.Execution.Success'),
        ('SmartContract.Execution.Fail', 'SmartContract.Execution.Fail'),
        ('SmartContract.Verification.*', 'SmartContract.Verification.*'),
        ('SmartContract.Verification.Success', 'SmartContract.Verification.Success'),
        ('SmartContract.Verification.Fail', 'SmartContract.Verification.Fail'),
        ('SmartContract.Storage.*', 'SmartContract.Storage.*'),
        ('SmartContract.Storage.Get', 'SmartContract.Storage.Get'),
        ('SmartContract.Storage.Put', 'SmartContract.Storage.Put'),
        ('SmartContract.Storage.Delete', 'SmartContract.Storage.Delete'),
        ('SmartContract.Contract.*', 'SmartContract.Contract.*'),
        ('SmartContract.Contract.Create', 'SmartContract.Contract.Create'),
        ('SmartContract.Contract.Migrate', 'SmartContract.Contract.Migrate'),
        ('SmartContract.Contract.Destroy', 'SmartContract.Contract.Destroy')
    ]

    __tablename__ = 'test_cases'
    id = Column(Integer, Sequence('test_case_id_seq'), primary_key=True)
    contract_hash = Column(String(128))
    transaction_hash = Column(String(128))
    event_type = Column(ChoiceType(EVENT_TYPES))
    expected_payload_type = Column(ChoiceType(DATA_TYPES))
    expected_payload_value = Column(String(512))
    sc_event = Column(String(512))
    active = Column(Boolean, default=True)
    success = Column(Boolean, default=None)
    createdAt = Column(DateTime, default=datetime.now)
    updatedAt = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return "<TestCase(test_id='%s' contract_hash='%s' contract_hash='%s' event='%s' expected_payload_type='%s " \
               "expected_payload_value='%s' active='%s')>" % (
                   self.id, self.contract_hash, self.transaction_hash, self.event_type, self.expected_payload_type,
                   self.expected_payload_value, self.active)


engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
engine.dispose()
