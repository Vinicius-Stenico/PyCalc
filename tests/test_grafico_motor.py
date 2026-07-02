import unittest

import numpy as np

from modos.grafico_motor import (
    ExpressaoInvalida,
    compilar_expressao,
)


class GraficoMotorTestes(unittest.TestCase):
    def test_funcoes_explicitas_obrigatorias(self):
        exemplos = {
            "y=x": np.array([-1.0, 0.0, 1.0]),
            "x^2": np.array([1.0, 0.0, 1.0]),
            "2x+1": np.array([-1.0, 1.0, 3.0]),
        }
        xs = np.array([-1.0, 0.0, 1.0])

        for texto, esperado in exemplos.items():
            with self.subTest(texto=texto):
                expressao = compilar_expressao(texto)
                self.assertEqual(expressao.tipo, "explicita")
                np.testing.assert_allclose(
                    expressao.avaliar_y(xs),
                    esperado,
                    equal_nan=True,
                )

    def test_funcoes_matematicas_validas(self):
        xs = np.array([1.0, 4.0, 9.0])

        self.assertEqual(compilar_expressao("sin(x)").tipo, "explicita")
        self.assertEqual(compilar_expressao("tan(x)").tipo, "explicita")
        self.assertEqual(compilar_expressao("1/x").tipo, "explicita")
        np.testing.assert_allclose(
            compilar_expressao("sqrt(x)").avaliar_y(xs),
            np.array([1.0, 2.0, 3.0]),
        )

    def test_funcoes_do_segundo_teclado_grafico(self):
        xs = np.array([0.0])

        self.assertAlmostEqual(
            compilar_expressao("root(27,3)").avaliar_y(xs)[0],
            3.0,
        )
        self.assertAlmostEqual(
            compilar_expressao("log(8,2)").avaliar_y(xs)[0],
            3.0,
        )
        self.assertAlmostEqual(
            compilar_expressao("ln(e)").avaliar_y(xs)[0],
            1.0,
        )
        self.assertAlmostEqual(
            compilar_expressao("exp(1)").avaliar_y(xs)[0],
            np.e,
        )

    def test_trigonometria_inversa_respeita_unidade_angular(self):
        xs = np.array([0.0])

        self.assertAlmostEqual(
            compilar_expressao("asin(1)").avaliar_y(xs, "graus")[0],
            90.0,
        )
        self.assertAlmostEqual(
            compilar_expressao("asec(2)").avaliar_y(xs, "graus")[0],
            60.0,
        )
        self.assertAlmostEqual(
            compilar_expressao("acot(1)").avaliar_y(xs, "graus")[0],
            45.0,
        )

    def test_funcoes_do_teclado_virtual(self):
        xs = np.array([1.0, 3.0])

        np.testing.assert_allclose(
            compilar_expressao("min(x,2)").avaliar_y(xs),
            np.array([1.0, 2.0]),
        )
        np.testing.assert_allclose(
            compilar_expressao("max(x,2)").avaliar_y(xs),
            np.array([2.0, 3.0]),
        )
        np.testing.assert_allclose(
            compilar_expressao("mod(x,2)").avaliar_y(xs),
            np.array([1.0, 1.0]),
        )
        self.assertEqual(compilar_expressao("sech(x)").tipo, "explicita")

    def test_constantes_e_operadores_unicode(self):
        xs = np.array([0.0])

        self.assertAlmostEqual(
            compilar_expressao("π").avaliar_y(xs)[0],
            np.pi,
        )
        self.assertAlmostEqual(
            compilar_expressao("2×x+1").avaliar_y(np.array([2.0]))[0],
            5.0,
        )
        self.assertAlmostEqual(
            compilar_expressao("4÷2").avaliar_y(xs)[0],
            2.0,
        )

    def test_implicita_e_desigualdade(self):
        implicita = compilar_expressao("x^2+y^2=25")
        desigualdade = compilar_expressao("y>x^2")

        self.assertEqual(implicita.tipo, "implicita")
        self.assertEqual(desigualdade.tipo, "desigualdade")
        self.assertTrue(
            desigualdade.avaliar_desigualdade(
                np.array([[0.0]]),
                np.array([[2.0]]),
            )[0, 0]
        )

    def test_rejeita_entradas_inseguras(self):
        exemplos = (
            "__import__('os')",
            "x.__class__",
            "open(x)",
            "lambda x:x",
            "abc(x)",
        )

        for texto in exemplos:
            with self.subTest(texto=texto):
                with self.assertRaises(ExpressaoInvalida):
                    compilar_expressao(texto)


if __name__ == "__main__":
    unittest.main()
