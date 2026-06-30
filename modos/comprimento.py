from decimal import Decimal

from modos.conversor_unidades import ConversorUnidades


# Cada fator representa quantos metros existem em uma unidade.
# Estrutura: "CODIGO": ("Nome exibido", "símbolo", fator em metros)
UNIDADES_COMPRIMENTO = {
    "ANGSTROMS": ("Ångströms", "Å", Decimal("1e-10")),
    "NANOMETROS": ("Nanômetros", "nm", Decimal("1e-9")),
    "MICRONS": ("Mícrons", "μm", Decimal("1e-6")),
    "MILIMETROS": ("Milímetros", "mm", Decimal("0.001")),
    "CENTIMETROS": ("Centímetros", "cm", Decimal("0.01")),
    "METROS": ("Metros", "m", Decimal("1")),
    "QUILOMETROS": ("Quilômetros", "km", Decimal("1000")),
    "POLEGADAS": ("Polegadas", "in", Decimal("0.0254")),
    "PES": ("Pés", "ft", Decimal("0.3048")),
    "JARDAS": ("Jardas", "yd", Decimal("0.9144")),
    "MILHAS": ("Milhas", "mi", Decimal("1609.344")),
    "MILHAS_NAUTICAS": ("Milhas náuticas", "nmi", Decimal("1852")),
}

CASAS_DECIMAIS_CONVERSAO = 12


class CalculadoraComprimento(ConversorUnidades):
    """Conversor de unidades de comprimento."""

    UNIDADES = UNIDADES_COMPRIMENTO
    UNIDADE_ORIGEM_PADRAO = "CENTIMETROS"
    UNIDADE_DESTINO_PADRAO = "METROS"
    CASAS_DECIMAIS_CONVERSAO = CASAS_DECIMAIS_CONVERSAO
