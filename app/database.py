import sqlite3
import os
from datetime import datetime, timedelta
import uuid

DB_PATH = 'reservas.db'

def init_db():
    """Inicializa la base de datos con tablas y datos de ejemplo."""
    if os.path.exists(DB_PATH):
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de instalaciones
    cursor.execute('''
        CREATE TABLE instalaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tarifa_hora REAL NOT NULL,
            descripcion TEXT
        )
    ''')
    
    # Insertar instalaciones de ejemplo
    instalaciones = [
        ('Campo de Fútbol', 20.0, 'Pista de fútbol 11'),
        ('Pista de Tenis', 10.0, 'Pista de tenis profesional'),
        ('Pista de Pádel', 10.0, 'Pista de pádel'),
        ('Pista de Baloncesto', 15.0, 'Cancha de baloncesto')
    ]
    cursor.executemany('INSERT INTO instalaciones (nombre, tarifa_hora, descripcion) VALUES (?, ?, ?)', instalaciones)
    
    # Tabla de reservas
    cursor.execute('''
        CREATE TABLE reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instalacion_id INTEGER NOT NULL,
            nombre_usuario TEXT NOT NULL,
            email TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(instalacion_id) REFERENCES instalaciones(id)
        )
    ''')
    
    conn.commit()
    conn.close()

    # Asegurar columna cancel_token exista (si migración desde versiones previas)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(reservas)")
        cols = [r[1] for r in cursor.fetchall()]
        if 'cancel_token' not in cols:
            cursor.execute('ALTER TABLE reservas ADD COLUMN cancel_token TEXT')
            conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    # Insertar reservas de ejemplo (ocupados) para mostrar horarios ocupados al inicio
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # reservas de ejemplo: mañana 10:00-11:00 para instalación 1, pasado mañana 12:00-13:00 para instalación 2
        mañana = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        pasado = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        reservas_demo = [
            (1, 'Demo IA', 'demo@ia.local', f"{mañana} 10:00", f"{mañana} 11:00"),
            (2, 'Usuario Demo', 'user@example.com', f"{pasado} 12:00", f"{pasado} 13:00"),
            (3, 'Demo IA', 'demo@ia.local', f"{mañana} 15:00", f"{mañana} 16:00")
        ]
        cursor.executemany('INSERT INTO reservas (instalacion_id, nombre_usuario, email, fecha_inicio, fecha_fin) VALUES (?, ?, ?, ?, ?)', reservas_demo)
        conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

def get_db_connection():
    """Obtiene una conexión a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_instalaciones():
    """Obtiene la lista de instalaciones disponibles."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM instalaciones')
    instalaciones = cursor.fetchall()
    conn.close()
    return instalaciones

def get_disponibilidad(instalacion_id, fecha):
    """
    Obtiene la disponibilidad de una instalación para un día específico.
    Retorna un diccionario con horas disponibles y ocupadas.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener todas las reservas para esta instalación en esta fecha
    cursor.execute('''
        SELECT fecha_inicio, fecha_fin FROM reservas 
        WHERE instalacion_id = ? AND DATE(fecha_inicio) = ?
    ''', (instalacion_id, fecha))
    
    reservas = cursor.fetchall()
    conn.close()
    
    # Generar lista de horas (09:00 a 20:00)
    horas = []
    for hora in range(9, 21):
        hora_str = f"{hora:02d}:00"
        # Verificar si esta hora está ocupada
        ocupada = False
        for reserva in reservas:
            inicio = datetime.fromisoformat(reserva['fecha_inicio'])
            fin = datetime.fromisoformat(reserva['fecha_fin'])
            hora_datetime = datetime.strptime(f"{fecha} {hora_str}", "%Y-%m-%d %H:%M")
            if inicio <= hora_datetime < fin:
                ocupada = True
                break
        
        horas.append({
            'hora': hora_str,
            'ocupada': ocupada
        })
    
    return horas

def crear_reserva(instalacion_id, nombre, email, fecha, hora):
    """Crea una reserva si no hay solapamientos.

    Retorna (ok: bool, msg: str, reserva_id: int|None, cancel_token: str|None)
    """
    fecha_inicio = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
    fecha_fin = fecha_inicio + timedelta(hours=1)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Comprobar solapamientos: existe alguna reserva para la misma instalación
    # donde start < fecha_fin AND end > fecha_inicio
    cursor.execute(
        'SELECT COUNT(*) FROM reservas WHERE instalacion_id = ? AND (fecha_inicio < ? AND fecha_fin > ?)',
        (instalacion_id, fecha_fin.isoformat(), fecha_inicio.isoformat())
    )
    (count,) = cursor.fetchone()
    if count > 0:
        conn.close()
        return (False, 'La franja ya está ocupada', None, None)

    # Generar token de cancelación
    token = uuid.uuid4().hex

    cursor.execute(
        'INSERT INTO reservas (instalacion_id, nombre_usuario, email, fecha_inicio, fecha_fin, cancel_token) VALUES (?, ?, ?, ?, ?, ?)',
        (instalacion_id, nombre, email, fecha_inicio.isoformat(), fecha_fin.isoformat(), token)
    )
    reserva_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return (True, 'Reserva creada', reserva_id, token)


def cancelar_reserva(reserva_id, email):
    """Cancela una reserva sólo si el email coincide. Retorna True si se eliminó."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM reservas WHERE id = ?', (reserva_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, 'Reserva no encontrada'
    if row['email'].lower() != email.lower():
        conn.close()
        return False, 'Email no coincide con la reserva'
    cursor.execute('DELETE FROM reservas WHERE id = ?', (reserva_id,))
    conn.commit()
    conn.close()
    return True, None

def get_proximos_30_dias():
    """Retorna una lista de fechas para los próximos 30 días."""
    fechas = []
    for i in range(30):
        fecha = datetime.now() + timedelta(days=i)
        fechas.append(fecha.strftime("%Y-%m-%d"))
    return fechas
