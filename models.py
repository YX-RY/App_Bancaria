from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Transaccion:
    id: Optional[int] = None
    monto: float = 0.0
    descripcion: str = ""
    categoria_id: Optional[int] = None
    fecha: date = date.today()
    tipo: str = "gasto"  # 'ingreso' o 'gasto'

    @property
    def color(self):
        return "#4CAF50" if self.tipo == "ingreso" else "#FF5722"


@dataclass
class Categoria:
    id: Optional[int] = None
    nombre: str = ""
    tipo: str = "gasto"  # 'ingreso' o 'gasto'
    color: str = "#795548"
    presupuesto: float = 0.0


@dataclass
class Alerta:
    id: Optional[int] = None
    mensaje: str = ""
    tipo: str = "info"  # 'info', 'warning', 'error'
    fecha: date = date.today()
    leida: bool = False