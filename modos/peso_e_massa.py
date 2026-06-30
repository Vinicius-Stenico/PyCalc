from decimal import Decimal

from modos.conversor_unidades import ConversorUnidades


# Cada fator representa quantos quilogramas existem em uma unidade.
UNIDADES_PESO_E_MASSA = {
    "MICROGRAMA": ("Micrograma", "µg", Decimal("0.000000001")),
    "MILIGRAMA": ("Miligrama", "mg", Decimal("0.000001")),
    "GRAMA": ("Grama", "g", Decimal("0.001")),
    "QUILOGRAMA": ("Quilograma", "kg", Decimal("1")),
    "TONELADA": ("Tonelada métrica", "t", Decimal("1000")),
    "QUILATE": ("Quilate", "ct", Decimal("0.0002")),
    "ONCA": ("Onça", "oz", Decimal("0.028349523125")),
    "LIBRA": ("Libra", "lb", Decimal("0.45359237")),
    "STONE": ("Stone", "st", Decimal("6.35029318")),
    "TONELADA_CURTA": ("Tonelada curta (EUA)", "sh tn", Decimal("907.18474")),
    "TONELADA_LONGA": ("Tonelada longa (Reino Unido)", "long tn", Decimal("1016.0469088")),
}


class CalculadoraPesoEMassa(ConversorUnidades):
    """Conversor de unidades de peso e massa."""

    UNIDADES = UNIDADES_PESO_E_MASSA
    UNIDADE_ORIGEM_PADRAO = "QUILOGRAMA"
    UNIDADE_DESTINO_PADRAO = "GRAMA"
