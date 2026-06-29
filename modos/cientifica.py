import tkinter as tk
import tkinter.font as tkfont
import operacoes_cientificas as op_cientificas

from interacao_teclado_visor import InteracaoTecladoVisorMixin
from tema import Tema
from gerenciador_historico import GerenciadorHistorico
from gerenciador_memoria import GerenciadorMemoria
from operacoes import (
    dividir,
    fracao,
    multiplicar,
    potencia,
    raiz,
    somar,
    subtrair,
)

LIMITES_CARACTERES_ENTRADA = 42

TAMANHO_FONTE_VISOR_MAXIMO = 32
TAMANHO_FONTE_VISOR_MINIMO = 10
ESPACO_INTERNO_VISOR = 16

TAMANHO_FONTE_EXPRESSAO_MAXIMO = 16
TAMANHO_FONTE_EXPRESSAO_MINIMO = 6
ESPACO_INTERNO_EXPRESSAO = 8

LIMITE_CARACTERES_VISOR = 42

OPERADORES_COMUNS = {"+", "-", "×", "÷"}

OPERACOES_UNARIAS = {
    "x²",
    "√x",
    "1/x",
    "|x|",
    "n!",
    "10ˣ",
    "log",
    "ln",
    "abs",
    "⌊x⌋",
    "⌈x⌉",
    "→dms",
    "→deg",
}

OPERACOES_TRIGONOMETRICAS = {"sin", "cos", "tan", "sec", "csc", "cot"}
OPERACOES_BINARIAS_CIENTIFICAS = {"xʸ", "mod", "exp"}
CONTROLES_DE_MODO = {"2ⁿᵈ", "DEG", "RAD", "GRAD", "F-E"}
CONTROLES_DE_EXPRESSAO = {"(", ")"}
CONSTANTES = {"π", "e"}

GRADE_BOTOES_CIENTIFICA = (
    ("2ⁿᵈ", "π", "e", "C", "⌫"),
    ("x²", "1/x", "|x|", "exp", "mod"),
    ("√x", "(", ")", "n!", "÷"),
    ("xʸ", "7", "8", "9", "×"),
    ("10ˣ", "4", "5", "6", "-"),
    ("log", "1", "2", "3", "+"),
    ("ln", "+/-", "0", ".", "="),
)

BOTOES_PERMITIDOS_EM_ERRO = {
    "1", "2", "3", "4", "5",
    "6", "7", "8", "9",
    "CE", "C", "⌫", "=",
}


class CalculadoraCientifica(InteracaoTecladoVisorMixin, tk.Frame):
    """
    Interface do modo Científica.

    Este arquivo contém apenas a estrutura visual do modo:
    - visor;
    - controles DEG e F-E;
    - botões de memória;
    - menus Trigonometria e Função;
    - teclado científico.

    A janela principal, o cabeçalho e o menu lateral continuam sendo
    controlados por calculadora.py.
    """

    NOME_MODO = "Científica"

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=Tema.COR_FUNDO)

        self.botoes_trigonometria: dict[str, tk.Button] = {}

        self.frame_menu_trigonometria: tk.Frame | None = None
        self.frame_menu_funcoes: tk.Frame | None = None

        self._inicializar_estado()
        self._inicializar_mapeamentos()
        self._inicializar_mapeamentos_trigonometricos()
        self._configurar_aparencia()
        self._construir_interface()

    # ==========================================================
    # INICIALIZAÇÃO E ESTADO
    # ==========================================================

    def _inicializar_estado(self) -> None:
        self.texto_visor = tk.StringVar(value="0")
        self.texto_expressao = tk.StringVar(value="")

        self.numero_atual = 0.0
        self.operador_atual: str | None = None

        self.substituir_visor = False
        self.resultado_indefinido = False

        self.mantissa_exp: float | None = None

        self.modo_angular = "DEG"

        self.funcoes_secundarias = False
        self.trigonometria_inversa = False

        self.modo_hiperbolico = False

        self.modo_limpeza_entrada = False

        self.painel_modal_ativo: tk.Frame | None = None
        self.bind_clique_externo: str | None = None

        self.botao_seletor_ativo: tk.Button | None = None

        self.notacao_cientifica = False

        self.estados_botoes_bloqueados: dict[
            tk.Button,
            tuple[str, str],
        ] = {}

        self.botoes_principais: dict[str, tk.Button] = {}

    def _inicializar_mapeamentos(self) -> None:
        self.operacoes_unarias_primarias = {
            "x²": (
                potencia,
                lambda numero: (
                    f"sqr({self.formatar_numero(numero)})"
                ),
            ),
            "√x": (
                raiz,
                lambda numero: (
                    f"√{self.formatar_numero(numero)}"
                ),
            ),
            "1/x": (
                fracao,
                lambda numero: (
                    f"1/{self.formatar_numero(numero)}"
                ),
            ),
            "|x|": (
                op_cientificas.valor_absoluto,
                lambda numero: (
                    f"abs({self.formatar_numero(numero)})"
                ),
            ),
            "n!": (
                op_cientificas.fatorial,
                lambda numero: (
                    f"{self.formatar_numero(numero)}!"
                ),
            ),
            "10ˣ": (
                op_cientificas.potencia_base_dez,
                lambda numero: (
                    f"10^({self.formatar_numero(numero)})"
                ),
            ),
            "log": (
                op_cientificas.logaritmo_base_dez,
                lambda numero: (
                    f"log({self.formatar_numero(numero)})"
                ),
            ),
            "ln": (
                op_cientificas.logaritmo_natural,
                lambda numero: (
                    f"ln({self.formatar_numero(numero)})"
                ),
            ),
            "abs": (
                op_cientificas.valor_absoluto,
                lambda numero: (
                    f"abs({self.formatar_numero(numero)})"
                ),
            ),
            "⌊x⌋": (
                op_cientificas.arredondar_para_baixo,
                lambda numero: (
                    f"floor({self.formatar_numero(numero)})"
                ),
            ),
            "⌈x⌉": (
                op_cientificas.arredondar_para_cima,
                lambda numero: (
                    f"ceil({self.formatar_numero(numero)})"
                ),
            ),
            "→dms": (
                op_cientificas.decimal_para_dms,
                lambda numero: (
                    f"dms({self.formatar_numero(numero)})"
                ),
            ),
            "→deg": (
                op_cientificas.dms_para_decimal,
                lambda numero: (
                    f"deg({self.formatar_numero(numero)})"
                ),
            ),
        }

        self.operacoes_unarias_secundarias = {
            "x²": (
                op_cientificas.cubo,
                lambda numero: (
                    f"cube({self.formatar_numero(numero)})"
                ),
            ),
            "√x": (
                op_cientificas.raiz_cubica,
                lambda numero: (
                    f"∛{self.formatar_numero(numero)}"
                ),
            ),
            "10ˣ": (
                op_cientificas.potencia_base_dois,
                lambda numero: (
                    f"2^({self.formatar_numero(numero)})"
                ),
            ),
            "ln": (
                op_cientificas.exponencial_e,
                lambda numero: (
                    f"e^({self.formatar_numero(numero)})"
                ),
            ),
        }

        self.operacoes_binarias = {
            "+": somar,
            "-": subtrair,
            "×": multiplicar,
            "÷": self._calcular_divisao,
            "mod": op_cientificas.modulo,
            "xʸ": op_cientificas.potencia_xy,
            "ʸ√x": op_cientificas.raiz_indice_y,
            "logᵧx": op_cientificas.logaritmo_base_y,
        }

        self.operadores_cientificos_primarios = {
            "xʸ": "xʸ",
            "mod": "mod",
        }

        self.operadores_cientificos_secundarios = {
            "xʸ": "ʸ√x",
            "mod": "mod",
        }

        self.constantes = {
            "π": op_cientificas.PI,
            "e": op_cientificas.E,
        }

        self.controles_modo = {
            "2ⁿᵈ": self._alternar_funcoes_secundarias,
            "F-E": self._alternar_notacao_cientifica,
        }

        self.rotulos_funcoes_primarias = {
            "x²": "x²",
            "√x": "²√x",
            "xʸ": "xʸ",
            "10ˣ": "10ˣ",
            "log": "log",
            "ln": "ln",
        }

        self.rotulos_funcoes_secundarias = {
            "x²": "x³",
            "√x": "³√x",
            "xʸ": "ʸ√x",
            "10ˣ": "2ˣ",
            "log": "logᵧx",
            "ln": "eˣ",
        }

    def _inicializar_mapeamentos_trigonometricos(self) -> None:
        self.operacoes_trigonometricas = {
            "sin": op_cientificas.seno,
            "cos": op_cientificas.cosseno,
            "tan": op_cientificas.tangente,
            "sec": op_cientificas.secante,
            "csc": op_cientificas.cossecante,
            "cot": op_cientificas.cotangente,
        }

        self.operacoes_trigonometricas_inversas = {
            "sin": op_cientificas.arco_seno,
            "cos": op_cientificas.arco_cosseno,
            "tan": op_cientificas.arco_tangente,
            "sec": op_cientificas.arco_secante,
            "csc": op_cientificas.arco_cossecante,
            "cot": op_cientificas.arco_cotangente,
        }

        self.operacoes_hiperbolicas = {
            "sin": op_cientificas.seno_hiperbolico,
            "cos": op_cientificas.cosseno_hiperbolico,
            "tan": op_cientificas.tangente_hiperbolica,
            "sec": op_cientificas.secante_hiperbolica,
            "csc": op_cientificas.cossecante_hiperbolica,
            "cot": op_cientificas.cotangente_hiperbolica,
        }

        self.operacoes_hiperbolicas_inversas = {
            "sin": op_cientificas.arco_seno_hiperbolico,
            "cos": op_cientificas.arco_cosseno_hiperbolico,
            "tan": op_cientificas.arco_tangente_hiperbolica,
            "sec": op_cientificas.arco_secante_hiperbolica,
            "csc": op_cientificas.arco_cossecante_hiperbolica,
            "cot": op_cientificas.arco_cotangente_hiperbolica,
        }

    def _configurar_aparencia(self) -> None:
        self.master.configure(bg=Tema.COR_FUNDO)
        self.configure(bg=Tema.COR_FUNDO)

    def _construir_interface(self) -> None:
        self._configurar_layout()

        self.memoria = GerenciadorMemoria(
            parent=self,
            obter_texto_visor=self.texto_visor.get,
            ao_recuperar_valor=self._recuperar_valor_memoria,
            ao_clicar_botao=self._ao_acionar_botao_calculadora,
            ao_marcar_substituicao=self._marcar_substituicao,
        )

        self._criar_interface()

        self.historico = GerenciadorHistorico(
            parent=self,
            frame_referencia=self.memoria.frame_memoria,
            ao_recuperar_resultado=self._recuperar_valor_historico,
            ao_abrir_painel=self.memoria.fechar_painel,
        )

    # ==========================================================
    # CONSTRUÇÃO DA INTERFACE PRINCIPAL
    # ==========================================================

    def _configurar_layout(self) -> None:
        """Configura as áreas verticais do modo Científica."""
        self.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=2)  # Visor
        self.rowconfigure(1, weight=0)  # DEG e F-E
        self.rowconfigure(2, weight=0)  # Memória
        self.rowconfigure(3, weight=0)  # Trigonometria e Função
        self.rowconfigure(4, weight=7)  # Teclado

    def _criar_interface(self) -> None:
        """Cria todos os frames do modo Científica."""
        self._criar_frame_visor()
        self._criar_frame_modos_exibicao()
        self._criar_frame_memoria()
        self._criar_frame_funcoes()
        self._criar_frame_teclado()

    # ==========================================================
    # VISOR
    # ==========================================================

    def _criar_frame_visor(self) -> None:
        """Cria o frame da expressão e do valor principal."""
        frame_visor = tk.Frame(
            self,
            bg=Tema.COR_VISOR,
        )
        frame_visor.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=8,
            pady=(2, 0),
        )

        frame_visor.columnconfigure(0, weight=1)
        frame_visor.rowconfigure(0, weight=1)
        frame_visor.rowconfigure(1, weight=2)

        self.fonte_expressao_dinamica = tkfont.Font(
            font=Tema.FONTE_EXPRESSAO
        )

        self.label_expressao = tk.Label(
            frame_visor,
            textvariable=self.texto_expressao,
            bg=Tema.COR_VISOR,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=self.fonte_expressao_dinamica,
            anchor="e",
            padx=4,
        )
        self.label_expressao.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.texto_expressao.trace_add(
            "write",
            self._ao_alterar_texto_expressao,
        )

        self.fonte_visor_dinamica = tkfont.Font(
            font=Tema.FONTE_VISOR
        )

        self.visor = tk.Entry(
            frame_visor,
            textvariable=self.texto_visor,
            bg=Tema.COR_VISOR,
            fg=Tema.COR_TEXTO,
            font=self.fonte_visor_dinamica,
            justify="right",
            relief="flat",
            bd=0,
            highlightthickness=0,
            disabledbackground=Tema.COR_VISOR,
            disabledforeground=Tema.COR_TEXTO,
        )
        self.visor.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

        self.texto_visor.trace_add(
            "write",
            self._ao_alterar_texto_visor,
        )
        self._configurar_visor_editavel()

    # ==========================================================
    # DEG E F-E
    # ==========================================================

    def _criar_frame_modos_exibicao(self) -> None:
        """Cria os controles de ângulo e notação científica."""
        frame_modos = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        frame_modos.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 2),
        )

        self.botao_modo_angular = self._criar_botao_texto(
            parent=frame_modos,
            texto=self.modo_angular,
            comando=self._alterar_modo_angular,
        )
        self.botao_modo_angular.pack(
            side="left",
            padx=(2, 14),
            pady=2,
        )

        self.botao_fe = self._criar_botao_texto(
            parent=frame_modos,
            texto="F-E",
            comando=lambda: self._ao_acionar_botao_calculadora("F-E"),
        )
        self.botao_fe.pack(
            side="left",
            padx=4,
            pady=2,
        )

    # ==========================================================
    # MEMÓRIA
    # ==========================================================

    def _criar_frame_memoria(self) -> None:
        """Cria a linha de botões de memória."""
        self.memoria.criar_botoes(linha=2)

    # ==========================================================
    # TRIGONOMETRIA E FUNÇÃO
    # ==========================================================

    def _criar_frame_funcoes(self) -> None:
        """Cria os dois seletores acima do teclado."""
        self.frame_funcoes = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        self.frame_funcoes.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=8,
            pady=(0, 4),
        )

        self.frame_funcoes.columnconfigure(0, weight=1)
        self.frame_funcoes.columnconfigure(1, weight=1)

        self.botao_trigonometria = tk.Button(
            self.frame_funcoes,
            text="△  Trigonometria  ⌄",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="w",
            padx=8,
            cursor="hand2",
            command=self._alternar_menu_trigonometria,
        )
        self.botao_trigonometria.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 2),
            ipady=6,
        )

        self.botao_funcoes = tk.Button(
            self.frame_funcoes,
            text="ƒ  Função  ⌄",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="w",
            padx=8,
            cursor="hand2",
            command=self._alternar_menu_funcoes,
        )
        self.botao_funcoes.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(2, 0),
            ipady=6,
        )

    # ==========================================================
    # TECLADO
    # ==========================================================

    def _criar_frame_teclado(self) -> None:
        """Cria a grade de botões da calculadora científica."""
        frame_teclado = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        frame_teclado.grid(
            row=4,
            column=0,
            sticky="nsew",
            padx=7,
            pady=(0, 6),
        )

        for coluna in range(5):
            frame_teclado.columnconfigure(coluna, weight=1)

        for linha in range(len(GRADE_BOTOES_CIENTIFICA)):
            frame_teclado.rowconfigure(linha, weight=1)

        for linha, valores in enumerate(GRADE_BOTOES_CIENTIFICA):
            for coluna, texto in enumerate(valores):
                botao = self._criar_botao_teclado(
                    parent=frame_teclado,
                    texto=texto,
                )
                botao.grid(
                    row=linha,
                    column=coluna,
                    sticky="nsew",
                    padx=2,
                    pady=2,
                    ipady=5,
                )

                self.botoes_principais[texto] = botao

    def _criar_botao_teclado(
        self,
        parent: tk.Widget,
        texto: str,
    ) -> tk.Button:
        """Cria um botão do teclado com o estilo adequado."""
        if texto == "=":
            cor_fundo = Tema.COR_BOTAO_IGUAL
            cor_hover = Tema.COR_BOTAO_IGUAL_HOVER
            cor_texto = "#000000"
        else:
            cor_fundo = Tema.COR_BOTAO
            cor_hover = Tema.COR_BOTAO_HOVER
            cor_texto = Tema.COR_TEXTO

        return tk.Button(
            parent,
            text=texto,
            bg=cor_fundo,
            fg=cor_texto,
            activebackground=cor_hover,
            activeforeground=cor_texto,
            font=("Segoe UI", 13),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=(
                lambda valor=texto:
                self._ao_acionar_botao_calculadora(valor)
            ),
        )

    @staticmethod
    def _criar_botao_texto(
        parent: tk.Widget,
        texto: str,
        comando,
    ) -> tk.Button:
        """Cria um botão textual sem fundo destacado."""
        return tk.Button(
            parent,
            text=texto,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=comando,
        )

    # ==========================================================
    # MENUS TEMPORÁRIOS
    # ==========================================================

    def _alternar_menu_trigonometria(self) -> None:
        """Abre ou fecha o painel de funções trigonométricas."""
        if self._painel_existe(self.frame_menu_trigonometria):
            self._fechar_menus_funcoes()
            return

        self._fechar_menus_funcoes()

        self.frame_menu_trigonometria = (
            self._criar_painel_trigonometria()
        )
        self._ativar_painel_modal(
            painel=self.frame_menu_trigonometria,
            botao_ativo=self.botao_trigonometria,
        )

    def _alternar_menu_funcoes(self) -> None:
        """Abre ou fecha o painel de funções adicionais."""
        if self._painel_existe(self.frame_menu_funcoes):
            self._fechar_menus_funcoes()
            return

        self._fechar_menus_funcoes()

        self.frame_menu_funcoes = self._criar_painel_funcoes()
        self._ativar_painel_modal(
            painel=self.frame_menu_funcoes,
            botao_ativo=self.botao_funcoes,
        )

    def _criar_painel_trigonometria(self) -> tk.Frame:
        """Cria o painel com as funções trigonométricas."""
        self.botoes_trigonometria.clear()

        painel = tk.Frame(
            self,
            bg=Tema.COR_MENU,
            bd=1,
            relief="solid",
        )

        for coluna in range(4):
            painel.columnconfigure(coluna, weight=1)

        for linha in range(2):
            painel.rowconfigure(linha, weight=1)

        grupos_botoes = (
            ("2ⁿᵈ", "sin", "cos", "tan"),
            ("hyp", "sec", "csc", "cot"),
        )

        for linha, valores in enumerate(grupos_botoes):
            for coluna, texto in enumerate(valores):
                botao = tk.Button(
                    painel,
                    text=texto,
                    bg=Tema.COR_BOTAO,
                    fg=Tema.COR_TEXTO,
                    activebackground=Tema.COR_BOTAO_HOVER,
                    activeforeground=Tema.COR_TEXTO,
                    font=("Segoe UI", 10),
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                    cursor="hand2",
                    command=lambda valor=texto: (
                        self._selecionar_funcao_trigonometrica(valor)
                    ),
                )
                botao.grid(
                    row=linha,
                    column=coluna,
                    sticky="nsew",
                    padx=2,
                    pady=2,
                    ipadx=8,
                    ipady=9,
                )

                self.botoes_trigonometria[texto] = botao

        self._atualizar_botoes_trigonometria()
        return painel

    def _criar_painel_funcoes(self) -> tk.Frame:
        """Cria o painel com as funções adicionais."""
        painel = tk.Frame(
            self,
            bg=Tema.COR_MENU,
            bd=1,
            relief="solid",
        )

        for coluna in range(3):
            painel.columnconfigure(coluna, weight=1)

        for linha in range(2):
            painel.rowconfigure(linha, weight=1)

        grupos_funcoes = (
            ("|x|", "⌊x⌋", "⌈x⌉"),
            ("rand", "→dms", "→deg"),
        )

        for linha, valores in enumerate(grupos_funcoes):
            for coluna, texto in enumerate(valores):
                botao = tk.Button(
                    painel,
                    text=texto,
                    bg=Tema.COR_BOTAO,
                    fg=Tema.COR_TEXTO,
                    activebackground=Tema.COR_BOTAO_HOVER,
                    activeforeground=Tema.COR_TEXTO,
                    font=("Segoe UI", 10),
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                    cursor="hand2",
                    command=lambda valor=texto: (
                        self._selecionar_funcao(valor)
                    ),
                )
                botao.grid(
                    row=linha,
                    column=coluna,
                    sticky="nsew",
                    padx=2,
                    pady=2,
                    ipadx=8,
                    ipady=9,
                )

        return painel

    def _ativar_painel_modal(
        self,
        painel: tk.Frame,
        botao_ativo: tk.Button,
    ) -> None:
        """
        Exibe o painel abaixo do seletor e bloqueia os demais botões.

        O botão que abriu o painel e os botões internos continuam
        clicáveis. Um clique em qualquer outra parte fecha o painel.
        """
        self.painel_modal_ativo = painel
        self.botao_seletor_ativo = botao_ativo

        self._posicionar_painel_abaixo_do_botao(
            painel,
            botao_ativo,
        )
        self._destacar_botao_seletor(botao_ativo)
        self._bloquear_botoes_fora_do_painel(
            painel,
            botao_ativo,
        )

        painel.lift()
        botao_ativo.lift()

        janela = self.winfo_toplevel()
        self.bind_clique_externo = janela.bind(
            "<ButtonPress-1>",
            self._tratar_clique_com_painel_aberto,
            add="+",
        )

    def _posicionar_painel_abaixo_do_botao(
        self,
        painel: tk.Frame,
        botao: tk.Button,
    ) -> None:
        """Posiciona o painel logo abaixo do botão que o abriu."""
        self.update_idletasks()
        painel.update_idletasks()

        largura = max(
            painel.winfo_reqwidth(),
            botao.winfo_width(),
        )
        altura = painel.winfo_reqheight()

        posicao_x = (
            botao.winfo_rootx()
            - self.winfo_rootx()
        )
        posicao_y = (
            botao.winfo_rooty()
            - self.winfo_rooty()
            + botao.winfo_height()
            + 2
        )

        limite_direito = max(
            0,
            self.winfo_width() - largura - 2,
        )
        posicao_x = max(
            2,
            min(posicao_x, limite_direito),
        )

        painel.place(
            x=posicao_x,
            y=posicao_y,
            width=largura,
            height=altura,
        )

    def _destacar_botao_seletor(
        self,
        botao: tk.Button,
    ) -> None:
        """Altera a cor do seletor enquanto o painel está aberto."""
        botao.config(
            bg=Tema.COR_BOTAO,
            activebackground=Tema.COR_BOTAO_HOVER,
        )

    def _restaurar_botoes_seletores(self) -> None:
        """Restaura a aparência normal dos dois seletores."""
        for botao in (
            self.botao_trigonometria,
            self.botao_funcoes,
        ):
            botao.config(
                state="normal",
                bg=Tema.COR_FUNDO,
                activebackground=Tema.COR_BOTAO_HOVER,
                fg=Tema.COR_TEXTO,
                cursor="hand2",
            )

    def _bloquear_botoes_fora_do_painel(
        self,
        painel: tk.Frame,
        botao_ativo: tk.Button,
    ) -> None:
        """
        Bloqueia todos os botões, exceto o seletor ativo e os
        botões que pertencem ao painel aberto.
        """
        self.estados_botoes_bloqueados.clear()

        for widget in self._percorrer_widgets(self):
            if not isinstance(widget, tk.Button):
                continue

            if widget == botao_ativo:
                continue

            if self._widget_esta_dentro(widget, painel):
                continue

            estado_original = str(widget.cget("state"))
            cursor_original = str(widget.cget("cursor"))

            self.estados_botoes_bloqueados[widget] = (
                estado_original,
                cursor_original,
            )
            widget.config(
                state="disabled",
                cursor="arrow",
            )

    def _restaurar_botoes_bloqueados(self) -> None:
        """Restaura o estado que cada botão tinha antes do painel."""
        for botao, estado_anterior in (
            self.estados_botoes_bloqueados.items()
        ):
            if not botao.winfo_exists():
                continue

            estado, cursor = estado_anterior
            botao.config(
                state=estado,
                cursor=cursor,
            )

        self.estados_botoes_bloqueados.clear()

    def _tratar_clique_com_painel_aberto(
        self,
        event: tk.Event,
    ) -> str | None:
        """Fecha o painel ao clicar fora dele e do seletor ativo."""
        painel = self.painel_modal_ativo
        botao_ativo = self.botao_seletor_ativo

        if not self._painel_existe(painel):
            return None

        if self._clique_dentro_widget(event, painel):
            return None

        if (
            botao_ativo is not None
            and self._clique_dentro_widget(event, botao_ativo)
        ):
            return None

        self._fechar_menus_funcoes()
        return "break"

    def _desativar_painel_modal(self) -> None:
        """Libera os controles e remove o monitor de clique externo."""
        if self.bind_clique_externo is not None:
            janela = self.winfo_toplevel()
            janela.unbind(
                "<ButtonPress-1>",
                self.bind_clique_externo,
            )

        self._restaurar_botoes_bloqueados()
        self._restaurar_botoes_seletores()

        self.painel_modal_ativo = None
        self.botao_seletor_ativo = None
        self.bind_clique_externo = None

    @staticmethod
    def _percorrer_widgets(
        widget: tk.Widget,
    ):
        """Percorre recursivamente os componentes da calculadora."""
        for filho in widget.winfo_children():
            yield filho
            yield from CalculadoraCientifica._percorrer_widgets(
                filho
            )

    @staticmethod
    def _widget_esta_dentro(
        widget: tk.Widget,
        container: tk.Widget,
    ) -> bool:
        """Verifica se um widget pertence ao container informado."""
        widget_atual: tk.Widget | None = widget

        while widget_atual is not None:
            if widget_atual == container:
                return True

            widget_atual = getattr(
                widget_atual,
                "master",
                None,
            )

        return False

    def _selecionar_funcao_trigonometrica(
        self,
        valor: str,
    ) -> None:
        """Executa uma opção do painel de trigonometria."""
        if valor == "2ⁿᵈ":
            self._alternar_trigonometria_inversa()
            return

        if valor == "hyp":
            self._alternar_trigonometria_hiperbolica()
            return

        self._ao_acionar_botao_calculadora(valor)
        self._fechar_menus_funcoes()

    def _selecionar_funcao(self, funcao: str) -> None:
        """Executa uma opção do painel de funções."""
        self._ao_acionar_botao_calculadora(funcao)
        self._fechar_menus_funcoes()

    def _alternar_trigonometria_inversa(self) -> None:
        self.trigonometria_inversa = not self.trigonometria_inversa
        self._atualizar_botoes_trigonometria()

    def _alternar_trigonometria_hiperbolica(self) -> None:
        self.modo_hiperbolico = not self.modo_hiperbolico
        self._atualizar_botoes_trigonometria()

    def _atualizar_botoes_trigonometria(self) -> None:
        if not self.botoes_trigonometria:
            return

        botao_segundo = self.botoes_trigonometria["2ⁿᵈ"]
        botao_hyp = self.botoes_trigonometria["hyp"]

        self._configurar_botao_estado(
            botao=botao_segundo,
            ativo=self.trigonometria_inversa,
        )
        self._configurar_botao_estado(
            botao=botao_hyp,
            ativo=self.modo_hiperbolico,
        )

        if self.modo_hiperbolico:
            rotulos = {
                "sin": "sinh",
                "cos": "cosh",
                "tan": "tanh",
                "sec": "sech",
                "csc": "csch",
                "cot": "coth",
            }
        else:
            rotulos = {
                "sin": "sin",
                "cos": "cos",
                "tan": "tan",
                "sec": "sec",
                "csc": "csc",
                "cot": "cot",
            }

        if self.trigonometria_inversa:
            rotulos = {
                nome: f"{texto}⁻¹"
                for nome, texto in rotulos.items()
            }

        for nome, texto in rotulos.items():
            self.botoes_trigonometria[nome].config(text=texto)

    @staticmethod
    def _configurar_botao_estado(
        botao: tk.Button,
        ativo: bool,
    ) -> None:
        if ativo:
            botao.config(
                bg=Tema.COR_BOTAO_IGUAL,
                activebackground=Tema.COR_BOTAO_IGUAL_HOVER,
                fg="#000000",
                activeforeground="#000000",
            )
        else:
            botao.config(
                bg=Tema.COR_BOTAO,
                activebackground=Tema.COR_BOTAO_HOVER,
                fg=Tema.COR_TEXTO,
                activeforeground=Tema.COR_TEXTO,
            )

    def _fechar_menu_trigonometria(self) -> None:
        if self._painel_existe(self.frame_menu_trigonometria):
            self.frame_menu_trigonometria.destroy()

        self.frame_menu_trigonometria = None
        self.botoes_trigonometria.clear()

    def _fechar_menu_funcoes(self) -> None:
        if self._painel_existe(self.frame_menu_funcoes):
            self.frame_menu_funcoes.destroy()

        self.frame_menu_funcoes = None

    def _fechar_menus_funcoes(self) -> None:
        self._desativar_painel_modal()
        self._fechar_menu_trigonometria()
        self._fechar_menu_funcoes()

    @staticmethod
    def _painel_existe(painel: tk.Frame | None) -> bool:
        return painel is not None and bool(painel.winfo_exists())

    # ==========================================================
    # EVENTOS E ROTEAMENTO
    # ==========================================================

    def ao_clicar(self, valor: str) -> None:
        """Encaminha o clique para o grupo de ação correspondente."""
        texto_atual = self.texto_visor.get()
        expressao = self.texto_expressao.get().strip()

        if self._tratar_estado_erro_divisao(valor):
            return

        if valor != "M⌄":
            self.memoria.fechar_painel()

        self.historico.fechar_painel()

        if self.memoria.tratar_comando(valor):
            return

        if valor in OPERADORES_COMUNS:
            self._tratar_operador_comum(valor, texto_atual, expressao)
            return

        elif valor in OPERACOES_UNARIAS:
            self._tratar_operacao_unaria(valor, texto_atual, expressao)
            return
        
        elif valor in OPERACOES_BINARIAS_CIENTIFICAS:
            self._tratar_operacao_binaria_cientifica(
                valor,
                texto_atual,
                expressao,
            )
            return

        elif valor in OPERACOES_TRIGONOMETRICAS:
            self._tratar_operacao_trigonometrica(valor, texto_atual)
            return

        elif valor in CONSTANTES:
            self._tratar_constante(valor)
            return
        
        elif valor in CONTROLES_DE_MODO:
            self._tratar_controle_modo(valor)
            return

        elif valor in {"(", ")"}:
            self._tratar_parentese(valor)
            return

        elif valor == "rand":
            self._gerar_numero_aleatorio()
            return

        if self._tratar_comando_edicao(valor, texto_atual):
            return

        if valor == "=":
            self._tratar_igual(expressao)
            return

        if valor.isdigit():
            self._tratar_numero(valor)
            return

        if valor == ".":
            self._tratar_ponto_decimal()

    # ==========================================================
    # OPERADORES E NÚMEROS
    # ==========================================================

    def _tratar_operador_comum(
        self,
        operador_novo: str,
        texto_atual: str,
        expressao: str,
    ) -> None:
        if expressao:
            partes = expressao.split()

            if len(partes) >= 2:
                numero_anterior = partes[0]
                operador_anterior = partes[1]

                if self.substituir_visor:
                    self.operador_atual = operador_novo
                    self.texto_expressao.set(
                        f"{numero_anterior} {operador_novo}"
                    )
                    print(
                        "Operador alterado:",
                        operador_anterior,
                        "para",
                        operador_novo,
                    )
                    return

                resultado = self.calcular_resultado()
                if resultado is None:
                    return

                resultado_formatado = self.formatar_numero(resultado)
                self.numero_atual = float(resultado)
                self.operador_atual = operador_novo
                self.texto_expressao.set(
                    f"{resultado_formatado} {operador_novo}"
                )
                self.texto_visor.set(resultado_formatado)
                self.substituir_visor = True
                return

        if texto_atual:
            self.numero_atual = float(texto_atual)
            self.operador_atual = operador_novo
            self.texto_expressao.set(f"{texto_atual} {operador_novo}")
            self.texto_visor.set(texto_atual)
            self.substituir_visor = True

    def _tratar_numero(self, valor: str) -> None:
        texto_atual = self.texto_visor.get()

        if (
            texto_atual == "0"
            or self.substituir_visor
            or texto_atual == "Erro"
        ):
            novo_texto = valor
        else:
            novo_texto = texto_atual + valor

        if len(novo_texto) > LIMITES_CARACTERES_ENTRADA:
            return

        self.texto_visor.set(novo_texto)
        self.numero_atual = float(novo_texto)
        self.substituir_visor = False

        self._mostrar_botao_ce()

    def _tratar_ponto_decimal(self) -> None:
        texto_atual = self.texto_visor.get()

        if self.substituir_visor or texto_atual == "Erro":
            novo_texto = "0."
        
        elif "." not in texto_atual:
            novo_texto = texto_atual + "."

        else:
            return
        
        if len(novo_texto) > LIMITES_CARACTERES_ENTRADA:
            return
        
        self.texto_visor.set(novo_texto)
        self.substituir_visor = False
            
        self._mostrar_botao_ce()
    
    def _tratar_igual(self, expressao: str) -> None:
        if self.mantissa_exp is not None:
            self._calcular_expoente_cientifico()
            return

        if expressao and not self.substituir_visor:
            self.calcular_resultado()

    # ==========================================================
    # OPERAÇÕES UNÁRIAS
    # ==========================================================

    def _executar_operacao_unaria(
            self,
            texto_atual: str,
            funcao,
            montar_expressao,
    ) -> None:
        try:
            numero = float(texto_atual)
            resultado = funcao(numero)
            expressao_historico = montar_expressao(numero)

            self.texto_expressao.set(expressao_historico)
            self.historico.adicionar_expressao(
                expressao=expressao_historico,
                resultado=resultado,
            )
            self._mostrar_resultado(resultado)

        except (
            ValueError,
            TypeError,
            OverflowError,
            ZeroDivisionError,
        ):
            self._mostrar_erro()

    def _tratar_operacao_unaria(
        self,
        valor: str,
        texto_atual: str,
        expressao: str,
    ) -> None:
        if self.funcoes_secundarias and valor == "log":
            self._preparar_logaritmo_base_y(
                texto_atual,
                expressao,
            )
            return

        mapa = self.operacoes_unarias_primarias

        if (
            self.funcoes_secundarias
            and valor in self.operacoes_unarias_secundarias
        ):
            mapa = self.operacoes_unarias_secundarias

        operacao = mapa.get(valor)

        if operacao is None:
            return

        funcao, montar_expressao = operacao

        self._executar_operacao_unaria(
            texto_atual,
            funcao,
            montar_expressao,
        )

    def _preparar_logaritmo_base_y(self, texto_atual: str, expressao: str) -> None:
        self._preparar_operacao_binaria(
            "logᵧx",
            texto_atual,
            expressao,
        )


    # ==========================================================
    # OPERAÇÕES BINÁRIAS CIENTÍFICAS
    # ==========================================================

    def _tratar_operacao_binaria_cientifica(
        self,
        valor: str,
        texto_atual: str,
        expressao: str,
    ) -> None:
        if valor == "exp":
            self._tratar_expoente_cientifico(texto_atual)
            return

        mapa = self.operadores_cientificos_primarios

        if self.funcoes_secundarias:
            mapa = self.operadores_cientificos_secundarios

        operador = mapa.get(valor)

        if operador is None:
            return

        self._preparar_operacao_binaria(
            operador,
            texto_atual,
            expressao,
        )
    
    def _preparar_operacao_binaria(
        self,
        operador_novo: str,
        texto_atual: str,
        expressao: str,
    ) -> None:
        try:
            if expressao:
                partes = expressao.split()

                if len(partes) >= 2 and self.substituir_visor:
                    numero_anterior = partes[0]

                    self.operador_atual = operador_novo
                    self.texto_expressao.set(
                        f"{numero_anterior} {operador_novo}"
                    )
                    return
                
                resultado = self.calcular_resultado()

                if resultado is None:
                    return
                
                texto_atual = self.formatar_numero(resultado)

            self.numero_atual = float(texto_atual)
            self.operador_atual = operador_novo
            self.texto_expressao.set(
                f"{texto_atual} {operador_novo}"
            )
            self.texto_visor.set(texto_atual)
            self.substituir_visor = True
        
        except (ValueError, TypeError):
            self._mostrar_erro()


    def _tratar_expoente_cientifico(self, texto_atual: str) -> None:
        try:
            self.mantissa_exp = float(texto_atual)
            self.texto_expressao.set(
                f"{self.formatar_numero(self.mantissa_exp)}"
            )
            self.texto_visor.set("0")
            self.substituir_visor = False

        except (ValueError, TypeError):
            self._mostrar_erro()

    def _calcular_expoente_cientifico(self) -> float | None:
        try:
            if self.mantissa_exp is None:
                return None

            expoente = float(self.texto_visor.get())
            resultado = op_cientificas.expoente_cientifico(
                self.mantissa_exp,
                expoente,
            )
            expressao_historico = (
                f"{self.formatar_numero(self.mantissa_exp)}"
                f" × 10^{self.formatar_numero(expoente)}"
            )

            self.texto_expressao.set(expressao_historico)
            self.historico.adicionar_expressao(
                expressao=expressao_historico,
                resultado=resultado,
            )
            self.mantissa_exp = None
            self._mostrar_resultado(resultado)
            return resultado

        except (ValueError, TypeError, OverflowError):
            self._mostrar_erro()
            return None
    

    # ==========================================================
    # CONSTANTES
    # ==========================================================
    
    def _tratar_constante(self, valor: str) -> None:
        numero = self.constantes.get(valor)

        if numero is None:
            return

        self.numero_atual = numero
        self.texto_visor.set(self.formatar_numero(numero))
        self.substituir_visor = True

    # ==========================================================
    # OPERAÇÕES TRIGONOMÉTRICAS
    # ==========================================================

    def _tratar_operacao_trigonometrica(
        self,
        valor: str,
        texto_atual: str,
    ) -> None:
        try:
            numero = float(texto_atual)

            if self.modo_hiperbolico:
                if self.trigonometria_inversa:
                    funcao = self.operacoes_hiperbolicas_inversas[valor]
                    nome_expressao = f"{valor}h^-1"
                else:
                    funcao = self.operacoes_hiperbolicas[valor]
                    nome_expressao = f"{valor}h"

                resultado = funcao(numero)
            else:
                if self.trigonometria_inversa:
                    funcao = self.operacoes_trigonometricas_inversas[valor]
                    nome_expressao = f"{valor}^-1"
                else:
                    funcao = self.operacoes_trigonometricas[valor]
                    nome_expressao = valor

                resultado = funcao(
                    numero,
                    self.modo_angular,
                )

            expressao_historico = (
                f"{nome_expressao}("
                f"{self.formatar_numero(numero)})"
            )
            self.texto_expressao.set(expressao_historico)
            self.historico.adicionar_expressao(
                expressao=expressao_historico,
                resultado=resultado,
            )
            self._mostrar_resultado(resultado)

        except (
            KeyError,
            ValueError,
            TypeError,
            OverflowError,
            ZeroDivisionError,
        ):
            self._mostrar_erro()


    
    


    


    # ==========================================================
    # CONTROLADORES DE MODO
    # ==========================================================

    def _tratar_controle_modo(self, valor: str) -> None:
        comando = self.controles_modo.get(valor)

        if comando is not None:
            comando()

    def _alternar_funcoes_secundarias(self) -> None:
        self.funcoes_secundarias = not self.funcoes_secundarias

        botao_segundo = self.botoes_principais["2ⁿᵈ"]
        rotulos = self.rotulos_funcoes_primarias

        if self.funcoes_secundarias:
            rotulos = self.rotulos_funcoes_secundarias
            botao_segundo.config(
                bg=Tema.COR_BOTAO_IGUAL,
                activebackground=Tema.COR_BOTAO_IGUAL_HOVER,
                fg="#000000",
            )
        else:
            botao_segundo.config(
                bg=Tema.COR_BOTAO,
                activebackground=Tema.COR_BOTAO_HOVER,
                fg=Tema.COR_TEXTO,
            )

        for nome_botao, texto in rotulos.items():
            self.botoes_principais[nome_botao].config(text=texto)


    def _alterar_modo_angular(self) -> None:
        modos = ("DEG", "RAD", "GRAD")

        indice_atual = modos.index(self.modo_angular)
        proximo_indice = (indice_atual + 1) % len(modos)

        self.modo_angular = modos[proximo_indice]
        self.botao_modo_angular.config(text=self.modo_angular)

    def _alternar_notacao_cientifica(self) -> None:
        """Alterna o visor entre notação comum e científica"""
        try:
            numero = float(self.texto_visor.get())
        except ValueError:
            return

        self.numero_atual = numero
        self.notacao_cientifica = not self.notacao_cientifica

        self.texto_visor.set(
            self.formatar_numero(numero)
        )

        cor = (
            Tema.COR_BOTAO
            if self.notacao_cientifica
            else Tema.COR_FUNDO
        )

        self.botao_fe.config(
            bg=cor,
            activebackground=Tema.COR_BOTAO_HOVER,
        )

    # ==========================================================
    # NÚMERO ALEATÓRIO
    # ==========================================================
    
    def _gerar_numero_aleatorio(self) -> None:
        resultado = op_cientificas.gerar_numero_aleatorio()

        self.texto_expressao.set("rand()")
        self.historico.adicionar_expressao(
            expressao="rand()",
            resultado=resultado,
        )
        self._mostrar_resultado(resultado)


    # ==========================================================
    # COMANDOS DE EDIÇÃO
    # ==========================================================

    def _tratar_comando_edicao(
        self,
        valor: str,
        texto_atual: str,
    ) -> bool:
        if valor == "⌫":
            self._apagar_ultimo_digito(texto_atual)
            return True

        if valor == "C":
            if self.modo_limpeza_entrada:
                self._limpar_entrada()
                self._mostrar_botao_c()
            else:
                self._limpar_tudo()

            return True

        if valor == "CE":
            self._limpar_entrada()
            return True

        if valor == "+/-":
            self._trocar_sinal(texto_atual)
            return True

        return False
    
    def _apagar_ultimo_digito(self, texto_atual: str) -> None:
        if self.substituir_visor:
            return

        novo_texto = "0" if len(texto_atual) <= 1 else texto_atual[:-1]
        self.texto_visor.set(novo_texto)
        self.numero_atual = float(novo_texto)

    def _limpar_tudo(self) -> None:
        self.texto_visor.set("0")
        self.texto_expressao.set("")
        self.numero_atual = 0.0
        self.operador_atual = None
        self.substituir_visor = False
        self._mostrar_botao_c()

        print("Conta reiniciada")
    
    def _limpar_entrada(self) -> None:
        self.texto_visor.set("0")
        self.numero_atual = 0.0
        self.substituir_visor = False
        print("Entrada do visor limpa")
    
    def _trocar_sinal(self, texto_atual: str) -> None:
        try:
            numero = -float(texto_atual)
            self.numero_atual = numero
            self.texto_visor.set(self.formatar_numero(numero))
        except ValueError:
            self._mostrar_erro()


    # ==========================================================
    # CÁLCULOS BINÁRIOS
    # ==========================================================

    def calcular_resultado(self) -> float | None:
        try:
            partes = self.texto_expressao.get().strip().split()

            if len(partes) < 2:
                return None

            primeiro_numero = float(partes[0])
            operador = partes[1]
            segundo_numero = float(self.texto_visor.get())

            operacao = self.operacoes_binarias.get(operador)

            if operacao is None:
                return None

            resultado = operacao(
                primeiro_numero,
                segundo_numero,
            )

            if resultado is None:
                return None

            self.historico.adicionar(
                primeiro_numero=primeiro_numero,
                operador=operador,
                segundo_numero=segundo_numero,
                resultado=resultado,
            )

            self._mostrar_resultado(
                resultado,
                limpar_expressao=True,
            )
            self.operador_atual = None
            return float(resultado)

        except (
            ValueError,
            TypeError,
            IndexError,
            ZeroDivisionError,
            OverflowError,
        ):
            self._mostrar_erro()
            return None
    
    def _calcular_divisao(
        self,
        primeiro_numero: float,
        segundo_numero: float,
    ) -> float | None:
        if primeiro_numero == 0 and segundo_numero == 0:
            self._mostrar_erro_divisao(
                mensagem="Resultado indefinido",
                expressao="0 ÷",
            )
            return None

        if segundo_numero == 0:
            self._mostrar_erro_divisao(
                mensagem="Não é possível dividir por zero",
                expressao=f"{self.formatar_numero(primeiro_numero)} ÷",
            )
            return None

        return dividir(primeiro_numero, segundo_numero)
    
    def _mostrar_resultado(
        self,
        resultado: float,
        limpar_expressao: bool = False,
    ) -> None:
        self.numero_atual = float(resultado)
        self.texto_visor.set(self.formatar_numero(resultado))

        if limpar_expressao:
            self.texto_expressao.set("")

        self.substituir_visor = True


    # ==========================================================
    # INTEGRAÇÃO COM OS COMPONENTES
    # ==========================================================

    def _recuperar_valor_memoria(self, numero: float) -> None:
        self.numero_atual = float(numero)
        self.texto_visor.set(self.formatar_numero(numero))
        self.substituir_visor = True

    def _marcar_substituicao(self) -> None:
        self.substituir_visor = True

    def _recuperar_valor_historico(
        self,
        resultado: float,
    ) -> None:
        self.numero_atual = float(resultado)
        self.texto_visor.set(
            self.formatar_numero(resultado)
        )
        self.texto_expressao.set("")
        self.operador_atual = None
        self.substituir_visor = True

    def alternar_historico(self) -> None:
        """Abre ou fecha o painel de histórico do modo científico."""
        self._fechar_menus_funcoes()
        self.memoria.fechar_painel()
        self.historico.alternar_painel()

    def fechar_paineis(self) -> None:
        """Fecha painéis temporários antes da troca de modo."""
        self._fechar_menus_funcoes()
        self.memoria.fechar_painel()
        self.historico.fechar_painel()
    

    # ==========================================================
    # ESTADOS DE ERRO
    # ==========================================================

    def _tratar_estado_erro_divisao(self, valor: str) -> bool:
        if not self.resultado_indefinido:
            return False

        if valor in {"1", "2", "3", "4", "5", "6", "7", "8", "9"}:
            self._limpar_resultado_indefinido(valor)
            return True

        if valor in {"=", "CE", "C", "⌫"}:
            self._limpar_resultado_indefinido("0")
            return True

        return True
    
    def _mostrar_erro_divisao(
        self,
        mensagem: str,
        expressao: str,
    ) -> None:
        self.texto_visor.set(mensagem)
        self.texto_expressao.set(expressao)
        self.resultado_indefinido = True
        self.substituir_visor = True

        fonte = (
            Tema.FONTE_VISOR_ERRO_CURTO
            if mensagem == "Resultado indefinido"
            else Tema.FONTE_VISOR_ERRO_LONGO
        )
        self.visor.config(font=fonte)

        self._bloquear_botoes_erro()

    def _limpar_resultado_indefinido(
        self,
        novo_valor: str = "0",
    ) -> None:
        self.texto_visor.set(novo_valor)
        self.texto_expressao.set("")
        self.numero_atual = float(novo_valor)
        self.operador_atual = None
        self.resultado_indefinido = False
        self.substituir_visor = False

        self.visor.config(font=self.fonte_visor_dinamica)
        self._ajustar_fonte_visor()
        self._desbloquear_botoes_erro()

    def _bloquear_botoes_erro(self) -> None:
        for nome, botao in self.botoes_principais.items():
            if nome in BOTOES_PERMITIDOS_EM_ERRO:
                botao.config(state="normal")
            else:
                botao.config(
                    state="disabled",
                    bg=Tema.COR_BOTAO_DESATIVADO,
                    disabledforeground=Tema.COR_TEXTO_DESATIVADO,
                )

        self.memoria.bloquear_por_erro()

    def _desbloquear_botoes_erro(self) -> None:
        for nome, botao in self.botoes_principais.items():
            if nome == "=":
                botao.config(
                    state="normal",
                    bg=Tema.COR_BOTAO_IGUAL,
                    fg="#000000",
                    disabledforeground="#000000",
                )
            else:
                botao.config(
                    state="normal",
                    bg=Tema.COR_BOTAO,
                    fg=Tema.COR_TEXTO,
                    disabledforeground=Tema.COR_TEXTO,
                )

        self.memoria.desbloquear_apos_erro()

    def _mostrar_erro(self) -> None:
        self.texto_visor.set("Erro")
        self.texto_expressao.set("")
        self.operador_atual = None
        self.substituir_visor = True


    # ==========================================================
    # BOTÕES
    # ==========================================================

    def _mostrar_botao_ce(self) -> None:
        self.modo_limpeza_entrada = True
        self.botoes_principais["C"].config(text="CE")

    def _mostrar_botao_c(self) -> None:
        self.modo_limpeza_entrada = False
        self.botoes_principais["C"].config(text="C")


    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    def formatar_numero(self, numero: float) -> str:
        numero = float(numero)

        if self.notacao_cientifica:
            return self._formatar_notacao_cientifica(numero)

        return self._formatar_notacao_normal(numero)
        
    @staticmethod
    def _formatar_notacao_cientifica(numero: float) -> str:
        if numero == 0:
            return "0e+0"

        texto = f"{numero:.14e}"
        mantissa, expoente = texto.split("e")

        mantissa = mantissa.rstrip("0").rstrip(".")
        expoente = int(expoente)

        return f"{mantissa}e{expoente:+d}"
    
    @staticmethod
    def _formatar_notacao_normal(numero: float) -> str:
        if numero.is_integer():
            return str(int(numero))

        return format(numero, ".15g")
        
    @staticmethod
    def _clique_dentro_widget(
        event: tk.Event,
        widget: tk.Widget,
    ) -> bool:
        widget.update_idletasks()

        esquerda = widget.winfo_rootx()
        topo = widget.winfo_rooty()
        direita = esquerda + widget.winfo_width()
        inferior = topo + widget.winfo_height()

        return (
            esquerda <= event.x_root < direita
            and topo <= event.y_root < inferior
        )
    
    def _ao_alterar_texto_visor(self, *args) -> None:
        """Agenda o ajuste da fonte após o visor ser atualizado."""
        self.after_idle(self._ajustar_fonte_visor)

    def _ajustar_fonte_visor(self) -> None:
        """Reduz ou aumenta a fonte para manter o texto dentro do visor."""
        if not hasattr(self, "visor"):
            return
        
        if not hasattr(self, "fonte_visor_dinamica"):
            return
        
        # Os erros de divisão já usam fontes especiais.
        if self.resultado_indefinido:
            return
        
        texto = self.texto_visor.get()

        self.visor.update_idletasks()

        largura_disponivel = (
            self.visor.winfo_width()
            - ESPACO_INTERNO_VISOR
        )

        if largura_disponivel <= 1:
            return
        
        tamanho = TAMANHO_FONTE_VISOR_MAXIMO

        self.fonte_visor_dinamica.configure(size=tamanho)

        while (
            tamanho > TAMANHO_FONTE_VISOR_MINIMO
            and self.fonte_visor_dinamica.measure(texto)
            > largura_disponivel
        ):
            tamanho -= 1
            self.fonte_visor_dinamica.configure(size=tamanho)

    def _ao_alterar_texto_expressao(self, *_args) -> None:
        self.after_idle(self._ajustar_fonte_expressao)

    def _ajustar_fonte_expressao(self) -> None:
        if not hasattr(self, "label_expressao"):
            return

        texto = self.texto_expressao.get()

        self.label_expressao.update_idletasks()

        largura_disponivel = (
            self.label_expressao.winfo_width()
            - ESPACO_INTERNO_EXPRESSAO
        )

        if largura_disponivel <= 1:
            return

        tamanho = TAMANHO_FONTE_EXPRESSAO_MAXIMO

        while tamanho >= TAMANHO_FONTE_EXPRESSAO_MINIMO:
            self.fonte_expressao_dinamica.configure(
                size=tamanho
            )

            if (
                self.fonte_expressao_dinamica.measure(texto)
                <= largura_disponivel
            ):
                return

            tamanho -= 1

        self.fonte_expressao_dinamica.configure(
            size=TAMANHO_FONTE_EXPRESSAO_MINIMO
        )
        
