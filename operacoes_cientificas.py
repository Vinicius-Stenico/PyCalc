import math
import random

PI = math.pi
E = math.e

# ==========================================================
# OPERAÇÕES UNÁRIAS
# ==========================================================

def cubo(numero: float) -> float:
    return numero ** 3

def raiz_cubica(numero: float) -> float:
    return math.copysign(abs(numero) ** (1 / 3), numero)

def valor_absoluto(numero: float) -> float:
    return abs(numero)

def fatorial(numero: float) -> float:
    if numero < 0 or not numero.is_integer():
        raise ValueError(
            "O fatorial aceita apenas inteiros não negativos."
        )
    
    return math.factorial(int(numero))

def potencia_base_dois(numero: float) -> float:
    return 2 ** numero

def potencia_base_dez(numero: float) -> float:
    return 10 ** numero

def exponencial_e(numero: float) -> float:
    return math.exp(numero)

def logaritmo_base_dez(numero: float) -> float:
    if numero <= 0:
        raise ValueError("O logaritmo exige um número positivo.")
    
    return math.log10(numero)

def logaritmo_natural(numero: float) -> float:
    if numero <= 0:
        raise ValueError("O logaritmo exige um número positivo")
    
    return math.log(numero)

def arredondar_para_baixo(numero: float) -> int:
    return math.floor(numero)

def arredondar_para_cima(numero:float) -> int:
    return math.ceil(numero)


def decimal_para_dms(numero: float) -> float:
    sinal = -1 if numero < 0 else 1
    numero = abs(numero)

    graus = math.floor(numero)
    minutos_decimais = (numero - graus) * 60
    minutos = math.floor(minutos_decimais)
    segundos = (minutos_decimais - minutos) * 60

    segundos = round(segundos, 10)

    if segundos >= 60:
        segundos -= 60
        minutos += 1

    if minutos >= 60:
        minutos -= 60
        graus += 1

    return sinal * (graus + minutos / 100 + segundos / 10000)


def dms_para_decimal(numero: float) -> float:
    sinal = -1 if numero < 0 else 1
    numero = abs(numero)

    graus = math.floor(numero)
    minutos_segundos = round((numero - graus) * 100, 10)
    minutos = math.floor(minutos_segundos)
    segundos = round((minutos_segundos - minutos) * 100, 10)

    if minutos >= 60 or segundos >= 60:
        raise ValueError(
            "O formato DMS exige minutos e segundos menores que 60."
        )

    return sinal * (graus + minutos / 60 + segundos / 3600)

# ==========================================================
# OPERAÇÕES BINÁRIAS
# ==========================================================

def potencia_xy(base: float, expoente: float) -> float:
    resultado = base ** expoente

    if isinstance(resultado, complex):
        raise ValueError(
            "O resultado não pertence aos números reais."
        )
    
    return resultado

def modulo(
        primeiro_numero: float,
        segundo_numero: float
) -> float:
    if segundo_numero == 0:
        raise ZeroDivisionError(
            "Não é possível calcular módulo por zero."
        )
    
    return primeiro_numero % segundo_numero

def raiz_indice_y(
        radicando: float,
        indice: float,
) -> float:
    if indice == 0:
        raise ValueError("O índice da raiz não pode ser zero.")
    
    if radicando == 0:
        if not indice.is_integer() or int(indice) % 2 == 0:
            raise ValueError(
                "Essa raiz não possui resultado real."
            )
        
        return -((-radicando) ** (1 / indice))
    
    return radicando ** (1 / indice)

def logaritmo_base_y(
        numero: float,
        base: float,
) -> float:
    if numero <= 0:
        raise ValueError(
            "O número do logaritmo deve ser positivo."
        )
    
    if base <=0 or base == 1:
        raise ValueError(
            "A base deve ser positiva e diferente de 1."
        )
    
    return math.log(numero, base)

def expoente_cientifico(
        mantissa: float,
        expoente: float,
) -> float:
    return mantissa * (10 ** expoente)

# ==========================================================
# CONVERSÃO ANGULAR
# ==========================================================

def converter_angulo(
        angulo: float,
        modo_angular: str,
) -> float:
    if modo_angular == "DEG":
        return math.radians(angulo)
    
    if modo_angular == "GRAD":
        return angulo * math.pi / 200
    
    if modo_angular == "RAD":
        return angulo
    
    raise ValueError("Modo angular inválido.")


def converter_de_radianos(
        angulo: float,
        modo_angular: str,
) -> float:
    if modo_angular == "DEG":
        return math.degrees(angulo)

    if modo_angular == "GRAD":
        return angulo * 200 / math.pi

    if modo_angular == "RAD":
        return angulo

    raise ValueError("Modo angular invalido.")

# ==========================================================
# TRIGONOMETRIA
# ==========================================================

def seno(angulo: float, modo_angular: str) -> float:
    return math.sin(converter_angulo(angulo, modo_angular))


def cosseno(angulo: float, modo_angular: str) -> float:
    return math.cos(converter_angulo(angulo, modo_angular))


def tangente(angulo: float, modo_angular: str) -> float:
    angulo_convertido = converter_angulo(
        angulo,
        modo_angular,
    )
    cosseno_angulo = math.cos(angulo_convertido)

    if math.isclose(cosseno_angulo, 0.0, abs_tol=1e-12):
        raise ValueError("A tangente não está definida.")

    return math.tan(angulo_convertido)


def secante(angulo: float, modo_angular: str) -> float:
    angulo_convertido = converter_angulo(
        angulo,
        modo_angular,
    )
    cosseno_angulo = math.cos(angulo_convertido)

    if math.isclose(cosseno_angulo, 0.0, abs_tol=1e-12):
        raise ValueError("A secante não está definida.")

    return 1 / cosseno_angulo


def cossecante(angulo: float, modo_angular: str) -> float:
    angulo_convertido = converter_angulo(
        angulo,
        modo_angular,
    )
    seno_angulo = math.sin(angulo_convertido)

    if math.isclose(seno_angulo, 0.0, abs_tol=1e-12):
        raise ValueError("A cossecante não está definida.")

    return 1 / seno_angulo


def cotangente(angulo: float, modo_angular: str) -> float:
    angulo_convertido = converter_angulo(
        angulo,
        modo_angular,
    )
    seno_angulo = math.sin(angulo_convertido)

    if math.isclose(seno_angulo, 0.0, abs_tol=1e-12):
        raise ValueError("A cotangente não está definida.")

    return math.cos(angulo_convertido) / seno_angulo


def arco_seno(numero: float, modo_angular: str) -> float:
    if numero < -1 or numero > 1:
        raise ValueError("O arco seno exige valor entre -1 e 1.")

    return converter_de_radianos(math.asin(numero), modo_angular)


def arco_cosseno(numero: float, modo_angular: str) -> float:
    if numero < -1 or numero > 1:
        raise ValueError("O arco cosseno exige valor entre -1 e 1.")

    return converter_de_radianos(math.acos(numero), modo_angular)


def arco_tangente(numero: float, modo_angular: str) -> float:
    return converter_de_radianos(math.atan(numero), modo_angular)


def arco_secante(numero: float, modo_angular: str) -> float:
    if -1 < numero < 1:
        raise ValueError(
            "O arco secante exige valor menor ou igual a -1 "
            "ou maior ou igual a 1."
        )

    return converter_de_radianos(math.acos(1 / numero), modo_angular)


def arco_cossecante(numero: float, modo_angular: str) -> float:
    if -1 < numero < 1:
        raise ValueError(
            "O arco cossecante exige valor menor ou igual a -1 "
            "ou maior ou igual a 1."
        )

    return converter_de_radianos(math.asin(1 / numero), modo_angular)


def arco_cotangente(numero: float, modo_angular: str) -> float:
    return converter_de_radianos(math.atan2(1, numero), modo_angular)


# ==========================================================
# FUNÇÕES HIPERBÓLICAS
# ==========================================================

def seno_hiperbolico(numero: float) -> float:
    return math.sinh(numero)


def cosseno_hiperbolico(numero: float) -> float:
    return math.cosh(numero)


def tangente_hiperbolica(numero: float) -> float:
    return math.tanh(numero)


def secante_hiperbolica(numero: float) -> float:
    return 1 / math.cosh(numero)


def cossecante_hiperbolica(numero: float) -> float:
    seno_hiperbolico_numero = math.sinh(numero)

    if math.isclose(
        seno_hiperbolico_numero,
        0.0,
        abs_tol=1e-12,
    ):
        raise ValueError(
            "A cossecante hiperbólica não está definida."
        )

    return 1 / seno_hiperbolico_numero


def cotangente_hiperbolica(numero: float) -> float:
    seno_hiperbolico_numero = math.sinh(numero)

    if math.isclose(
        seno_hiperbolico_numero,
        0.0,
        abs_tol=1e-12,
    ):
        raise ValueError(
            "A cotangente hiperbólica não está definida."
        )

    return math.cosh(numero) / seno_hiperbolico_numero


def arco_seno_hiperbolico(numero: float) -> float:
    return math.asinh(numero)


def arco_cosseno_hiperbolico(numero: float) -> float:
    if numero < 1:
        raise ValueError(
            "O arco cosseno hiperbolico exige valor maior ou igual a 1."
        )

    return math.acosh(numero)


def arco_tangente_hiperbolica(numero: float) -> float:
    if numero <= -1 or numero >= 1:
        raise ValueError(
            "O arco tangente hiperbolico exige valor entre -1 e 1."
        )

    return math.atanh(numero)


def arco_secante_hiperbolica(numero: float) -> float:
    if numero <= 0 or numero > 1:
        raise ValueError(
            "O arco secante hiperbolico exige valor maior que 0 "
            "e menor ou igual a 1."
        )

    return math.acosh(1 / numero)


def arco_cossecante_hiperbolica(numero: float) -> float:
    if numero == 0:
        raise ValueError("O arco cossecante hiperbolico nao aceita zero.")

    return math.asinh(1 / numero)


def arco_cotangente_hiperbolica(numero: float) -> float:
    if -1 <= numero <= 1:
        raise ValueError(
            "O arco cotangente hiperbolico exige valor menor que -1 "
            "ou maior que 1."
        )

    return math.atanh(1 / numero)

# ==========================================================
# ABSOLUTO
# ==========================================================

def absoluto(numero: float) -> float:
    return abs(numero)

# ==========================================================
# OUTRAS FUNÇÕES
# ==========================================================

def gerar_numero_aleatorio() -> float:
    return random.random()
