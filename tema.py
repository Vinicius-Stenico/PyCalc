class Tema:
    """Cores e fontes compartilhadas pelos componentes da calculadora."""

    # Cores principais
    COR_FUNDO = "#1f2533"
    COR_TOPO = "#1f2533"
    COR_VISOR = "#1f2533"
    COR_BOTAO = "#2c3244"
    COR_BOTAO_HOVER = "#3a4258"
    COR_BOTAO_IGUAL = "#4cc2ff"
    COR_BOTAO_IGUAL_HOVER = "#65ccff"

    # Gráfico
    COR_GRAFICO_FUNDO = "#ffffff"
    COR_GRAFICO_GRADE = "#dddddd"
    COR_GRAFICO_EIXO = "#666666"
    COR_GRAFICO_TEXTO = "#555555"
    COR_GRAFICO_BORDA = "#c8c8c8"
    COR_GRAFICO_BARRA = "#202020"
    COR_GRAFICO_TEXTO_ESCURO = "#101820"
    CORES_CURVAS_GRAFICO = (
        "#0078d7",
        "#c239b3",
        "#10893e",
        "#ff8c00",
        "#744da9",
        "#d13438",
    )
    COR_ERRO = "#ff8080"

    # Textos
    COR_TEXTO = "#ffffff"
    COR_TEXTO_SECUNDARIO = "#aab2c5"

    # Menu lateral
    COR_MENU = "#292b2f"
    COR_MENU_HOVER = "#3a3d43"
    COR_TITULO_SECAO = "#c5c7ce"

    # Painel de memória
    COR_PAINEL_MEMORIA = "#202020"
    COR_PAINEL_MEMORIA_HOVER = "#323232"

    # Estado desativado
    COR_BOTAO_DESATIVADO = "#171b25"
    COR_TEXTO_DESATIVADO = "#555b68"

    # Fontes
    FONTE_TOPO = ("Segoe UI", 16, "bold")
    FONTE_ICONE_TOPO = ("Segoe UI Symbol", 17)
    FONTE_EXPRESSAO = ("Segoe UI", 14)
    FONTE_VISOR = ("Segoe UI", 34, "bold")
    FONTE_VISOR_ERRO_CURTO = ("Segoe UI", 20, "bold")
    FONTE_VISOR_ERRO_LONGO = ("Segoe UI", 15, "bold")
    FONTE_BOTAO = ("Segoe UI", 18)
    FONTE_BOTAO_MEMORIA = ("Segoe UI", 11)
    FONTE_MENU = ("Segoe UI", 11)
    FONTE_TITULO_MENU = ("Segoe UI", 10, "bold")

    # Aplicativo
    VERSAO_APLICACAO = "1.0.0"
    TEMA_ATUAL = "escuro"

    PALETA_ESCURO = {
        "COR_FUNDO": "#1f2533",
        "COR_TOPO": "#1f2533",
        "COR_VISOR": "#1f2533",
        "COR_BOTAO": "#2c3244",
        "COR_BOTAO_HOVER": "#3a4258",
        "COR_BOTAO_IGUAL": "#4cc2ff",
        "COR_BOTAO_IGUAL_HOVER": "#65ccff",
        "COR_GRAFICO_BARRA": "#202020",
        "COR_GRAFICO_TEXTO_ESCURO": "#101820",
        "COR_ERRO": "#ff8080",
        "COR_TEXTO": "#ffffff",
        "COR_TEXTO_SECUNDARIO": "#aab2c5",
        "COR_MENU": "#292b2f",
        "COR_MENU_HOVER": "#3a3d43",
        "COR_TITULO_SECAO": "#c5c7ce",
        "COR_PAINEL_MEMORIA": "#202020",
        "COR_PAINEL_MEMORIA_HOVER": "#323232",
        "COR_BOTAO_DESATIVADO": "#171b25",
        "COR_TEXTO_DESATIVADO": "#555b68",
    }

    PALETA_CLARO = {
        "COR_FUNDO": "#f3f3f3",
        "COR_TOPO": "#f3f3f3",
        "COR_VISOR": "#f3f3f3",
        "COR_BOTAO": "#ffffff",
        "COR_BOTAO_HOVER": "#e8e8e8",
        "COR_BOTAO_IGUAL": "#4cc2ff",
        "COR_BOTAO_IGUAL_HOVER": "#65ccff",
        "COR_GRAFICO_BARRA": "#ffffff",
        "COR_GRAFICO_TEXTO_ESCURO": "#101820",
        "COR_ERRO": "#b00020",
        "COR_TEXTO": "#111111",
        "COR_TEXTO_SECUNDARIO": "#5f6368",
        "COR_MENU": "#f8f8f8",
        "COR_MENU_HOVER": "#e9e9e9",
        "COR_TITULO_SECAO": "#666a73",
        "COR_PAINEL_MEMORIA": "#ffffff",
        "COR_PAINEL_MEMORIA_HOVER": "#ededed",
        "COR_BOTAO_DESATIVADO": "#dadde3",
        "COR_TEXTO_DESATIVADO": "#8a8f99",
    }

    CHAVES_CORES_TEMA = tuple(PALETA_ESCURO)

    @classmethod
    def aplicar(cls, nome_tema: str) -> None:
        """Aplica as cores centrais do tema informado."""
        tema = "claro" if nome_tema == "claro" else "escuro"
        paleta = cls.PALETA_CLARO if tema == "claro" else cls.PALETA_ESCURO

        for chave, valor in paleta.items():
            setattr(cls, chave, valor)

        cls.TEMA_ATUAL = tema

    @classmethod
    def cores_tema(cls) -> dict[str, str]:
        """Retorna as cores atuais usadas para atualizar widgets existentes."""
        return {
            chave: getattr(cls, chave)
            for chave in cls.CHAVES_CORES_TEMA
        }
