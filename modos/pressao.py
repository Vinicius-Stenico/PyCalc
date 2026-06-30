from decimal import Decimal

from modos.conversor_unidades import ConversorUnidades


# Cada fator representa quantos pascals existem em uma unidade.
UNIDADES_PRESSAO = {
    "PASCAL": ("Pascal", "Pa", Decimal("1")),
    "QUILOPASCAL": ("Quilopascal", "kPa", Decimal("1000")),
    "MEGAPASCAL": ("Megapascal", "MPa", Decimal("1000000")),
    "BAR": ("Bar", "bar", Decimal("100000")),
    "ATMOSFERA": ("Atmosfera", "atm", Decimal("101325")),
    "TORR": ("Torr", "Torr", Decimal("133.3223684210526315789473684")),
    "MMHG": ("Milímetro de mercúrio", "mmHg", Decimal("133.322387415")),
    "INHG": ("Polegada de mercúrio", "inHg", Decimal("3386.38815789")),
    "PSI": ("Libra por polegada quadrada", "psi", Decimal("6894.757293168")),
}


class CalculadoraPressao(ConversorUnidades):
    """Conversor de unidades de pressão."""

    UNIDADES = UNIDADES_PRESSAO
    UNIDADE_ORIGEM_PADRAO = "PASCAL"
    UNIDADE_DESTINO_PADRAO = "BAR"
