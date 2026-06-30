from decimal import Decimal

from modos.conversor_unidades import ConversorUnidades


# O fator é mantido apenas para compatibilidade com a base genérica.
UNIDADES_TEMPERATURA = {
    "CELSIUS": ("Celsius", "°C", Decimal("1")),
    "FAHRENHEIT": ("Fahrenheit", "°F", Decimal("1")),
    "KELVIN": ("Kelvin", "K", Decimal("1")),
    "RANKINE": ("Rankine", "°R", Decimal("1")),
    "REAUMUR": ("Réaumur", "°Ré", Decimal("1")),
}


class CalculadoraTemperatura(ConversorUnidades):
    """Conversor de unidades de temperatura."""

    UNIDADES = UNIDADES_TEMPERATURA
    UNIDADE_ORIGEM_PADRAO = "CELSIUS"
    UNIDADE_DESTINO_PADRAO = "FAHRENHEIT"
    PERMITE_NEGATIVO = True

    @classmethod
    def _converter_valor(
        cls,
        valor: Decimal,
        unidade_origem: str,
        unidade_destino: str,
    ) -> Decimal:
        celsius = cls._para_celsius(valor, unidade_origem)
        return cls._de_celsius(celsius, unidade_destino)

    @staticmethod
    def _para_celsius(valor: Decimal, unidade: str) -> Decimal:
        if unidade == "CELSIUS":
            return valor
        if unidade == "FAHRENHEIT":
            return (valor - Decimal("32")) * Decimal("5") / Decimal("9")
        if unidade == "KELVIN":
            return valor - Decimal("273.15")
        if unidade == "RANKINE":
            return (valor - Decimal("491.67")) * Decimal("5") / Decimal("9")
        if unidade == "REAUMUR":
            return valor * Decimal("5") / Decimal("4")

        return valor

    @staticmethod
    def _de_celsius(valor: Decimal, unidade: str) -> Decimal:
        if unidade == "CELSIUS":
            return valor
        if unidade == "FAHRENHEIT":
            return valor * Decimal("9") / Decimal("5") + Decimal("32")
        if unidade == "KELVIN":
            return valor + Decimal("273.15")
        if unidade == "RANKINE":
            return (valor + Decimal("273.15")) * Decimal("9") / Decimal("5")
        if unidade == "REAUMUR":
            return valor * Decimal("4") / Decimal("5")

        return valor
