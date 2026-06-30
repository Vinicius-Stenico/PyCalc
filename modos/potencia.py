from decimal import Decimal

from modos.conversor_unidades import ConversorUnidades


# Cada fator representa quantos watts existem em uma unidade.
UNIDADES_POTENCIA = {
    "WATT": ("Watt", "W", Decimal("1")),
    "QUILOWATT": ("Quilowatt", "kW", Decimal("1000")),
    "MEGAWATT": ("Megawatt", "MW", Decimal("1000000")),
    "CAVALO_VAPOR": ("Cavalo-vapor", "cv", Decimal("735.49875")),
    "HORSEPOWER": ("Horsepower", "hp", Decimal("745.69987158227022")),
    "BTU_HORA": ("BTU por hora", "BTU/h", Decimal("0.2930710701722222")),
    "PE_LIBRA_MINUTO": ("Pé-libra por minuto", "ft⋅lb/min", Decimal("0.02259696580552333")),
    "CALORIA_SEGUNDO": ("Caloria por segundo", "cal/s", Decimal("4.184")),
}


class CalculadoraPotencia(ConversorUnidades):
    """Conversor de unidades de potência."""

    UNIDADES = UNIDADES_POTENCIA
    UNIDADE_ORIGEM_PADRAO = "WATT"
    UNIDADE_DESTINO_PADRAO = "HORSEPOWER"
