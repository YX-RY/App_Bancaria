import sqlite3
from datetime import datetime, timedelta
import json


def get_connection():
    return sqlite3.connect('finanzas.db', check_same_thread=False)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de categorías
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        tipo TEXT NOT NULL CHECK(tipo IN ('ingreso', 'gasto')),
        color TEXT,
        presupuesto REAL DEFAULT 0
    )
    ''')

    # Tabla de transacciones
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transacciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        monto REAL NOT NULL,
        descripcion TEXT,
        categoria_id INTEGER,
        fecha DATE NOT NULL,
        tipo TEXT NOT NULL CHECK(tipo IN ('ingreso', 'gasto')),
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    )
    ''')

    # Tabla de alertas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alertas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mensaje TEXT NOT NULL,
        tipo TEXT NOT NULL,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        leida INTEGER DEFAULT 0
    )
    ''')

    # Insertar categorías por defecto
    categorias_default = [
        ('Salario', 'ingreso', '#4CAF50', 0),
        ('Freelance', 'ingreso', '#8BC34A', 0),
        ('Inversiones', 'ingreso', '#2E7D32', 0),
        ('Alimentación', 'gasto', '#FF5722', 500),
        ('Transporte', 'gasto', '#2196F3', 300),
        ('Vivienda', 'gasto', '#3F51B5', 1000),
        ('Entretenimiento', 'gasto', '#9C27B0', 200),
        ('Salud', 'gasto', '#E91E63', 300),
        ('Educación', 'gasto', '#009688', 400),
        ('Otros', 'gasto', '#795548', 500)
    ]

    cursor.executemany(
        'INSERT OR IGNORE INTO categorias (nombre, tipo, color, presupuesto) VALUES (?, ?, ?, ?)',
        categorias_default
    )

    # Insertar transacciones de ejemplo
    fecha_hoy = datetime.now().date()
    transacciones_ejemplo = [
        (2500.00, 'Pago mensual', 1, fecha_hoy, 'ingreso'),
        (500.00, 'Diseño web', 2, fecha_hoy, 'ingreso'),
        (75.50, 'Supermercado', 4, fecha_hoy, 'gasto'),
        (25.00, 'Gasolina', 5, fecha_hoy, 'gasto'),
        (150.00, 'Netflix y Spotify', 7, fecha_hoy, 'gasto'),
        (1200.00, 'Alquiler', 6, fecha_hoy, 'gasto'),
        (80.00, 'Farmacia', 8, fecha_hoy, 'gasto'),
        (200.00, 'Curso online', 9, fecha_hoy, 'gasto')
    ]

    # Verificar si ya hay datos
    cursor.execute('SELECT COUNT(*) FROM transacciones')
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            'INSERT INTO transacciones (monto, descripcion, categoria_id, fecha, tipo) VALUES (?, ?, ?, ?, ?)',
            transacciones_ejemplo
        )

    conn.commit()
    conn.close()


# Operaciones CRUD para transacciones
def get_transacciones(filtro_categoria=None, filtro_tipo=None, fecha_inicio=None, fecha_fin=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = '''
    SELECT t.id, t.monto, t.descripcion, c.nombre, t.fecha, t.tipo, c.color
    FROM transacciones t
    LEFT JOIN categorias c ON t.categoria_id = c.id
    WHERE 1=1
    '''
    params = []

    if filtro_categoria:
        query += ' AND c.nombre LIKE ?'
        params.append(f'%{filtro_categoria}%')

    if filtro_tipo:
        query += ' AND t.tipo = ?'
        params.append(filtro_tipo)

    if fecha_inicio:
        query += ' AND t.fecha >= ?'
        params.append(fecha_inicio)

    if fecha_fin:
        query += ' AND t.fecha <= ?'
        params.append(fecha_fin)

    query += ' ORDER BY t.fecha DESC'

    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()

    return resultados


def agregar_transaccion(monto, descripcion, categoria_id, fecha, tipo):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO transacciones (monto, descripcion, categoria_id, fecha, tipo)
    VALUES (?, ?, ?, ?, ?)
    ''', (monto, descripcion, categoria_id, fecha, tipo))

    # Verificar presupuesto y crear alerta si es necesario
    if tipo == 'gasto':
        cursor.execute('''
        SELECT c.presupuesto, SUM(t.monto) as gasto_total
        FROM categorias c
        LEFT JOIN transacciones t ON c.id = t.categoria_id AND t.tipo = 'gasto'
        WHERE c.id = ?
        GROUP BY c.id
        ''', (categoria_id,))

        resultado = cursor.fetchone()
        if resultado and resultado[0] > 0:  # Si hay presupuesto definido
            presupuesto = resultado[0]
            gasto_total = resultado[1] or 0

            if gasto_total > presupuesto:
                cursor.execute('''
                INSERT INTO alertas (mensaje, tipo)
                VALUES (?, 'exceso_presupuesto')
                ''', (f'¡Presupuesto excedido en categoría ID {categoria_id}!',))
            elif gasto_total >= presupuesto * 0.8:
                cursor.execute('''
                INSERT INTO alertas (mensaje, tipo)
                VALUES (?, 'alerta_presupuesto')
                ''', (f'Cerca de alcanzar el presupuesto en categoría ID {categoria_id}',))

    conn.commit()
    conn.close()
    return cursor.lastrowid


def eliminar_transaccion(transaccion_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transacciones WHERE id = ?', (transaccion_id,))
    conn.commit()
    conn.close()
    return True


# Operaciones para categorías
def get_categorias(tipo=None):
    conn = get_connection()
    cursor = conn.cursor()

    if tipo:
        cursor.execute('SELECT * FROM categorias WHERE tipo = ? ORDER BY nombre', (tipo,))
    else:
        cursor.execute('SELECT * FROM categorias ORDER BY tipo, nombre')

    resultados = cursor.fetchall()
    conn.close()
    return resultados


def agregar_categoria(nombre, tipo, color, presupuesto=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO categorias (nombre, tipo, color, presupuesto) VALUES (?, ?, ?, ?)',
        (nombre, tipo, color, presupuesto)
    )
    conn.commit()
    conn.close()
    return True


# Estadísticas y resúmenes
def get_resumen_mes():
    conn = get_connection()
    cursor = conn.cursor()

    # Obtener el mes actual
    hoy = datetime.now().date()
    primer_dia_mes = hoy.replace(day=1)

    cursor.execute('''
    SELECT 
        COALESCE(SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END), 0) as total_ingresos,
        COALESCE(SUM(CASE WHEN tipo = 'gasto' THEN monto ELSE 0 END), 0) as total_gastos,
        COALESCE(SUM(CASE WHEN tipo = 'ingreso' THEN monto ELSE 0 END), 0) - 
        COALESCE(SUM(CASE WHEN tipo = 'gasto' THEN monto ELSE 0 END), 0) as saldo
    FROM transacciones
    WHERE fecha >= ?
    ''', (primer_dia_mes,))

    resumen = cursor.fetchone()
    conn.close()

    return {
        'ingresos': resumen[0] if resumen else 0,
        'gastos': resumen[1] if resumen else 0,
        'saldo': resumen[2] if resumen else 0
    }


def get_gastos_por_categoria(mes=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = '''
    SELECT c.nombre, c.color, SUM(t.monto) as total
    FROM transacciones t
    JOIN categorias c ON t.categoria_id = c.id
    WHERE t.tipo = 'gasto'
    '''

    params = []
    if mes:
        query += ' AND strftime("%Y-%m", t.fecha) = ?'
        params.append(mes)

    query += ' GROUP BY c.id ORDER BY total DESC'

    cursor.execute(query, params)
    resultados = cursor.fetchall()
    conn.close()

    return resultados


def get_ultimas_transacciones(limite=5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT t.id, t.monto, t.descripcion, c.nombre, t.fecha, t.tipo
    FROM transacciones t
    LEFT JOIN categorias c ON t.categoria_id = c.id
    ORDER BY t.fecha DESC, t.id DESC
    LIMIT ?
    ''', (limite,))

    resultados = cursor.fetchall()
    conn.close()
    return resultados


# Alertas
def get_alertas_no_leidas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM alertas WHERE leida = 0 ORDER BY fecha DESC')
    resultados = cursor.fetchall()
    conn.close()
    return resultados


def marcar_alerta_leida(alerta_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE alertas SET leida = 1 WHERE id = ?', (alerta_id,))
    conn.commit()
    conn.close()
    return True