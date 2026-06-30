from decimal import Decimal

from modos.conversor_unidades import ConversorUnidades


# Cada fator representa quantos joules existem em uma unidade.
UNIDADES_ENERGIA = {
    "JOULE": ("Joule", "J", Decimal("1")),
    "QUILOJOULE": ("Quilojoule", "kJ", Decimal("1000")),
    "CALORIA": ("Caloria", "cal", Decimal("4.184")),
    "QUILOCALORIA": ("Quilocaloria", "kcal", Decimal("4184")),
    "WATT_HORA": ("Watt-hora", "Wh", Decimal("3600")),
    "QUILOWATT_HORA": ("Quilowatt-hora", "kWh", Decimal("3600000")),
    "ELETRONVOLT": ("Elétron-volt", "eV", Decimal("1.602176634e-19")),
    "BTU": ("BTU", "BTU", Decimal("1055.05585262")),
    "THERM": ("Therm", "thm", Decimal("105505585.262")),
    "PE_LIBRA": ("Pé-libra", "ft⋅lb", Decimal("1.3558179483314004")),
}


class CalculadoraEnergia(ConversorUnidades):
    """Conversor de unidades de energia."""

    UNIDADES = UNIDADES_ENERGIA
    UNIDADE_ORIGEM_PADRAO = "JOULE"
    UNIDADE_DESTINO_PADRAO = "QUILOCALORIA"
