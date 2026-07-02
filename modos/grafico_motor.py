from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


TipoExpressao = Literal["explicita", "implicita", "desigualdade"]
UnidadeAngular = Literal["radianos", "graus", "grados"]

X, Y = sp.symbols("x y")

TRANSFORMACOES = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

FUNCOES_PERMITIDAS = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "asec": sp.asec,
    "acsc": sp.acsc,
    "acot": sp.acot,
    "arcsin": sp.asin,
    "arccos": sp.acos,
    "arctan": sp.atan,
    "arcsec": sp.asec,
    "arccsc": sp.acsc,
    "arccot": sp.acot,
    "asinh": sp.asinh,
    "acosh": sp.acosh,
    "atanh": sp.atanh,
    "asech": sp.asech,
    "acsch": sp.acsch,
    "acoth": sp.acoth,
    "sinh": sp.sinh,
    "cosh": sp.cosh,
    "tanh": sp.tanh,
    "sec": sp.sec,
    "csc": sp.csc,
    "cot": sp.cot,
    "sech": sp.sech,
    "csch": sp.csch,
    "coth": sp.coth,
    "sqrt": sp.sqrt,
    "root": sp.Function("root"),
    "abs": sp.Abs,
    "floor": sp.floor,
    "ceil": sp.ceiling,
    "min": sp.Min,
    "max": sp.Max,
    "mod": sp.Mod,
    "ln": sp.Function("ln"),
    "exp": sp.exp,
    # Mantido como função simbólica separada para que log seja base 10.
    "log": sp.Function("log"),
}

CONSTANTES_PERMITIDAS = {
    "x": X,
    "y": Y,
    "pi": sp.pi,
    "e": sp.E,
}

IDENTIFICADORES_PERMITIDOS = set(FUNCOES_PERMITIDAS) | set(
    CONSTANTES_PERMITIDAS
)
FUNCOES_INTERNAS_PERMITIDAS = IDENTIFICADORES_PERMITIDOS | {
    "Abs",
    "Max",
    "Min",
    "Mod",
    "ceiling",
}

LOCAL_DICT = {
    **FUNCOES_PERMITIDAS,
    **CONSTANTES_PERMITIDAS,
}

GLOBAL_DICT = {
    "__builtins__": {},
    "Add": sp.Add,
    "Integer": sp.Integer,
    "Float": sp.Float,
    "Mul": sp.Mul,
    "Pow": sp.Pow,
    "Rational": sp.Rational,
}

PADRAO_IDENTIFICADOR = re.compile(r"[A-Za-z]+")
PADRAO_DECIMAL_COM_VIRGULA = re.compile(r"(?<=\d),(?=\d)")
PADRAO_CARACTER_PROIBIDO = re.compile(r"['\"`\[\]{};:@_\\]")
PADRAO_OPERADOR_RELACIONAL = re.compile(r"(<=|>=|!=|=|<|>)")
FUNCOES_COM_VIRGULA_ARGUMENTO = {"log", "root", "min", "max", "mod"}
MARCADOR_VIRGULA_ARGUMENTO = "\ue000"


class ExpressaoInvalida(ValueError):
    """Erro controlado para entradas matemáticas inválidas."""


@dataclass
class ExpressaoCompilada:
    texto_original: str
    texto_normalizado: str
    tipo: TipoExpressao
    expressao: sp.Expr | None = None
    esquerda: sp.Expr | None = None
    direita: sp.Expr | None = None
    operador: str | None = None

    def avaliar_y(
        self,
        valores_x: np.ndarray,
        unidade_angular: UnidadeAngular = "radianos",
    ) -> np.ndarray:
        if self.tipo != "explicita" or self.expressao is None:
            raise ExpressaoInvalida("A expressão não é uma função y=f(x).")

        funcao = sp.lambdify(
            X,
            self.expressao,
            modules=[_modulo_numpy(unidade_angular), "numpy"],
        )

        with np.errstate(all="ignore"):
            valores_y = funcao(valores_x)

        if np.isscalar(valores_y):
            valores_y = np.full_like(
                valores_x,
                float(valores_y),
                dtype=float,
            )
        else:
            valores_y = np.asarray(valores_y, dtype=float)

        return _limpar_valores_invalidos(valores_y)

    def avaliar_diferenca(
        self,
        valores_x: np.ndarray,
        valores_y: np.ndarray,
        unidade_angular: UnidadeAngular = "radianos",
    ) -> np.ndarray:
        if self.esquerda is None or self.direita is None:
            raise ExpressaoInvalida("A expressão não possui dois lados.")

        diferenca = self.esquerda - self.direita
        funcao = sp.lambdify(
            (X, Y),
            diferenca,
            modules=[_modulo_numpy(unidade_angular), "numpy"],
        )

        with np.errstate(all="ignore"):
            resultado = funcao(valores_x, valores_y)

        if np.isscalar(resultado):
            resultado = np.full_like(
                valores_x,
                float(resultado),
                dtype=float,
            )
        else:
            resultado = np.asarray(resultado, dtype=float)

        return _limpar_valores_invalidos(resultado)

    def avaliar_desigualdade(
        self,
        valores_x: np.ndarray,
        valores_y: np.ndarray,
        unidade_angular: UnidadeAngular = "radianos",
    ) -> np.ndarray:
        diferenca = self.avaliar_diferenca(
            valores_x,
            valores_y,
            unidade_angular,
        )

        if self.operador == "<":
            return diferenca < 0
        if self.operador == "<=":
            return diferenca <= 0
        if self.operador == ">":
            return diferenca > 0
        if self.operador == ">=":
            return diferenca >= 0
        if self.operador == "!=":
            return np.abs(diferenca) > 1e-9

        raise ExpressaoInvalida("Operador de desigualdade inválido.")


def compilar_expressao(texto: str) -> ExpressaoCompilada:
    texto_normalizado = normalizar_texto(texto)

    operador, esquerda_texto, direita_texto = _separar_operador(
        texto_normalizado
    )

    if operador is None:
        expressao = _parsear_lado(texto_normalizado)
        _validar_variaveis(expressao, permitir_y=False)
        return ExpressaoCompilada(
            texto_original=texto,
            texto_normalizado=f"y={texto_normalizado}",
            tipo="explicita",
            expressao=expressao,
        )

    esquerda = _parsear_lado(esquerda_texto)
    direita = _parsear_lado(direita_texto)

    if operador == "=" and esquerda == Y:
        _validar_variaveis(direita, permitir_y=False)
        return ExpressaoCompilada(
            texto_original=texto,
            texto_normalizado=f"y={direita_texto}",
            tipo="explicita",
            expressao=direita,
            esquerda=esquerda,
            direita=direita,
            operador=operador,
        )

    if operador == "=" and direita == Y:
        _validar_variaveis(esquerda, permitir_y=False)
        return ExpressaoCompilada(
            texto_original=texto,
            texto_normalizado=f"y={esquerda_texto}",
            tipo="explicita",
            expressao=esquerda,
            esquerda=esquerda,
            direita=direita,
            operador=operador,
        )

    tipo: TipoExpressao = (
        "implicita" if operador == "=" else "desigualdade"
    )
    _validar_variaveis(esquerda, permitir_y=True)
    _validar_variaveis(direita, permitir_y=True)

    return ExpressaoCompilada(
        texto_original=texto,
        texto_normalizado=(
            f"{esquerda_texto}{operador}{direita_texto}"
        ),
        tipo=tipo,
        esquerda=esquerda,
        direita=direita,
        operador=operador,
    )


def normalizar_texto(texto: str) -> str:
    texto = texto.strip().lower()

    if not texto:
        raise ExpressaoInvalida("Insira uma expressão.")

    if PADRAO_CARACTER_PROIBIDO.search(texto):
        raise ExpressaoInvalida("Use apenas funções matemáticas conhecidas.")

    substituicoes = {
        "π": "pi",
        "×": "*",
        "÷": "/",
        "−": "-",
        "≤": "<=",
        "≥": ">=",
        "≠": "!=",
        "√": "sqrt",
    }

    for antigo, novo in substituicoes.items():
        texto = texto.replace(antigo, novo)

    texto = _proteger_virgulas_argumentos(texto)
    texto = PADRAO_DECIMAL_COM_VIRGULA.sub(".", texto)
    texto = texto.replace(MARCADOR_VIRGULA_ARGUMENTO, ",")
    texto = re.sub(r"\s+", "", texto)

    for identificador in PADRAO_IDENTIFICADOR.findall(texto):
        if identificador not in IDENTIFICADORES_PERMITIDOS:
            raise ExpressaoInvalida(
                f"Função ou variável desconhecida: {identificador}."
            )

    return texto


def _proteger_virgulas_argumentos(texto: str) -> str:
    resultado: list[str] = []
    pilha_funcoes_multiargumento: list[bool] = []

    for indice, caractere in enumerate(texto):
        if caractere == "(":
            anterior = indice - 1
            while anterior >= 0 and texto[anterior].isalpha():
                anterior -= 1

            nome_funcao = texto[anterior + 1 : indice]
            pilha_funcoes_multiargumento.append(
                nome_funcao in FUNCOES_COM_VIRGULA_ARGUMENTO
            )
            resultado.append(caractere)
            continue

        if caractere == ")":
            if pilha_funcoes_multiargumento:
                pilha_funcoes_multiargumento.pop()
            resultado.append(caractere)
            continue

        if (
            caractere == ","
            and pilha_funcoes_multiargumento
            and pilha_funcoes_multiargumento[-1]
        ):
            resultado.append(MARCADOR_VIRGULA_ARGUMENTO)
            continue

        resultado.append(caractere)

    return "".join(resultado)


def quebrar_descontinuidades(
    valores_y: np.ndarray,
    altura_visivel: float,
) -> np.ndarray:
    valores = np.asarray(valores_y, dtype=float).copy()
    valores = _limpar_valores_invalidos(valores)

    limite_salto = max(abs(altura_visivel) * 0.75, 25.0)
    saltos = np.abs(np.diff(valores)) > limite_salto
    if saltos.any():
        indices = np.where(saltos)[0] + 1
        valores[indices] = np.nan

    return valores


def _separar_operador(
    texto: str,
) -> tuple[str | None, str, str]:
    correspondencia = PADRAO_OPERADOR_RELACIONAL.search(texto)
    if correspondencia is None:
        return None, texto, ""

    operador = correspondencia.group(1)
    esquerda = texto[: correspondencia.start()]
    direita = texto[correspondencia.end() :]

    if not esquerda or not direita:
        raise ExpressaoInvalida("Complete os dois lados da expressão.")

    return operador, esquerda, direita


def _parsear_lado(texto: str) -> sp.Expr:
    try:
        expressao = parse_expr(
            texto,
            local_dict=LOCAL_DICT,
            global_dict=GLOBAL_DICT,
            transformations=TRANSFORMACOES,
            evaluate=False,
        )
    except Exception as exc:
        raise ExpressaoInvalida("Expressão inválida.") from exc

    if not isinstance(expressao, sp.Expr):
        raise ExpressaoInvalida("Expressão inválida.")

    for funcao in expressao.atoms(sp.Function):
        nome = funcao.func.__name__
        if nome not in FUNCOES_INTERNAS_PERMITIDAS:
            raise ExpressaoInvalida(f"Função desconhecida: {nome}.")

    return expressao


def _validar_variaveis(
    expressao: sp.Expr,
    permitir_y: bool,
) -> None:
    variaveis = expressao.free_symbols
    permitidas = {X, Y} if permitir_y else {X}
    invalidas = variaveis - permitidas

    if invalidas:
        nomes = ", ".join(sorted(str(item) for item in invalidas))
        raise ExpressaoInvalida(f"Variável desconhecida: {nomes}.")

    if not permitir_y and Y in variaveis:
        raise ExpressaoInvalida("Use y apenas em equações implícitas.")


def _limpar_valores_invalidos(valores: np.ndarray) -> np.ndarray:
    valores = np.asarray(valores, dtype=float)
    valores[~np.isfinite(valores)] = np.nan
    return valores


def _modulo_numpy(unidade_angular: UnidadeAngular) -> dict[str, object]:
    def para_radianos(valor):
        if unidade_angular == "graus":
            return np.deg2rad(valor)
        if unidade_angular == "grados":
            return np.asarray(valor) * np.pi / 200
        return valor

    def de_radianos(valor):
        if unidade_angular == "graus":
            return np.rad2deg(valor)
        if unidade_angular == "grados":
            return np.asarray(valor) * 200 / np.pi
        return valor

    def sec(valor):
        return 1 / np.cos(para_radianos(valor))

    def csc(valor):
        return 1 / np.sin(para_radianos(valor))

    def cot(valor):
        return 1 / np.tan(para_radianos(valor))

    def log(valor, base=10):
        return np.log(valor) / np.log(base)

    def root(valor, indice):
        return np.power(valor, 1 / indice)

    return {
        "sin": lambda valor: np.sin(para_radianos(valor)),
        "cos": lambda valor: np.cos(para_radianos(valor)),
        "tan": lambda valor: np.tan(para_radianos(valor)),
        "asin": lambda valor: de_radianos(np.arcsin(valor)),
        "acos": lambda valor: de_radianos(np.arccos(valor)),
        "atan": lambda valor: de_radianos(np.arctan(valor)),
        "asec": lambda valor: de_radianos(np.arccos(1 / valor)),
        "acsc": lambda valor: de_radianos(np.arcsin(1 / valor)),
        "acot": lambda valor: de_radianos(np.arctan(1 / valor)),
        "arcsin": lambda valor: de_radianos(np.arcsin(valor)),
        "arccos": lambda valor: de_radianos(np.arccos(valor)),
        "arctan": lambda valor: de_radianos(np.arctan(valor)),
        "arcsec": lambda valor: de_radianos(np.arccos(1 / valor)),
        "arccsc": lambda valor: de_radianos(np.arcsin(1 / valor)),
        "arccot": lambda valor: de_radianos(np.arctan(1 / valor)),
        "asinh": np.arcsinh,
        "acosh": np.arccosh,
        "atanh": np.arctanh,
        "asech": lambda valor: np.arccosh(1 / valor),
        "acsch": lambda valor: np.arcsinh(1 / valor),
        "acoth": lambda valor: np.arctanh(1 / valor),
        "sinh": np.sinh,
        "cosh": np.cosh,
        "tanh": np.tanh,
        "sec": sec,
        "csc": csc,
        "cot": cot,
        "sech": lambda valor: 1 / np.cosh(valor),
        "csch": lambda valor: 1 / np.sinh(valor),
        "coth": lambda valor: 1 / np.tanh(valor),
        "sqrt": np.sqrt,
        "root": root,
        "Abs": np.abs,
        "abs": np.abs,
        "floor": np.floor,
        "ceiling": np.ceil,
        "ceil": np.ceil,
        "Min": np.minimum,
        "Max": np.maximum,
        "Mod": np.mod,
        "mod": np.mod,
        "log": log,
        "ln": np.log,
        "exp": np.exp,
    }
