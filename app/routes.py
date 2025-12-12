import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from app.database import (
    init_db, get_instalaciones, get_disponibilidad, 
    crear_reserva, get_proximos_30_dias, cancelar_reserva, get_db_connection
)

# Obtener rutas absolutas
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(base_dir, 'app', 'templates')
static_dir = os.path.join(base_dir, 'app', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Inicializar BD al arrancar
init_db()

@app.route('/')
def index():
    """Página principal - selección de instalación."""
    instalaciones = get_instalaciones()
    return render_template('index.html', instalaciones=instalaciones)

@app.route('/instalacion/<int:instalacion_id>')
def seleccionar_instalacion(instalacion_id):
    """Página para seleccionar fecha y hora de una instalación."""
    instalaciones = get_instalaciones()
    instalacion = next((i for i in instalaciones if i['id'] == instalacion_id), None)
    
    if not instalacion:
        return redirect(url_for('index'))
    
    fechas = get_proximos_30_dias()
    return render_template('seleccionar_fecha.html', instalacion=instalacion, fechas=fechas)

@app.route('/api/disponibilidad/<int:instalacion_id>/<fecha>')
def api_disponibilidad(instalacion_id, fecha):
    """API que retorna la disponibilidad para una instalación y fecha."""
    horas = get_disponibilidad(instalacion_id, fecha)
    return jsonify(horas)

@app.route('/reservar/<int:instalacion_id>/<fecha>/<hora>')
def formulario_reserva(instalacion_id, fecha, hora):
    """Página con formulario para completar la reserva."""
    instalaciones = get_instalaciones()
    instalacion = next((i for i in instalaciones if i['id'] == instalacion_id), None)
    
    if not instalacion:
        return redirect(url_for('index'))
    
    return render_template('formulario_reserva.html', 
                         instalacion=instalacion, 
                         fecha=fecha, 
                         hora=hora)

@app.route('/api/crear_reserva', methods=['POST'])
def api_crear_reserva():
    """API que crea una nueva reserva."""
    datos = request.json or {}

    instalacion_id = datos.get('instalacion_id')
    nombre = datos.get('nombre')
    email = datos.get('email')
    fecha = datos.get('fecha')
    hora = datos.get('hora')

    # Validar datos
    if not all([instalacion_id, nombre, email, fecha, hora]):
        return jsonify({'error': 'Faltan datos'}), 400

    # Crear reserva con validación de solapamientos y token
    ok, msg, reserva_id, token = crear_reserva(int(instalacion_id), nombre, email, fecha, hora)
    if not ok:
        return jsonify({'exito': False, 'mensaje': msg}), 409

    # Simular envío de email con token: incluimos URL de confirmación/cancelación
    confirm_url = url_for('confirmacion') + f'?res_id={reserva_id}&token={token}'
    cancel_url = url_for('cancel_via_token', token=token)
    return jsonify({'exito': True, 'reserva_id': reserva_id, 'cancel_token': token, 'confirm_url': confirm_url, 'cancel_url': cancel_url}), 201

@app.route('/confirmacion')
def confirmacion():
    """Página de confirmación de reserva."""
    return render_template('confirmacion.html')


@app.route('/mis_reservas', methods=['GET'])
def mis_reservas():
    """Página donde el usuario introduce su email y ve sus reservas (con opción de cancelar)."""
    return render_template('mis_reservas.html')


@app.route('/api/mis_reservas')
def api_mis_reservas():
    """Retorna en JSON las reservas asociadas a un email pasado como query param: ?email=.."""
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'email requerido'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, instalacion_id, nombre_usuario, email, fecha_inicio, fecha_fin, fecha_reserva FROM reservas WHERE LOWER(email) = LOWER(?) ORDER BY fecha_inicio', (email,))
    rows = cursor.fetchall()
    conn.close()
    res = []
    for r in rows:
        res.append({k: r[k] for k in r.keys()})
    return jsonify(res)


@app.route('/api/cancel_reserva', methods=['POST'])
def api_cancel_reserva():
    """Cancela una reserva si el email coincide con el registrado."""
    datos = request.json or {}
    reserva_id = datos.get('reserva_id')
    email = datos.get('email')
    if not reserva_id or not email:
        return jsonify({'error': 'reserva_id y email requeridos'}), 400
    ok, msg = cancelar_reserva(reserva_id, email)
    if not ok:
        return jsonify({'error': msg}), 403
    return jsonify({'exito': True}), 200


@app.route('/cancel/<token>')
def cancel_via_token(token):
    """Muestra una página para confirmar la cancelación a través del token."""
    return render_template('cancel_confirm.html', token=token)


@app.route('/api/cancel_with_token', methods=['POST'])
def api_cancel_with_token():
    datos = request.json or request.form
    token = datos.get('token')
    if not token:
        return jsonify({'ok': False, 'msg': 'Token no proporcionado'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM reservas WHERE cancel_token = ?', (token,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return jsonify({'ok': False, 'msg': 'Token inválido o ya usado'}), 404
    reserva_id = row['id']
    cur.execute('DELETE FROM reservas WHERE id = ?', (reserva_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'msg': 'Reserva cancelada'})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
