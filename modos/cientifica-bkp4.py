import tkinter as tk
import operacoes_cientificas as op_cientificas

from tema import Tema
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


class CalculadoraCientifica(tk.Frame):
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
        self.pack(fill="both", expand=True)

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

        self.modo_hiperbolico = False

        self.modo_limpeza_entrada = False

        self.painel_modal_ativo: tk.Frame | None = None
        self.bind_clique_externo: str | None = None

        self.botao_seletor_ativo: tk.Button | None = None

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

        self.operacoes_hiperbolicas = {
            "sin": op_cientificas.seno_hiperbolico,
            "cos": op_cientificas.cosseno_hiperbolico,
            "tan": op_cientificas.tangente_hiperbolica,
            "sec": op_cientificas.secante_hiperbolica,
            "csc": op_cientificas.cossecante_hiperbolica,
            "cot": op_cientificas.cotangente_hiperbolica,
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
            ao_clicar_botao=self.ao_clicar,
            ao_marcar_substituicao=self._marcar_substituicao,
        )

        self._criar_interface()

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

        label_expressao = tk.Label(
            frame_visor,
            textvariable=self.texto_expressao,
            bg=Tema.COR_VISOR,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=Tema.FONTE_EXPRESSAO,
            anchor="e",
            padx=8,
        )
        label_expressao.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.visor = tk.Label(
            frame_visor,
            textvariable=self.texto_visor,
            bg=Tema.COR_VISOR,
            fg=Tema.COR_TEXTO,
            font=Tema.FONTE_VISOR,
            anchor="e",
            justify="right",
            padx=8,
        )
        self.visor.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

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

        botao_fe = self._criar_botao_texto(
            parent=frame_modos,
            texto="F-E",
            comando=lambda: self.ao_clicar("F-E"),
        )
        botao_fe.pack(
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
            command=lambda valor=texto: self.ao_clicar(valor),
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
        painel.place(
            relx=0.0,
            rely=0.31,
            relwidth=0.78,
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

        return painel

    def _criar_painel_funcoes(self) -> tk.Frame:
        painel = tk.Frame(
            self,
            bg=Tema.COR_MENU,
            bd=1,
            relief="solid",
        )

        painel.place(
            relx=0.5,
            rely=0.31,
            relwidth=0.5,
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

    def _ativar_painel_modal(self, painel: tk.Frame, botao_ativo: tk.Button) -> None:
        """
        Mantém apenas as opções do painel clicáveis.

        Um clique fora fecha o painel sem acionar o controle localizado
        abaixo dele. O próximo clique volta a funcionar normalmente.
        """
        self.painel_modal_ativo = painel
        self.botao_seletor_ativo = botao_ativo

        self._destacar_botao_seletor(botao_ativo)
        self._bloquear_botao_seletor_oposto(botao_ativo)

        painel.lift()
        botao_ativo.lift()
        painel.grab_set()

        janela = self.winfo_toplevel()
        self.bind_clique_externo = janela.bind(
            "<ButtonPress-1>",
            self._tratar_clique_com_painel_aberto,
            add="+",
        )

    def _destacar_botao_seletor(
            self,
            botao: tk.Button,
    ) -> None:
        botao.config(
            bg=Tema.COR_BOTAO,
            activebackground=Tema.COR_BOTAO_HOVER,
        )

    def _restaurar_botoes_seletores(self) -> None:
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

    def _bloquear_botao_seletor_oposto(
            self,
            botao_ativo: tk.Button,
    ) -> None:
        if botao_ativo == self.botao_trigonometria:
            botao_bloqueado = self.botao_funcoes
        else:
            botao_bloqueado = self.botao_trigonometria

        botao_bloqueado.config(
            state="disabled",
            disabledforeground=Tema.COR_TEXTO_DESATIVADO,
            cursor="arrow",
        )

    def _tratar_clique_com_painel_aberto(
        self,
        event: tk.Event,
    ) -> str | None:
        """Fecha o painel quando o clique ocorre fora de seus limites."""
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
            self._fechar_menu_funcoes()
            return "break"
        
        self._fechar_menu_funcoes()
        return "break"

    def _desativar_painel_modal(self) -> None:
        """Libera os cliques da calculadora ao fechar o painel."""
        painel = self.painel_modal_ativo

        if self._painel_existe(painel):
            try:
                if painel.grab_current() == painel:
                    painel.grab_release()
            except tk.TclError:
                pass

        if self.bind_clique_externo is not None:
            janela = self.winfo_toplevel()
            janela.unbind(
                "<ButtonPress-1>",
                self.bind_clique_externo,
            )
        
        self._restaurar_botoes_seletores()

        self.painel_modal_ativo = None
        self.botao_seletor_ativo = None
        self.bind_clique_externo = None

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

        self.ao_clicar(valor)
        self._fechar_menus_funcoes()

    def _selecionar_funcao(self, funcao: str) -> None:
        """Executa uma opção do painel de funções."""
        self.ao_clicar(funcao)
        self._fechar_menus_funcoes()

    def _alternar_trigonometria_inversa(self) -> None:
        pass

    def _alternar_trigonometria_hiperbolica(self) -> None:
        self.modo_hiperbolico = not self.modo_hiperbolico

        if self.modo_hiperbolico:
            self.botoes_trigonometria["hyp"].config(
                bg=Tema.COR_BOTAO_IGUAL,
                activebackground=Tema.COR_BOTAO_IGUAL_HOVER,
                fg="#000000",
            )

            self.botoes_trigonometria["sin"].config(text="sinh")
            self.botoes_trigonometria["cos"].config(text="cosh")
            self.botoes_trigonometria["tan"].config(text="tanh")
            self.botoes_trigonometria["sec"].config(text="sech")
            self.botoes_trigonometria["csc"].config(text="csch")
            self.botoes_trigonometria["cot"].config(text="coth")

        else:
            self.botoes_trigonometria["hyp"].config(
                bg=Tema.COR_BOTAO,
                activebackground=Tema.COR_BOTAO_HOVER,
                fg=Tema.COR_TEXTO,
            )

            self.botoes_trigonometria["sin"].config(text="sin")
            self.botoes_trigonometria["cos"].config(text="cos")
            self.botoes_trigonometria["tan"].config(text="tan")
            self.botoes_trigonometria["sec"].config(text="sec")
            self.botoes_trigonometria["csc"].config(text="csc")
            self.botoes_trigonometria["cot"].config(text="cot")

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
            self.texto_visor.set(valor)
            self.substituir_visor = False
        else:
            self.texto_visor.set(texto_atual + valor)

        self.numero_atual = float(self.texto_visor.get())

        self._mostrar_botao_ce()

    def _tratar_ponto_decimal(self) -> None:
        texto_atual = self.texto_visor.get()

        if self.substituir_visor or texto_atual == "Erro":
            self.texto_visor.set("0.")
            self.substituir_visor = False
        elif "." not in texto_atual:
            self.texto_visor.set(texto_atual + ".")
            
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

            self.texto_expressao.set(
                montar_expressao(numero)
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

            self.texto_expressao.set(
                f"{self.formatar_numero(self.mantissa_exp)}"
                f" × 10^{self.formatar_numero(expoente)}"
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
                funcao = self.operacoes_hiperbolicas[valor]
                resultado = funcao(numero)
                nome_expressao = f"{valor}h"
            else:
                funcao = self.operacoes_trigonometricas[valor]
                resultado = funcao(
                    numero,
                    self.modo_angular,
                )
                nome_expressao = valor

            self.texto_expressao.set(
                f"{nome_expressao}("
                f"{self.formatar_numero(numero)})"
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
    

    # ==========================================================
    # NÚMERO ALEATÓRIO
    # ==========================================================
    
    def _gerar_numero_aleatorio(self) -> None:
        resultado = op_cientificas.gerar_numero_aleatorio()

        self.texto_expressao.set("rand()")
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

    def fechar_paineis(self) -> None:
        """Fecha painéis temporários antes da troca de modo."""
        self._fechar_menus_funcoes()
        self.memoria.fechar_painel()
    

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

        self.visor.config(font=Tema.FONTE_VISOR)
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

    @staticmethod
    def formatar_numero(numero: float) -> str:
        numero = float(numero)
        return str(int(numero)) if numero.is_integer() else str(numero)
    
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