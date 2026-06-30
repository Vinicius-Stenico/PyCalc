from decimal import Decimal

from modos.conversor_unidades import ConversorUnidades


# Cada fator representa quantos segundos existem em uma unidade.
UNIDADES_TEMPO = {
    "NANOSEGUNDO": ("Nanossegundo", "ns", Decimal("0.000000001")),
    "MICROSSEGUNDO": ("Microssegundo", "µs", Decimal("0.000001")),
    "MILISSEGUNDO": ("Milissegundo", "ms", Decimal("0.001")),
    "SEGUNDO": ("Segundo", "s", Decimal("1")),
    "MINUTO": ("Minuto", "min", Decimal("60")),
    "HORA": ("Hora", "h", Decimal("3600")),
    "DIA": ("Dia", "d", Decimal("86400")),
    "SEMANA": ("Semana", "sem", Decimal("604800")),
    "ANO": ("Ano comum", "ano", Decimal("31536000")),
}


class CalculadoraTempo(ConversorUnidades):
    """Conversor de unidades de tempo."""

    UNIDADES = UNIDADES_TEMPO
    UNIDADE_ORIGEM_PADRAO = "HORA"
    UNIDADE_DESTINO_PADRAO = "MINUTO"
