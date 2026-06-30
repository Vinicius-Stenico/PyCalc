from decimal import Decimal

from modos.conversor_unidades import ConversorUnidades


# Cada fator representa quantos bits existem em uma unidade.
# Os múltiplos seguem base binária, como é comum em armazenamento.
UNIDADES_DADOS = {
    "BIT": ("Bit", "bit", Decimal("1")),
    "BYTE": ("Byte", "B", Decimal("8")),
    "KILOBIT": ("Kilobit", "Kbit", Decimal("1024")),
    "KILOBYTE": ("Kilobyte", "KB", Decimal("8192")),
    "MEGABIT": ("Megabit", "Mbit", Decimal("1048576")),
    "MEGABYTE": ("Megabyte", "MB", Decimal("8388608")),
    "GIGABIT": ("Gigabit", "Gbit", Decimal("1073741824")),
    "GIGABYTE": ("Gigabyte", "GB", Decimal("8589934592")),
    "TERABIT": ("Terabit", "Tbit", Decimal("1099511627776")),
    "TERABYTE": ("Terabyte", "TB", Decimal("8796093022208")),
    "PETABIT": ("Petabit", "Pbit", Decimal("1125899906842624")),
    "PETABYTE": ("Petabyte", "PB", Decimal("9007199254740992")),
}


class CalculadoraDados(ConversorUnidades):
    """Conversor de unidades de dados."""

    UNIDADES = UNIDADES_DADOS
    UNIDADE_ORIGEM_PADRAO = "MEGABYTE"
    UNIDADE_DESTINO_PADRAO = "KILOBYTE"
