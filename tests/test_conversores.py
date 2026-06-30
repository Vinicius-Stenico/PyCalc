from decimal import Decimal
import unittest

from modos.angulo import CalculadoraAngulo, PI
from modos.area import CalculadoraArea
from modos.comprimento import CalculadoraComprimento
from modos.conversor_unidades import ConversorUnidades
from modos.dados import CalculadoraDados
from modos.energia import CalculadoraEnergia
from modos.peso_e_massa import CalculadoraPesoEMassa
from modos.potencia import CalculadoraPotencia
from modos.pressao import CalculadoraPressao
from modos.temperatura import CalculadoraTemperatura
from modos.tempo import CalculadoraTempo
from modos.velocidade import CalculadoraVelocidade
from modos.volume import CalculadoraVolume


class ConversorVolumeTestes(unittest.TestCase):
    def test_usa_base_generica(self):
        self.assertTrue(issubclass(CalculadoraVolume, ConversorUnidades))

    def test_fatores_metricos(self):
        self.assertEqual(
            CalculadoraVolume._fator_conversao("L", "ML"),
            Decimal("1000"),
        )
        self.assertEqual(
            CalculadoraVolume._fator_conversao("M3", "L"),
            Decimal("1000"),
        )
        self.assertEqual(
            CalculadoraVolume._fator_conversao("MM3", "L"),
            Decimal("0.000001"),
        )

    def test_fatores_imperiais_e_americanos(self):
        self.assertEqual(
            CalculadoraVolume._fator_conversao("GALAO_US", "L"),
            Decimal("3.785411784"),
        )
        self.assertEqual(
            CalculadoraVolume._fator_conversao("GALAO_UK", "L"),
            Decimal("4.54609"),
        )
        self.assertEqual(
            CalculadoraVolume._fator_conversao("ONCA_FLUIDA_UK", "ML"),
            Decimal("28.4130625"),
        )
        self.assertEqual(
            CalculadoraVolume._fator_conversao("COLHER_CHA_US", "ML"),
            Decimal("4.92892159375"),
        )

    def test_formatacao_preserva_valores_pequenos(self):
        fator = CalculadoraVolume._fator_conversao("MM3", "JARDA3")
        texto = CalculadoraVolume._formatar_decimal(fator)

        self.assertNotEqual(texto, "0")
        self.assertTrue(texto.startswith("0,0000000013"))


class ConversorComprimentoTestes(unittest.TestCase):
    def test_usa_base_generica(self):
        self.assertTrue(issubclass(CalculadoraComprimento, ConversorUnidades))

    def test_fatores_metricos(self):
        self.assertEqual(
            CalculadoraComprimento._fator_conversao("METROS", "CENTIMETROS"),
            Decimal("100"),
        )
        self.assertEqual(
            CalculadoraComprimento._fator_conversao("QUILOMETROS", "METROS"),
            Decimal("1000"),
        )
        self.assertEqual(
            CalculadoraComprimento._fator_conversao("NANOMETROS", "METROS"),
            Decimal("1E-9"),
        )

    def test_fatores_imperiais(self):
        self.assertEqual(
            CalculadoraComprimento._fator_conversao("POLEGADAS", "CENTIMETROS"),
            Decimal("2.54"),
        )
        self.assertEqual(
            CalculadoraComprimento._fator_conversao("PES", "POLEGADAS"),
            Decimal("12"),
        )
        self.assertEqual(
            CalculadoraComprimento._fator_conversao("MILHAS", "PES"),
            Decimal("5280"),
        )
        self.assertEqual(
            CalculadoraComprimento._fator_conversao("MILHAS_NAUTICAS", "QUILOMETROS"),
            Decimal("1.852"),
        )

    def test_formatacao_preserva_valores_pequenos(self):
        fator = CalculadoraComprimento._fator_conversao(
            "ANGSTROMS",
            "QUILOMETROS",
        )

        self.assertEqual(
            CalculadoraComprimento._formatar_decimal(fator),
            "1e-13",
        )


class ConversoresNovosTestes(unittest.TestCase):
    def test_peso_e_massa(self):
        self.assertTrue(issubclass(CalculadoraPesoEMassa, ConversorUnidades))
        self.assertEqual(
            CalculadoraPesoEMassa._fator_conversao("QUILOGRAMA", "GRAMA"),
            Decimal("1000"),
        )
        self.assertEqual(
            CalculadoraPesoEMassa._fator_conversao("LIBRA", "QUILOGRAMA"),
            Decimal("0.45359237"),
        )

    def test_temperatura(self):
        self.assertTrue(issubclass(CalculadoraTemperatura, ConversorUnidades))
        self.assertEqual(
            CalculadoraTemperatura._converter_valor(
                Decimal("0"),
                "CELSIUS",
                "FAHRENHEIT",
            ),
            Decimal("32"),
        )
        self.assertEqual(
            CalculadoraTemperatura._converter_valor(
                Decimal("-40"),
                "CELSIUS",
                "FAHRENHEIT",
            ),
            Decimal("-40"),
        )
        self.assertEqual(
            CalculadoraTemperatura._converter_valor(
                Decimal("100"),
                "CELSIUS",
                "KELVIN",
            ),
            Decimal("373.15"),
        )

    def test_energia_area_velocidade_tempo(self):
        self.assertEqual(
            CalculadoraEnergia._fator_conversao("QUILOWATT_HORA", "JOULE"),
            Decimal("3600000"),
        )
        self.assertEqual(
            CalculadoraArea._fator_conversao("HECTARE", "METRO2"),
            Decimal("10000"),
        )
        self.assertEqual(
            CalculadoraVelocidade._converter_valor(
                Decimal("36"),
                "QUILOMETRO_HORA",
                "METRO_SEGUNDO",
            ),
            Decimal("10.00000000000000000000000000"),
        )
        self.assertEqual(
            CalculadoraTempo._fator_conversao("HORA", "MINUTO"),
            Decimal("60"),
        )

    def test_potencia_dados_pressao_angulo(self):
        self.assertEqual(
            CalculadoraPotencia._fator_conversao("HORSEPOWER", "WATT"),
            Decimal("745.69987158227022"),
        )
        self.assertEqual(
            CalculadoraDados._fator_conversao("MEGABYTE", "KILOBYTE"),
            Decimal("1024"),
        )
        self.assertEqual(
            CalculadoraPressao._fator_conversao("ATMOSFERA", "PASCAL"),
            Decimal("101325"),
        )
        self.assertEqual(
            CalculadoraAngulo._formatar_decimal(
                CalculadoraAngulo._converter_valor(
                    Decimal("180"),
                    "GRAU",
                    "RADIANO",
                )
            ),
            CalculadoraAngulo._formatar_decimal(PI),
        )


if __name__ == "__main__":
    unittest.main()
