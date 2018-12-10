import json
from celery import Task, Celery, shared_task
from exceptions import NoTransactionFound
from models import Session, TestCase
from settings import redis_url

app = Celery('tasks', broker=redis_url)


class DatabaseTask(Task):
    _session = None

    @property
    def session(self):
        if self._session is None:
            self._session = Session()
        return self._session


@shared_task(base=DatabaseTask, autoretry_for=(NoTransactionFound,), default_retry_delay=0.5, max_retries=10,
             retry_backoff=True)
def handle_event(sc_event):
    """
    This shared_task handles smart contract events by querying the database searching for tests that might concern them
    :param sc_event: a smart contract event
    :return: True if task is successful, False otherwise
    """
    try:
        test_case = handle_event.session.query(TestCase). \
            filter_by(contract_hash=sc_event['contract_hash'], transaction_hash=sc_event['tx_hash'],
                      event_type=sc_event['event_type'], active=True).first()
        if not test_case:
            print("Retrying...")
            raise NoTransactionFound("No transaction found with tx_hash: " + sc_event['tx_hash'])
    except NoTransactionFound:
        pass
    else:
        evaluate.delay(sc_event, test_case.id)
    return True


@shared_task(base=DatabaseTask)
def evaluate(sc_event, test_case_id):
    """
    This shared_task evaluates if a pre-determined test fails or passes.
    Stores the result on the database.
    :param sc_event: a smart contract event
    :param test_case_id: a test case ID
    :return: True if task is successful, False otherwise
    """
    test_case = evaluate.session.query(TestCase).get(test_case_id)
    if not test_case.success:
        s = """\n\n
            -------------------------------------
                        Event Received!
              Contract hash: {0}
              TX hash: {1}
              Event type: {2}
              Expected event: {3}
              Expected type: {4}
              Expected value: {5}
              Got: {6} - {7}
            -------------------------------------
            """
        print(s.format(sc_event['contract_hash'], sc_event['tx_hash'], sc_event['event_type'], test_case.event_type.value,
                       test_case.expected_payload_type.value, test_case.expected_payload_value,
                       sc_event['event_payload']['type'], sc_event['event_payload']['value']))

        sc_event_payload = sc_event['event_payload']

        if sc_event['event_type'] == test_case.event_type.value and sc_event_payload['type'] == test_case.\
                expected_payload_type.value:
            if str(sc_event_payload['value']) == test_case.expected_payload_value:
                print("Passed!")
                test_case.sc_event = json.dumps(sc_event)
                test_case.active = False
                test_case.success = True
        else:
            print("Failed!")
            test_case.sc_event = json.dumps(sc_event)
            test_case.active = False
            test_case.success = False

        evaluate.session.add(test_case)
        try:
            evaluate.session.commit()
        except Exception:
            evaluate.session.rollback()
            raise
        finally:
            evaluate.session.close()

        return True
