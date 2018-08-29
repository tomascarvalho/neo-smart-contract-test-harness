from celery import Task, Celery, shared_task
from settings import redis_url
from models import Session, TestCase
# from configuration.settings import redis_url

app = Celery('tasks', broker = redis_url)

class DatabaseTask(Task):
    _session = None

    @property
    def session(self):
        if self._session is None:
            self._session = Session()
        return self._session

@shared_task(base=DatabaseTask)
def handle_event(sc_event):
    #network = sc_event['extra']['network']
    # hooks = Hook.objects.filter(contract=sc_event['contract_hash'], network=network)
    # for hook in hooks:

    test_cases = handle_event.session.query(TestCase).\
        filter_by(contract_hash=sc_event['contract_hash'], event_type=sc_event['event_type'], active=True)

    for test_case in test_cases:
        evaluate.delay(sc_event, test_case.id)
    return True


@shared_task(base=DatabaseTask)
def evaluate(sc_event, id):
    # response = requests.post('localhost:1234', json=sc_event, timeout=10)
    # if response.status_code != 200:
    #     raise RuntimeError('Invalid response, will retry later')
    test_case = evaluate.session.query(TestCase).get(id)
    print('TestCase: ', test_case)
    s ="""\n\n
        -------------------------------------
                    Event Received!
          Contract hash: {0}
          Event type: {1}
          Expected event: {2}
          Expected type: {3}
          Expected value: {4}
          Got: {5} - {6}
        -------------------------------------
        """
    print(s.format(sc_event['contract_hash'], sc_event['event_type'], test_case.event_type.value, test_case.expected_payload_type.value, test_case.expected_payload_value, sc_event['event_payload']['type'], sc_event['event_payload']['value']))

    sc_event_payload = sc_event['event_payload']
    if sc_event['event_type'] == test_case.event_type.value and sc_event_payload['type'] == test_case.expected_payload_type.value:
        if str(sc_event_payload['value']) == test_case.expected_payload_value:
            print("Passed!")
            test_case.active = False # In production we need to save and commit this
            return True
    print("Failed!")
    return True
