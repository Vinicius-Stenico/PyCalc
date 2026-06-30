from decimal import Decimal

from modos.conversor_unidades import ConversorUnidades


PI = Decimal("3.1415926535897932384626433832795028841971693993751")

# Cada fator representa quantos radianos existem em uma unidade.
UNIDADES_ANGULO = {
    "RADIANO": ("Radiano", "rad", Decimal("1")),
    "GRAU": ("Grau", "°", PI / Decimal("180")),
    "GRADO": ("Grado", "grad", PI / Decimal("200")),
    "MINUTO_ARCO": ("Minuto de arco", "′", PI / Decimal("10800")),
    "SEGUNDO_ARCO": ("Segundo de arco", "″", PI / Decimal("648000")),
    "VOLTA": ("Volta", "volta", PI * Decimal("2")),
}


class CalculadoraAngulo(ConversorUnidades):
    """Conversor de unidades de ângulo."""

    UNIDADES = UNIDADES_ANGULO
    UNIDADE_ORIGEM_PADRAO = "GRAU"
    UNIDADE_DESTINO_PADRAO = "RADIANO"
