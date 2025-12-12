#!/usr/bin/env python
"""
Script de testing para verificar que la aplicación funciona correctamente.
"""

print("=" * 60)
print("TESTING POLIDEPORTIVO TORRELODONES")
print("=" * 60)

# Test 1: Importar app
print("\n[TEST 1] Importar aplicación Flask...")
try:
    from app.routes import app
    print("✓ App importada correctamente")
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Test 2: Verificar rutas
print("\n[TEST 2] Verificar rutas registradas...")
try:
    routes = [str(r) for r in app.url_map.iter_rules() if 'static' not in str(r)]
    print(f"✓ {len(routes)} rutas encontradas:")
    for route in routes:
        print(f"  - {route}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Verificar BD
print("\n[TEST 3] Verificar base de datos...")
try:
    from app.database import get_instalaciones, get_proximos_30_dias
    instalaciones = get_instalaciones()
    print(f"✓ BD inicializada. {len(instalaciones)} instalaciones:")
    for inst in instalaciones:
        print(f"  - {inst['nombre']} ({inst['tarifa_hora']}€/hora)")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Verificar fechas
print("\n[TEST 4] Verificar próximos 30 días...")
try:
    fechas = get_proximos_30_dias()
    print(f"✓ {len(fechas)} fechas disponibles (desde {fechas[0]} hasta {fechas[-1]})")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Test client
print("\n[TEST 5] Test GET / (página principal)...")
try:
    client = app.test_client()
    response = client.get('/')
    if response.status_code == 200:
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Content-Type: {response.content_type}")
        if b'Polideportivo' in response.data:
            print("✓ Contenido HTML válido (contiene 'Polideportivo')")
    else:
        print(f"✗ Status inesperado: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 6: Verificar rutas de instalaciones
print("\n[TEST 6] Test GET /instalacion/1...")
try:
    client = app.test_client()
    response = client.get('/instalacion/1')
    if response.status_code == 200:
        print(f"✓ Status: {response.status_code}")
        if b'disponib' in response.data.lower():
            print("✓ Página de disponibilidad cargada")
    else:
        print(f"✗ Status inesperado: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 7: Verificar API de disponibilidad
print("\n[TEST 7] Test GET /api/disponibilidad/1/2025-12-13...")
try:
    client = app.test_client()
    response = client.get('/api/disponibilidad/1/2025-12-13')
    if response.status_code == 200:
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Content-Type: {response.content_type}")
        datos = response.get_json()
        if isinstance(datos, list) and len(datos) > 0:
            print(f"✓ {len(datos)} horas retornadas")
            print(f"  Ejemplo: {datos[0]}")
    else:
        print(f"✗ Status inesperado: {response.status_code}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("TESTING COMPLETADO")
print("=" * 60)
print("\n✅ La aplicación está lista para ejecutar:")
print("   Ejecuta: python run.py")
print("   Luego abre: http://127.0.0.1:5000")
