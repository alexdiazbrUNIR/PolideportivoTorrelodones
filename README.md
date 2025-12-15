# Polideportivo Torrelodones - Sistema de Reservas

## Descripción
Aplicación web simple para gestionar reservas de instalaciones deportivas en un polideportivo ficticio.

## Características
- Selección de 4 tipos de instalaciones (fútbol, tenis, pádel, baloncesto)
- Visualización de disponibilidad para los próximos 30 días
- Sistema de reservas sin autenticación (acceso directo)
- Tarifa fija de 20€ por hora
- Base de datos SQLite local

## Instalación

### Requisitos
- Python 3.8 o superior

### Pasos
1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecuta la aplicación:
```bash
python run.py
```

3. Abre tu navegador en: `http://127.0.0.1:5000`

## Estructura del Proyecto
```
PolideportivoTorrelodones/
├── app/
│   ├── __init__.py
│   ├── database.py        # Funciones de base de datos
│   ├── routes.py          # Rutas de Flask
│   ├── static/
│   │   └── css/
│   │       └── style.css  # Estilos
│   └── templates/
│       ├── index.html     # Página principal
│       ├── seleccionar_fecha.html
│       ├── formulario_reserva.html
│       └── confirmacion.html
├── run.py                 # Punto de entrada
├── requirements.txt       # Dependencias
└── reservas.db           # Base de datos SQLite (se genera automáticamente)
```

## Flujo de la Aplicación
1. Usuario entra en la página principal y ve 4 instalaciones
2. Selecciona una instalación
3. Elige una fecha de los próximos 30 días
4. Ve horas disponibles (verde) y ocupadas (rojo)
5. Hace clic en una hora disponible
6. Rellena formulario con nombre y email
7. Confirma la reserva
8. Ve página de confirmación

## Dependencias
- Flask 2.3.3
- Werkzeug 2.3.7

## Notas
- Las reservas se almacenan en una BD SQLite local
- No requiere registro ni login
- Tarifa fija de 20€/hora para todas las instalaciones
- Horarios disponibles: 09:00 a 20:00

## Tests
- Instala dependencias de pruebas: `pip install -r requirements-tests.txt`
- Ejecuta todos los tests: `./run_tests.ps1` (Windows PowerShell) o `./run_tests.sh` (Linux / macOS)

E2E (Playwright):
- Se incluye un test E2E en `tests/test_e2e_playwright.py` que automatiza reservar y cancelar vía UI.
- Para ejecutarlo debes tener Playwright instalado y los navegadores descargados: después de `pip install -r requirements-tests.txt`, ejecuta `playwright install --with-deps`.
- En entornos con restricciones de red, la instalación de Playwright puede fallar. Como alternativa puedes usar Selenium (requiere instalar `selenium` y un driver de navegador).

## Autor
Generado mediante interacción con asistente de IA
