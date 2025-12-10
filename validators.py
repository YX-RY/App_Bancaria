import re
from datetime import datetime


def validar_monto(monto_str):
    """Valida que el monto sea un número positivo"""
    try:
        monto = float(monto_str)
        if monto <= 0:
            return False, "El monto debe ser mayor a cero"
        return True, ""
    except ValueError:
        return False, "Ingrese un número válido"


def validar_fecha(fecha_str):
    """Valida el formato de fecha"""
    try:
        datetime.strptime(fecha_str, '%Y-%m-%d')
        return True, ""
    except ValueError:
        return False, "Formato de fecha inválido (YYYY-MM-DD)"


def validar_descripcion(descripcion):
    """Valida la descripción"""
    if not descripcion or len(descripcion.strip()) == 0:
        return False, "La descripción es obligatoria"
    if len(descripcion) > 200:
        return False, "La descripción no debe exceder 200 caracteres"

    # Validar caracteres especiales peligrosos
    if re.search(r'[<>{}[\]]', descripcion):
        return False, "La descripción contiene caracteres no permitidos"

    return True, ""


def validar_categoria(categoria_id):
    """Valida que se haya seleccionado una categoría"""
    if not categoria_id or categoria_id <= 0:
        return False, "Seleccione una categoría"
    return True, ""


def validar_tipo_transaccion(tipo):
    """Valida el tipo de transacción"""
    if tipo not in ['ingreso', 'gasto']:
        return False, "Tipo de transacción inválido"
    return True, ""