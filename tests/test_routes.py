import json
import sqlite3
from app import database
from app.routes import app


def setup_tmp_db(tmp_path, monkeypatch):
    dbfile = tmp_path / "test_reservas.db"
    monkeypatch.setattr(database, 'DB_PATH', str(dbfile))
    try:
        dbfile.unlink()
    except Exception:
        pass
    database.init_db()
    return dbfile


def test_index_and_instalacion_pages(tmp_path, monkeypatch):
    setup_tmp_db(tmp_path, monkeypatch)
    client = app.test_client()
    r = client.get('/')
    assert r.status_code == 200
    assert b'Polideportivo' in r.data

    r2 = client.get('/instalacion/1')
    assert r2.status_code == 200
    assert b'Selecciona una fecha' in r2.data


def test_api_crear_reserva_and_cancel_with_token(tmp_path, monkeypatch):
    setup_tmp_db(tmp_path, monkeypatch)
    client = app.test_client()

    fecha = '2099-01-01'  # distant date to avoid demo conflicts
    data = {
        'instalacion_id': 1,
        'nombre': 'Tester',
        'email': 'tester@example.com',
        'fecha': fecha,
        'hora': '09:00'
    }

    resp = client.post('/api/crear_reserva', json=data)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body['exito'] is True
    assert 'cancel_token' in body
    token = body['cancel_token']

    # Now cancel via token
    resp2 = client.post('/api/cancel_with_token', json={'token': token})
    assert resp2.status_code == 200
    assert resp2.get_json().get('ok') is True


def test_api_mis_reservas_and_cancel_by_email(tmp_path, monkeypatch):
    setup_tmp_db(tmp_path, monkeypatch)
    client = app.test_client()

    fecha = '2099-02-01'
    # create a reservation
    resp = client.post('/api/crear_reserva', json={
        'instalacion_id': 2,
        'nombre': 'MailUser',
        'email': 'mail@example.com',
        'fecha': fecha,
        'hora': '10:00'
    })
    assert resp.status_code == 201
    body = resp.get_json()
    res_id = body['reserva_id']

    # fetch by email
    resp_get = client.get(f'/api/mis_reservas?email=mail@example.com')
    assert resp_get.status_code == 200
    arr = resp_get.get_json()
    assert any(r['id'] == res_id for r in arr)

    # cancel by email
    resp_cancel = client.post('/api/cancel_reserva', json={'reserva_id': res_id, 'email': 'mail@example.com'})
    assert resp_cancel.status_code == 200
    assert resp_cancel.get_json().get('exito') is True

    # cancelling again should fail
    resp_cancel2 = client.post('/api/cancel_reserva', json={'reserva_id': res_id, 'email': 'mail@example.com'})
    assert resp_cancel2.status_code == 403
