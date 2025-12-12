# 🚀 APLICACIÓN EN EJECUCIÓN

## Estado: ✅ FUNCIONANDO

La aplicación Polideportivo Torrelodones está corriendo correctamente en:

```
URL: http://127.0.0.1:5000
Servidor: Flask Development Server
Puerto: 5000
```

## Acceso

1. **Abre tu navegador** y ve a: **http://127.0.0.1:5000**
2. **Verás la página principal** con 4 instalaciones disponibles
3. **Selecciona una instalación** para continuar

## Flujo de la aplicación

1. **Página Principal** (`/`)
   - Muestra 4 instalaciones: Fútbol, Tenis, Pádel, Baloncesto
   - Cada una con tarifa de 20€/hora
   - Botón "Reservar" para cada instalación

2. **Seleccionar Fecha** (`/instalacion/<id>`)
   - Lista de fechas (próximos 30 días)
   - Grid de disponibilidad horaria (09:00-20:00)
   - Verde = Disponible (clickable)
   - Rojo = Ocupado (deshabilitado)

3. **Formulario de Reserva** (`/reservar/<id>/<fecha>/<hora>`)
   - Nombre (texto)
   - Email (email)
   - Botón "Confirmar Reserva"

4. **Confirmación** (`/confirmacion`)
   - Página de éxito con resumen

## API Endpoints (para developers)

### GET `/`
Página principal

### GET `/instalacion/<int:instalacion_id>`
Página de selección de fecha para una instalación

### GET `/api/disponibilidad/<int:instalacion_id>/<fecha>`
API REST que retorna disponibilidad horaria en JSON
```json
[
  {"hora": "09:00", "ocupada": false},
  {"hora": "10:00", "ocupada": false},
  ...
]
```

### GET `/reservar/<int:instalacion_id>/<fecha>/<hora>`
Formulario de reserva

### POST `/api/crear_reserva`
Crea una nueva reserva
```json
{
  "instalacion_id": 1,
  "nombre": "Juan",
  "email": "juan@example.com",
  "fecha": "2025-12-15",
  "hora": "14:00"
}
```

### GET `/confirmacion`
Página de confirmación

## Base de datos

**Archivo**: `reservas.db` (SQLite)

**Tablas**:
- `instalaciones` (id, nombre, tarifa_hora, descripcion)
- `reservas` (id, instalacion_id, nombre_usuario, email, fecha_inicio, fecha_fin, fecha_reserva)

## Testing

Para ejecutar los tests sin iniciar el servidor:
```bash
python test_app.py
```

Resultados esperados:
```
✓ App importada correctamente
✓ 6 rutas encontradas
✓ 4 instalaciones en BD
✓ 30 fechas disponibles
✓ Página principal carga correctamente
✓ API de disponibilidad funciona
```

## Parar la aplicación

Para detener el servidor:
1. Presiona **Ctrl+C** en la terminal donde corre `python run.py`
2. Espera a que el servidor se cierre (2-3 segundos)

## Próximos pasos

La aplicación está **lista para pruebas manuales** y **generación de informe final**. 

Puedes:
- ✅ Probar el flujo completo en tu navegador
- ✅ Crear varias reservas para ver cómo se actualizan
- ✅ Capturar pantallas para el informe
- ✅ Documentar cualquier mejora o feedback

---

**Generado por**: Asistente de IA
**Fecha**: 12-12-2025
