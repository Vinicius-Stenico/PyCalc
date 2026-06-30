from decimal import Decimal

from modos.conversor_unidades import ConversorUnidades


# Cada fator representa quantos metros quadrados existem em uma unidade.
UNIDADES_AREA = {
    "MILIMETRO2": ("Milímetro quadrado", "mm²", Decimal("0.000001")),
    "CENTIMETRO2": ("Centímetro quadrado", "cm²", Decimal("0.0001")),
    "METRO2": ("Metro quadrado", "m²", Decimal("1")),
    "QUILOMETRO2": ("Quilômetro quadrado", "km²", Decimal("1000000")),
    "HECTARE": ("Hectare", "ha", Decimal("10000")),
    "ACRE": ("Acre", "ac", Decimal("4046.8564224")),
    "POLEGADA2": ("Polegada quadrada", "in²", Decimal("0.00064516")),
    "PE2": ("Pé quadrado", "ft²", Decimal("0.09290304")),
    "JARDA2": ("Jarda quadrada", "yd²", Decimal("0.83612736")),
    "MILHA2": ("Milha quadrada", "mi²", Decimal("2589988.110336")),
}


class CalculadoraArea(ConversorUnidades):
    """Conversor de unidades de área."""

    UNIDADES = UNIDADES_AREA
    UNIDADE_ORIGEM_PADRAO = "METRO2"
    UNIDADE_DESTINO_PADRAO = "CENTIMETRO2"
