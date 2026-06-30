from decimal import Decimal

from modos.conversor_unidades import ConversorUnidades


# Cada fator representa quantos litros existem em uma unidade.
# Estrutura: "CODIGO": ("Nome exibido", "símbolo", fator em litros)
UNIDADES_VOLUME = {
    "ML": ("Mililitro", "mL", Decimal("0.001")),
    "CM3": ("Centímetro cúbico", "cm³", Decimal("0.001")),
    "CL": ("Centilitro", "cL", Decimal("0.01")),
    "DL": ("Decilitro", "dL", Decimal("0.1")),
    "L": ("Litro", "L", Decimal("1")),
    "DM3": ("Decímetro cúbico", "dm³", Decimal("1")),
    "DAL": ("Decalitro", "daL", Decimal("10")),
    "HL": ("Hectolitro", "hL", Decimal("100")),
    "KL": ("Quilolitro", "kL", Decimal("1000")),
    "M3": ("Metro cúbico", "m³", Decimal("1000")),
    "MM3": ("Milímetro cúbico", "mm³", Decimal("0.000001")),
    "POL3": ("Polegada cúbica", "in³", Decimal("0.016387064")),
    "PE3": ("Pé cúbico", "ft³", Decimal("28.316846592")),
    "JARDA3": ("Jarda cúbica", "yd³", Decimal("764.554857984")),
    "COLHER_CHA_US": ("Colher de chá (EUA)", "tsp", Decimal("0.00492892159375")),
    "COLHER_SOPA_US": ("Colher de sopa (EUA)", "tbsp", Decimal("0.01478676478125")),
    "ONCA_FLUIDA_US": ("Onça fluida (EUA)", "fl oz", Decimal("0.0295735295625")),
    "XICARA_US": ("Xícara (EUA)", "cup", Decimal("0.2365882365")),
    "PINT_US": ("Pint (EUA)", "pt", Decimal("0.473176473")),
    "QUART_US": ("Quart (EUA)", "qt", Decimal("0.946352946")),
    "GALAO_US": ("Galão (EUA)", "gal", Decimal("3.785411784")),
    "ONCA_FLUIDA_UK": ("Onça fluida (Reino Unido)", "fl oz", Decimal("0.0284130625")),
    "PINT_UK": ("Pint (Reino Unido)", "pt", Decimal("0.56826125")),
    "QUART_UK": ("Quart (Reino Unido)", "qt", Decimal("1.1365225")),
    "GALAO_UK": ("Galão (Reino Unido)", "gal", Decimal("4.54609")),
}

FATORES_EM_LITROS = {
    codigo: dados[2]
    for codigo, dados in UNIDADES_VOLUME.items()
}
CASAS_DECIMAIS_CONVERSAO = 12


class CalculadoraVolume(ConversorUnidades):
    """Conversor de unidades de volume."""

    UNIDADES = UNIDADES_VOLUME
    UNIDADE_ORIGEM_PADRAO = "L"
    UNIDADE_DESTINO_PADRAO = "ML"
    CASAS_DECIMAIS_CONVERSAO = CASAS_DECIMAIS_CONVERSAO
