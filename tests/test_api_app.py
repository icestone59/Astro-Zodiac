from fastapi.testclient import TestClient
from api_app import app
client = TestClient(app)

def test_health():
    r=client.get('/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_register_login_me():
    email='t18@example.com'
    r=client.post('/api/v1/auth/register',json={'email':email,'password':'StrongPass123!','display_name':'T18'})
    assert r.status_code==201
    r=client.post('/api/v1/auth/login',json={'email':email,'password':'StrongPass123!'})
    assert r.status_code==200
    token=r.json()['access_token']
    r=client.get('/api/v1/me',headers={'Authorization':f'Bearer {token}'})
    assert r.status_code==200 and r.json()['email']==email

def test_auth_required():
    assert client.get('/api/v1/me').status_code==401
    payload={'day':1,'month':1,'year_buddhist':2530,'hour':12,'minute':0,'location_name':'กรุงเทพมหานคร'}
    assert client.post('/api/v1/analysis/free',json=payload).status_code==401
