from decimal import Decimal

from modos.conversor_unidades import ConversorUnidades


# Cada fator representa quantos metros por segundo existem em uma unidade.
UNIDADES_VELOCIDADE = {
    "CENTIMETRO_SEGUNDO": ("Centímetro por segundo", "cm/s", Decimal("0.01")),
    "METRO_SEGUNDO": ("Metro por segundo", "m/s", Decimal("1")),
    "QUILOMETRO_HORA": ("Quilômetro por hora", "km/h", Decimal("0.2777777777777777777777777778")),
    "PE_SEGUNDO": ("Pé por segundo", "ft/s", Decimal("0.3048")),
    "MILHA_HORA": ("Milha por hora", "mph", Decimal("0.44704")),
    "NO": ("Nó", "kn", Decimal("0.5144444444444444444444444444")),
    "MACH": ("Mach", "Ma", Decimal("340.29")),
}


class CalculadoraVelocidade(ConversorUnidades):
    """Conversor de unidades de velocidade."""

    UNIDADES = UNIDADES_VELOCIDADE
    UNIDADE_ORIGEM_PADRAO = "QUILOMETRO_HORA"
    UNIDADE_DESTINO_PADRAO = "METRO_SEGUNDO"
