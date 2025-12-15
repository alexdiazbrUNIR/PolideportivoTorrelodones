import os
import sqlite3
from app import database
from datetime import datetime, timedelta


def setup_tmp_db(tmp_path, monkeypatch):
    dbfile = tmp_path / "test_reservas.db"
    monkeypatch.setattr(database, 'DB_PATH', str(dbfile))
    # remove if exists
    try:
        os.remove(dbfile)
    except Exception:
        pass
    database.init_db()
    return dbfile


def test_init_db_creates_tables(tmp_path, monkeypatch):
    dbfile = setup_tmp_db(tmp_path, monkeypatch)
    conn = sqlite3.connect(dbfile)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cursor.fetchall()}
    assert 'instalaciones' in tables
    assert 'reservas' in tables
    conn.close()


def test_get_instalaciones_contains_four(tmp_path, monkeypatch):
    setup_tmp_db(tmp_path, monkeypatch)
    insts = database.get_instalaciones()
    assert len(insts) == 4


def test_crear_reserva_and_cancel(tmp_path, monkeypatch):
    setup_tmp_db(tmp_path, monkeypatch)
    fecha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    ok, msg, reserva_id, token = database.crear_reserva(1, 'Test User', 'test@example.com', fecha, '10:00')
    assert ok is True
    assert reserva_id is not None
    assert token is not None

    # Ensure overlap prevented
    ok2, msg2, _, _ = database.crear_reserva(1, 'Another', 'a@example.com', fecha, '10:00')
    assert ok2 is False
    assert 'ocupada' in msg2

    # Cancel with wrong email
    ok_cancel, msg_cancel = database.cancelar_reserva(reserva_id, 'wrong@example.com')
    assert ok_cancel is False

    # Cancel with correct email
    ok_cancel2, msg_cancel2 = database.cancelar_reserva(reserva_id, 'test@example.com')
    assert ok_cancel2 is True


def test_get_disponibilidad_marks_occupied(tmp_path, monkeypatch):
    setup_tmp_db(tmp_path, monkeypatch)
    fecha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    database.crear_reserva(2, 'U', 'u@example.com', fecha, '12:00')
    horas = database.get_disponibilidad(2, fecha)
    occupied = [h for h in horas if h['hora'] == '12:00' and h['ocupada']]
    assert len(occupied) == 1
