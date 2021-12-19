import time
import requests

BASE_URL = "http://minikom:8080"

def url(suffix):
    return BASE_URL + "/" + suffix

def send_event(service_name, state, timestamp):
    return requests.post(url('event'), json=dict(
        service_name=service_name,
        state=state,
        timestamp=timestamp
    ))

def reset_server():
    requests.get(url('reset'))

def test_happy_flow():
    reset_server()
    current_time = time.time()
    response = send_event('service', 'state', current_time)
    assert response.status_code == 200
    response = requests.get(url('services'))
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert 'service' in payload
    entry = payload['service']
    assert entry['state'] == 'state'
    assert entry['since'] == current_time

def test_idle():
    reset_server()
    current_time = time.time()
    response = send_event('service', 'state', current_time - 20)
    assert response.status_code == 200
    response = requests.get(url('services'))
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert 'service' in payload
    entry = payload['service']
    assert entry['state'] == 'idle'
    assert entry['since'] == current_time - 10

def test_changing_state():
    reset_server()
    t1 = time.time()
    response = send_event('service', 's1', t1)
    assert response.status_code == 200
    t2 = time.time()
    response = send_event('service', 's2', t2)
    assert response.status_code == 200
    t3 = time.time()
    response = send_event('service', 's2', t3)
    assert response.status_code == 200
    response = requests.get(url('services'))
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert 'service' in payload
    entry = payload['service']
    assert entry['state'] == 's2'
    assert entry['since'] == t2
    response = requests.get(url('services/service/latest-events'))
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3
    for i in range(2):
        entry = payload[i]
        assert entry['state'] == 's2'
        assert entry['start_time'] == t2
        assert entry['end_time'] is None
    entry = payload[2]
    assert entry['state'] == 's1'
    assert entry['start_time'] == t1
    assert entry['end_time'] == t2


