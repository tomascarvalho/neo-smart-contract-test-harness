import requests
from celery import Celery, shared_task

app = Celery('tasks', broker = 'redis://localhost:6379/0')

@shared_task(autoretry_for=(Exception,), max_retries=5)
def handle_event(sc_event):
    #network = sc_event['extra']['network']
    # hooks = Hook.objects.filter(contract=sc_event['contract_hash'], network=network)
    # for hook in hooks:
    call_endpoint.delay(sc_event)
    return True


@shared_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=10)
def call_endpoint(sc_event):
    # response = requests.post('localhost:1234', json=sc_event, timeout=10)
    # if response.status_code != 200:
    #     raise RuntimeError('Invalid response, will retry later')
    print(sc_event)
    return True
