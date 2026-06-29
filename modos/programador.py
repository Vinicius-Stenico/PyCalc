import tkinter as tk
import tkinter.font as tkfont

from tema import Tema


BASES = {
    "HEX": 16,
    "DEC": 10,
    "OCT": 8,
    "BIN": 2,
}

WORD_SIZES = {
    "QWORD": 64,
    "DWORD": 32,
    "WORD": 16,
    "BYTE": 8,
}

OPERADORES_BINARIOS = {
    "+",
    "-",
    "×",
    "÷",
    "%",
    "AND",
    "OR",
    "NAND",
    "NOR",
    "XOR",
    "<<",
    ">>",
}

GRADE_BOTOES_PROGRAMADOR = (
    ("A", "<<", ">>", "C", "⌫"),
    ("B", "(", ")", "%", "÷"),
    ("C", "7", "8", "9", "×"),
    ("D", "4", "5", "6", "-"),
    ("E", "1", "2", "3", "+"),
    ("F", "+/-", "0", ",", "="),
)

TAMANHO_FONTE_VISOR_MAXIMO = 34
TAMANHO_FONTE_VISOR_MINIMO = 5
ESPACO_INTERNO_VISOR = 12


class CalculadoraProgramador(tk.Frame):
    """Modo Programador da calculadora."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=Tema.COR_FUNDO)

        self.base_atual = "DEC"
        self.tamanho_palavra = "QWORD"
        self.valor_atual = 0
        self.entrada_atual = "0"
        self.substituir_visor = True
        self.modo_limpeza_entrada = False
        self.modo_deslocamento = "aritmetico"
        self.bit_transporte = 0
        self.visualizacao_atual = "teclado"

        self.primeiro_operando: int | None = None
        self.operador_atual: str | None = None
        self.texto_primeiro_operando: str | None = None
        self.texto_operando_atual: str | None = None
        self.prefixo_expressao = ""
        self.pilha_parenteses: list[
            tuple[
                int | None,
                str | None,
                str | None,
                str | None,
                str,
                str,
            ]
        ] = []
        self.texto_expressao = tk.StringVar(value="")
        self.texto_visor = tk.StringVar(value="0")

        self.labels_bases: dict[str, tk.Label] = {}
        self.botoes_bases: dict[str, tk.Button] = {}
        self.botoes_principais: dict[str, tk.Button] = {}
        self.indicador_teclado: tk.Frame | None = None
        self.indicador_bits: tk.Frame | None = None
        self.frame_teclado: tk.Frame | None = None
        self.frame_bits: tk.Frame | None = None
        self.frame_menus: tk.Frame | None = None
        self.botoes_bits: dict[int, tk.Button] = {}
        self.frame_menu_bitwise: tk.Frame | None = None
        self.frame_menu_shift: tk.Frame | None = None
        self.frame_menu_word: tk.Frame | None = None
        self.frame_menu_memoria: tk.Frame | None = None
        self.memoria_valores: list[int] = []
        self._estado_sombra_memoria: list[
            tuple[tk.Widget, dict[str, str]]
        ] = []
        self._bind_clique_fora_memoria: str | None = None

        self._configurar_layout()
        self._criar_interface()
        self._atualizar_tela()

    # ==========================================================
    # CONSTRUÇÃO
    # ==========================================================

    def _configurar_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=1)

    def _criar_interface(self) -> None:
        self._criar_visor()
        self._criar_linhas_bases()
        self._criar_barra_modos()
        self._criar_menus_operacao()
        self._criar_area_inferior()

    def _criar_area_inferior(self) -> None:
        self.frame_area_inferior = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        self.frame_area_inferior.grid(
            row=4,
            column=0,
            sticky="nsew",
        )
        self.frame_area_inferior.columnconfigure(0, weight=1)
        self.frame_area_inferior.rowconfigure(0, weight=1)

        self._criar_teclado()
        self._criar_visualizacao_bits()

    def _criar_visor(self) -> None:
        frame_visor = tk.Frame(
            self,
            bg=Tema.COR_VISOR,
        )
        frame_visor.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=(18, 6),
        )
        frame_visor.grid_propagate(False)
        frame_visor.configure(height=78)
        frame_visor.columnconfigure(0, weight=1)
        frame_visor.rowconfigure(0, minsize=22, weight=0)
        frame_visor.rowconfigure(1, minsize=56, weight=1)

        label_expressao = tk.Label(
            frame_visor,
            textvariable=self.texto_expressao,
            bg=Tema.COR_VISOR,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=Tema.FONTE_EXPRESSAO,
            anchor="e",
        )
        label_expressao.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        self.fonte_visor_dinamica = tkfont.Font(
            font=Tema.FONTE_VISOR
        )

        self.label_visor = tk.Label(
            frame_visor,
            textvariable=self.texto_visor,
            bg=Tema.COR_VISOR,
            fg=Tema.COR_TEXTO,
            font=self.fonte_visor_dinamica,
            anchor="e",
            padx=2,
        )
        self.label_visor.grid(
            row=1,
            column=0,
            sticky="nsew",
        )
        self.texto_visor.trace_add(
            "write",
            self._ao_alterar_texto_visor,
        )

    def _criar_linhas_bases(self) -> None:
        frame_bases = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        frame_bases.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 8),
        )
        frame_bases.columnconfigure(1, weight=1)

        for linha, base in enumerate(("HEX", "DEC", "OCT", "BIN")):
            botao = tk.Button(
                frame_bases,
                text=base,
                bg=Tema.COR_FUNDO,
                fg=Tema.COR_TEXTO,
                activebackground=Tema.COR_BOTAO_HOVER,
                activeforeground=Tema.COR_TEXTO,
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                bd=0,
                highlightthickness=0,
                anchor="w",
                padx=6,
                pady=2,
                cursor="hand2",
                command=lambda valor=base: self._selecionar_base(valor),
            )
            botao.grid(
                row=linha,
                column=0,
                sticky="ew",
                padx=(0, 8),
            )

            label = tk.Label(
                frame_bases,
                text="0",
                bg=Tema.COR_FUNDO,
                fg=Tema.COR_TEXTO,
                font=("Segoe UI", 9),
                anchor="w",
            )
            label.grid(
                row=linha,
                column=1,
                sticky="ew",
            )

            self.botoes_bases[base] = botao
            self.labels_bases[base] = label

    def _criar_barra_modos(self) -> None:
        frame_barra = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        frame_barra.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 4),
        )
        for coluna in range(5):
            frame_barra.columnconfigure(coluna, weight=1)

        self.botao_teclado, self.indicador_teclado = (
            self._criar_botao_barra_com_indicador(
                frame_barra,
                "▦",
                lambda: self._selecionar_visualizacao("teclado"),
            )
        )
        self.botao_teclado.grid(row=0, column=0, sticky="ew")

        self.botao_bits, self.indicador_bits = (
            self._criar_botao_barra_com_indicador(
                frame_barra,
                "▥",
                lambda: self._selecionar_visualizacao("bits"),
            )
        )
        self.botao_bits.grid(row=0, column=1, sticky="ew")

        self.botao_word = self._criar_botao_barra(
            frame_barra,
            self.tamanho_palavra,
            self._alternar_word_size,
        )
        self.botao_word.grid(row=0, column=2, sticky="ew")

        self.botao_memoria = self._criar_botao_barra(
            frame_barra,
            "MS",
            self._salvar_memoria,
        )
        self.botao_memoria.grid(row=0, column=3, sticky="ew")

        self.botao_memoria_menu = self._criar_botao_barra(
            frame_barra,
            "M⌄",
            self._alternar_menu_memoria,
        )
        self.botao_memoria_menu.config(
            font=Tema.FONTE_BOTAO_MEMORIA,
            fg=Tema.COR_TEXTO_DESATIVADO,
            disabledforeground=Tema.COR_TEXTO_DESATIVADO,
        )
        self.botao_memoria_menu.grid(row=0, column=4, sticky="ew")

    def _criar_menus_operacao(self) -> None:
        frame_menus = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        self.frame_menus = frame_menus
        frame_menus.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 5),
        )
        frame_menus.columnconfigure(0, weight=1)
        frame_menus.columnconfigure(1, weight=1)

        self.botao_bitwise = self._criar_botao_menu(
            frame_menus,
            "Bit a bit  ⌄",
            self._alternar_menu_bitwise,
        )
        self.botao_bitwise.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 4),
        )

        self.botao_shift = self._criar_botao_menu(
            frame_menus,
            "Deslocamento de bit  ⌄",
            self._alternar_menu_shift,
        )
        self.botao_shift.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(4, 0),
        )

    def _criar_teclado(self) -> None:
        frame_teclado = tk.Frame(
            self.frame_area_inferior,
            bg=Tema.COR_FUNDO,
        )
        frame_teclado.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=7,
            pady=(0, 6),
        )
        frame_teclado.grid_propagate(False)
        self.frame_teclado = frame_teclado

        for coluna in range(5):
            frame_teclado.columnconfigure(
                coluna,
                weight=1,
                uniform="teclado_programador",
                minsize=58,
            )

        for linha in range(len(GRADE_BOTOES_PROGRAMADOR)):
            frame_teclado.rowconfigure(linha, weight=1)

        for linha, valores in enumerate(GRADE_BOTOES_PROGRAMADOR):
            for coluna, texto in enumerate(valores):
                acao = texto
                if coluna == 0 and texto in "ABCDEF":
                    acao = f"DIGIT_{texto}"

                botao = self._criar_botao_teclado(
                    frame_teclado,
                    texto,
                    acao,
                )
                botao.grid(
                    row=linha,
                    column=coluna,
                    sticky="nsew",
                    padx=2,
                    pady=2,
                    ipady=8,
                )
                self.botoes_principais[acao] = botao

    def _criar_visualizacao_bits(self) -> None:
        frame_bits = tk.Frame(
            self.frame_area_inferior,
            bg=Tema.COR_FUNDO,
        )
        frame_bits.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        self.frame_bits = frame_bits

        for coluna in range(4):
            frame_bits.columnconfigure(coluna, weight=1)

        for linha in range(8):
            frame_bits.rowconfigure(linha, weight=1)

        self.botoes_bits.clear()

        grupos = (
            (60, 56, 52, 48),
            (44, 40, 36, 32),
            (28, 24, 20, 16),
            (12, 8, 4, 0),
        )

        for linha, valores in enumerate(grupos):
            for coluna, inicio in enumerate(valores):
                frame_grupo = tk.Frame(
                    frame_bits,
                    bg=Tema.COR_FUNDO,
                )
                frame_grupo.grid(
                    row=linha * 2,
                    column=coluna,
                    sticky="nsew",
                    padx=4,
                    pady=(4, 0),
                )
                for coluna_bit in range(4):
                    frame_grupo.columnconfigure(coluna_bit, weight=1)

                for deslocamento in range(4):
                    bit = inicio + 3 - deslocamento
                    botao_bit = tk.Button(
                        frame_grupo,
                        text="0",
                        bg=Tema.COR_FUNDO,
                        fg=Tema.COR_TEXTO,
                        activebackground=Tema.COR_BOTAO_HOVER,
                        activeforeground=Tema.COR_TEXTO,
                        font=("Consolas", 18, "bold"),
                        relief="flat",
                        bd=0,
                        highlightthickness=0,
                        padx=0,
                        pady=0,
                        cursor="hand2",
                        command=lambda posicao=bit: (
                            self._alternar_bit(posicao)
                        ),
                    )
                    botao_bit.grid(
                        row=0,
                        column=deslocamento,
                        sticky="nsew",
                    )
                    self.botoes_bits[bit] = botao_bit

                label_indice = tk.Label(
                    frame_bits,
                    text=str(inicio),
                    bg=Tema.COR_FUNDO,
                    fg=Tema.COR_TEXTO_SECUNDARIO,
                    font=("Segoe UI", 8),
                    anchor="center",
                )
                label_indice.grid(
                    row=linha * 2 + 1,
                    column=coluna,
                    sticky="ew",
                    padx=3,
                    pady=(0, 12),
                )

    def _criar_botao_teclado(
        self,
        parent: tk.Widget,
        texto: str,
        acao: str,
    ) -> tk.Button:
        cor_fundo = Tema.COR_BOTAO_IGUAL if texto == "=" else Tema.COR_BOTAO
        cor_hover = (
            Tema.COR_BOTAO_IGUAL_HOVER
            if texto == "="
            else Tema.COR_BOTAO_HOVER
        )
        cor_texto = "#000000" if texto == "=" else Tema.COR_TEXTO

        return tk.Button(
            parent,
            text=texto,
            bg=cor_fundo,
            fg=cor_texto,
            activebackground=cor_hover,
            activeforeground=cor_texto,
            font=("Segoe UI", 13),
            width=4,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=lambda valor=acao: self.ao_clicar(valor),
        )

    @staticmethod
    def _criar_botao_barra(
        parent: tk.Widget,
        texto: str,
        comando,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=texto,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=comando,
        )

    def _criar_botao_barra_com_indicador(
        self,
        parent: tk.Widget,
        texto: str,
        comando,
    ) -> tuple[tk.Frame, tk.Frame]:
        container = tk.Frame(
            parent,
            bg=Tema.COR_FUNDO,
        )
        container.columnconfigure(0, weight=1)

        botao = tk.Button(
            container,
            text=texto,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=comando,
        )
        botao.grid(row=0, column=0, sticky="ew")

        indicador = tk.Frame(
            container,
            bg=Tema.COR_BOTAO_IGUAL,
            height=3,
        )
        indicador.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=18,
        )

        return container, indicador

    @staticmethod
    def _criar_botao_menu(
        parent: tk.Widget,
        texto: str,
        comando,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=texto,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 9),
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="w",
            padx=4,
            pady=6,
            cursor="hand2",
            command=comando,
        )

    # ==========================================================
    # EVENTOS
    # ==========================================================

    def ao_clicar(self, valor: str) -> None:
        self.fechar_paineis()

        if valor.startswith("DIGIT_"):
            digito = valor.removeprefix("DIGIT_")
            if digito in self._digitos_validos():
                self._inserir_digito(digito)
            return

        if valor == "(":
            self._abrir_parentese()
            return

        if valor == ")":
            self._fechar_parentese()
            return

        if valor == "C":
            if self.modo_limpeza_entrada:
                self._limpar_entrada()
                return

            self._limpar_tudo()
            return

        if valor == "CE":
            self._limpar_entrada()
            return

        if valor in self._digitos_validos():
            self._inserir_digito(valor)
            return

        if valor in OPERADORES_BINARIOS:
            self._preparar_operador(valor)
            return

        if valor == "=":
            self._calcular_resultado()
            return

        if valor == "⌫":
            self._apagar_ultimo()
            return

        if valor == "+/-":
            self._trocar_sinal()
            return

        if valor == "NOT":
            self._aplicar_not()

    def processar_tecla(self, event: tk.Event) -> str | None:
        if event.keysym in {
            "Alt_L",
            "Alt_R",
            "Control_L",
            "Control_R",
            "Shift_L",
            "Shift_R",
        }:
            return None

        if event.keysym in {"Return", "KP_Enter"}:
            self.ao_clicar("=")
            return "break"

        if event.keysym == "Escape":
            self.ao_clicar("C")
            return "break"

        if event.keysym == "BackSpace":
            self.ao_clicar("⌫")
            return "break"

        mapa = {
            "+": "+",
            "-": "-",
            "*": "×",
            "/": "÷",
            "%": "%",
            "=": "=",
            "&": "AND",
            "|": "OR",
            "^": "XOR",
            "~": "NOT",
            "(": "(",
            ")": ")",
        }

        if event.char in mapa:
            self.ao_clicar(mapa[event.char])
            return "break"

        if event.char:
            valor = event.char.upper()
            if valor in self._digitos_validos():
                self.ao_clicar(f"DIGIT_{valor}")
                return "break"

        return None

    # ==========================================================
    # OPERAÇÕES
    # ==========================================================

    def _inserir_digito(self, digito: str) -> None:
        if self.substituir_visor or self.entrada_atual == "0":
            self.entrada_atual = digito
        else:
            self.entrada_atual += digito

        self.valor_atual = self._parse_entrada(self.entrada_atual)
        self.texto_operando_atual = None
        self.substituir_visor = False
        self._definir_modo_limpeza_entrada(True)
        self._atualizar_tela()

    def _preparar_operador(self, operador: str) -> None:
        valor = self._valor_entrada_atual()
        texto_valor = self._texto_operando(valor)

        if self.operador_atual is not None and not self.substituir_visor:
            resultado = self._executar_operacao(
                self.primeiro_operando or 0,
                valor,
                self.operador_atual,
            )
            self._definir_valor(resultado)
            valor = resultado
            texto_valor = self._formatar_valor(resultado)

        self.primeiro_operando = valor
        self.operador_atual = operador
        self.texto_primeiro_operando = texto_valor
        self.texto_operando_atual = None
        self.texto_expressao.set(
            f"{self.prefixo_expressao}{texto_valor} "
            f"{self._rotulo_operador_expressao(operador)}"
        )
        self.substituir_visor = True
        self._definir_modo_limpeza_entrada(False)

    def _calcular_resultado(self) -> None:
        if self.operador_atual is None:
            return

        segundo_operando = self._valor_entrada_atual()
        primeiro = self.primeiro_operando or 0
        texto_primeiro = (
            self.texto_primeiro_operando
            or self._formatar_valor(primeiro)
        )
        texto_segundo = self._texto_operando(segundo_operando)

        try:
            resultado = self._executar_operacao(
                primeiro,
                segundo_operando,
                self.operador_atual,
            )
        except ZeroDivisionError:
            self._mostrar_erro("Erro")
            return

        self.texto_expressao.set(
            f"{self.prefixo_expressao}{texto_primeiro} "
            f"{self._rotulo_operador_expressao(self.operador_atual)} "
            f"{texto_segundo} ="
        )
        self._definir_valor(resultado)
        self.operador_atual = None
        self.primeiro_operando = None
        self.texto_primeiro_operando = None
        self.texto_operando_atual = None
        if not self.pilha_parenteses:
            self.prefixo_expressao = ""
        self.substituir_visor = True
        self._definir_modo_limpeza_entrada(False)

    def _abrir_parentese(self) -> None:
        expressao_antes = self.texto_expressao.get().strip()
        self.pilha_parenteses.append(
            (
                self.primeiro_operando,
                self.operador_atual,
                self.texto_primeiro_operando,
                self.texto_operando_atual,
                self.prefixo_expressao,
                expressao_antes,
            )
        )

        self.prefixo_expressao = (
            f"{expressao_antes} ("
            if expressao_antes
            else "("
        )
        self.primeiro_operando = None
        self.operador_atual = None
        self.texto_primeiro_operando = None
        self.texto_operando_atual = None
        self._definir_valor(0)
        self.texto_expressao.set(self.prefixo_expressao)
        self.substituir_visor = True
        self._definir_modo_limpeza_entrada(False)
        self._atualizar_botoes_parenteses()

    def _fechar_parentese(self) -> None:
        if not self.pilha_parenteses:
            return

        try:
            resultado, texto_grupo = self._resolver_parentese_atual()
        except ZeroDivisionError:
            self._mostrar_erro("Erro")
            return

        (
            primeiro_anterior,
            operador_anterior,
            texto_primeiro_anterior,
            _texto_operando_anterior,
            prefixo_anterior,
            expressao_antes,
        ) = self.pilha_parenteses.pop()

        texto_parentese = f"({texto_grupo})"
        expressao_fechada = (
            f"{expressao_antes} {texto_parentese}".strip()
        )

        self.prefixo_expressao = prefixo_anterior
        self.primeiro_operando = primeiro_anterior
        self.operador_atual = operador_anterior
        self.texto_primeiro_operando = texto_primeiro_anterior
        self.texto_operando_atual = texto_parentese
        self._definir_valor(resultado)
        self.texto_expressao.set(expressao_fechada)
        self.substituir_visor = False
        self._definir_modo_limpeza_entrada(False)
        self._atualizar_botoes_parenteses()

    def _resolver_parentese_atual(self) -> tuple[int, str]:
        valor = self._valor_entrada_atual()

        if self.operador_atual is None:
            return valor, self._texto_operando(valor)

        primeiro = self.primeiro_operando or 0
        texto_primeiro = (
            self.texto_primeiro_operando
            or self._formatar_valor(primeiro)
        )
        texto_segundo = self._texto_operando(valor)
        resultado = self._executar_operacao(
            primeiro,
            valor,
            self.operador_atual,
        )
        texto = (
            f"{texto_primeiro} "
            f"{self._rotulo_operador_expressao(self.operador_atual)} "
            f"{texto_segundo}"
        )

        return resultado, texto

    def _texto_operando(self, valor: int) -> str:
        return self.texto_operando_atual or self._formatar_valor(valor)

    def _executar_operacao(
        self,
        primeiro: int,
        segundo: int,
        operador: str,
    ) -> int:
        primeiro = self._mascarar(primeiro)
        segundo = self._mascarar(segundo)

        if operador == "+":
            return self._mascarar(primeiro + segundo)

        if operador == "-":
            return self._mascarar(primeiro - segundo)

        if operador == "×":
            return self._mascarar(primeiro * segundo)

        if operador == "÷":
            if segundo == 0:
                raise ZeroDivisionError

            return self._mascarar(
                int(self._to_signed(primeiro) / self._to_signed(segundo))
            )

        if operador == "%":
            if segundo == 0:
                raise ZeroDivisionError

            return self._mascarar(primeiro % segundo)

        if operador == "AND":
            return self._mascarar(primeiro & segundo)

        if operador == "OR":
            return self._mascarar(primeiro | segundo)

        if operador == "NAND":
            return self._mascarar(~(primeiro & segundo))

        if operador == "NOR":
            return self._mascarar(~(primeiro | segundo))

        if operador == "XOR":
            return self._mascarar(primeiro ^ segundo)

        if operador == "<<":
            return self._deslocar_esquerda(primeiro, segundo)

        if operador == ">>":
            return self._deslocar_direita(primeiro, segundo)

        return primeiro

    @staticmethod
    def _rotulo_operador_expressao(operador: str) -> str:
        if operador == "<<":
            return "Lsh"

        if operador == ">>":
            return "Rsh"

        return operador

    def _deslocar_esquerda(self, valor: int, deslocamento: int) -> int:
        bits = WORD_SIZES[self.tamanho_palavra]
        deslocamento = max(0, deslocamento)

        if self.modo_deslocamento == "carry":
            return self._rotacionar_esquerda_com_transporte(
                valor,
                deslocamento,
            )

        if self.modo_deslocamento == "circular":
            return self._rotacionar_esquerda(valor, deslocamento)

        deslocamento = min(deslocamento, bits)
        return self._mascarar(valor << deslocamento)

    def _deslocar_direita(self, valor: int, deslocamento: int) -> int:
        bits = WORD_SIZES[self.tamanho_palavra]
        deslocamento = max(0, deslocamento)

        if self.modo_deslocamento == "carry":
            return self._rotacionar_direita_com_transporte(
                valor,
                deslocamento,
            )

        if self.modo_deslocamento == "circular":
            return self._rotacionar_direita(valor, deslocamento)

        deslocamento = min(deslocamento, bits)

        if self.modo_deslocamento == "logico":
            return self._mascarar(valor >> deslocamento)

        return self._mascarar(self._to_signed(valor) >> deslocamento)

    def _rotacionar_esquerda(self, valor: int, deslocamento: int) -> int:
        bits = WORD_SIZES[self.tamanho_palavra]
        deslocamento %= bits
        valor = self._mascarar(valor)

        if deslocamento == 0:
            return valor

        return self._mascarar(
            (valor << deslocamento)
            | (valor >> (bits - deslocamento))
        )

    def _rotacionar_direita(self, valor: int, deslocamento: int) -> int:
        bits = WORD_SIZES[self.tamanho_palavra]
        deslocamento %= bits
        valor = self._mascarar(valor)

        if deslocamento == 0:
            return valor

        return self._mascarar(
            (valor >> deslocamento)
            | (valor << (bits - deslocamento))
        )

    def _rotacionar_esquerda_com_transporte(
        self,
        valor: int,
        deslocamento: int,
    ) -> int:
        bits = WORD_SIZES[self.tamanho_palavra]
        valor = self._mascarar(valor)
        deslocamento %= bits + 1

        for _ in range(deslocamento):
            novo_transporte = 1 if valor & (1 << (bits - 1)) else 0
            valor = self._mascarar((valor << 1) | self.bit_transporte)
            self.bit_transporte = novo_transporte

        return valor

    def _rotacionar_direita_com_transporte(
        self,
        valor: int,
        deslocamento: int,
    ) -> int:
        bits = WORD_SIZES[self.tamanho_palavra]
        valor = self._mascarar(valor)
        deslocamento %= bits + 1

        for _ in range(deslocamento):
            novo_transporte = valor & 1
            valor = self._mascarar(
                (valor >> 1) | (self.bit_transporte << (bits - 1))
            )
            self.bit_transporte = novo_transporte

        return valor

    def _aplicar_not(self) -> None:
        valor = self._valor_entrada_atual()
        resultado = self._mascarar(~valor)

        self.texto_expressao.set(f"NOT {self._formatar_valor(valor)}")
        self._definir_valor(resultado)
        self.substituir_visor = True

    def _trocar_sinal(self) -> None:
        valor = -self._to_signed(self._valor_entrada_atual())
        self._definir_valor(valor)
        self.substituir_visor = True

    def _apagar_ultimo(self) -> None:
        if self.substituir_visor:
            return

        self.entrada_atual = (
            "0"
            if len(self.entrada_atual) <= 1
            else self.entrada_atual[:-1]
        )
        self.valor_atual = self._parse_entrada(self.entrada_atual)
        self._atualizar_tela()

    def _limpar_entrada(self) -> None:
        self._definir_valor(0)
        self.substituir_visor = False
        self._definir_modo_limpeza_entrada(False)

    def _limpar_tudo(self) -> None:
        self.modo_limpeza_entrada = False
        self.pilha_parenteses.clear()
        self.prefixo_expressao = ""
        self.texto_primeiro_operando = None
        self.texto_operando_atual = None
        self._definir_valor(0)
        self.primeiro_operando = None
        self.operador_atual = None
        self.bit_transporte = 0
        self.texto_expressao.set("")
        self.substituir_visor = True
        self._atualizar_botao_limpeza()

    def _mostrar_erro(self, mensagem: str) -> None:
        self.texto_visor.set(mensagem)
        self.entrada_atual = "0"
        self.valor_atual = 0
        self.modo_limpeza_entrada = False
        self.primeiro_operando = None
        self.operador_atual = None
        self.texto_primeiro_operando = None
        self.texto_operando_atual = None
        self.prefixo_expressao = ""
        self.pilha_parenteses.clear()
        self.bit_transporte = 0
        self.substituir_visor = True
        self._atualizar_botoes_parenteses()
        self._atualizar_botao_limpeza()

    # ==========================================================
    # MENUS
    # ==========================================================

    def _alternar_menu_bitwise(self) -> None:
        if self._painel_existe(self.frame_menu_bitwise):
            self._fechar_menu_bitwise()
            return

        self.fechar_paineis()
        self.frame_menu_bitwise = self._criar_painel_bitwise()
        self._posicionar_painel(
            self.frame_menu_bitwise,
            self.botao_bitwise,
            largura=198,
        )

    def _alternar_menu_shift(self) -> None:
        if self._painel_existe(self.frame_menu_shift):
            self._fechar_menu_shift()
            return

        self.fechar_paineis()
        self.frame_menu_shift = self._criar_painel_shift()
        self._posicionar_painel(
            self.frame_menu_shift,
            self.botao_shift,
            largura=210,
        )

    def _alternar_menu_word(self) -> None:
        if self._painel_existe(self.frame_menu_word):
            self._fechar_menu_word()
            return

        self.fechar_paineis()
        self.frame_menu_word = self._criar_painel_word()
        self._posicionar_painel(
            self.frame_menu_word,
            self.botao_word,
            largura=120,
        )

    def _alternar_menu_memoria(self) -> None:
        if self._painel_existe(self.frame_menu_memoria):
            self._fechar_menu_memoria()
            return

        if not self.memoria_valores:
            return

        self.fechar_paineis()
        self._aplicar_sombra_memoria()
        self.frame_menu_memoria = self._criar_painel_memoria()
        self._posicionar_painel_memoria()

    def _criar_painel_bitwise(self) -> tk.Frame:
        painel = tk.Frame(
            self,
            bg=Tema.COR_MENU,
            bd=1,
            relief="solid",
        )

        operacoes = (
            ("AND", "OR", "NOT"),
            ("NAND", "NOR", "XOR"),
        )

        for coluna in range(3):
            painel.columnconfigure(coluna, weight=1)

        for linha, valores in enumerate(operacoes):
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
                    command=lambda valor=texto: self.ao_clicar(valor),
                )
                botao.grid(
                    row=linha,
                    column=coluna,
                    sticky="nsew",
                    padx=2,
                    pady=2,
                    ipadx=12,
                    ipady=12,
                )

        return painel

    def _criar_painel_shift(self) -> tk.Frame:
        painel = tk.Frame(
            self,
            bg=Tema.COR_MENU,
            bd=1,
            relief="solid",
        )
        painel.columnconfigure(0, weight=1)

        opcoes = (
            ("aritmetico", "Deslocamento\naritmético"),
            ("logico", "Deslocamento lógico"),
            ("circular", "Girar deslocamento\ncircular"),
            (
                "carry",
                "Girar através do\ndeslocamento circular\nde transporte",
            ),
        )

        for linha, (valor, texto) in enumerate(opcoes):
            selecionado = valor == self.modo_deslocamento
            botao = tk.Button(
                painel,
                text=f"{'◉' if selecionado else '○'}  {texto}",
                bg=Tema.COR_MENU,
                fg=Tema.COR_TEXTO,
                activebackground=Tema.COR_BOTAO_HOVER,
                activeforeground=Tema.COR_TEXTO,
                font=("Segoe UI", 10),
                relief="flat",
                bd=0,
                highlightthickness=0,
                anchor="w",
                justify="left",
                padx=10,
                pady=7,
                cursor="hand2",
                command=lambda modo=valor: self._selecionar_modo_shift(
                    modo
                ),
            )
            botao.grid(row=linha, column=0, sticky="ew")

        return painel

    def _selecionar_modo_shift(self, modo: str) -> None:
        self.modo_deslocamento = modo
        self._fechar_menu_shift()
        self._atualizar_tela()

    def _selecionar_visualizacao(self, visualizacao: str) -> None:
        self.visualizacao_atual = visualizacao
        self.fechar_paineis()
        self._atualizar_tela()

    def _alternar_bit(self, posicao: int) -> None:
        if posicao >= WORD_SIZES[self.tamanho_palavra]:
            return

        self.valor_atual = self._mascarar(
            self.valor_atual ^ (1 << posicao)
        )
        self.entrada_atual = self._formatar_valor(
            self.valor_atual,
            base=self.base_atual,
        )
        self.substituir_visor = True
        self._atualizar_tela()

    def _alternar_word_size(self) -> None:
        tamanhos = tuple(WORD_SIZES)
        indice_atual = tamanhos.index(self.tamanho_palavra)
        self.tamanho_palavra = tamanhos[
            (indice_atual + 1) % len(tamanhos)
        ]
        self.bit_transporte = 0
        self.valor_atual = self._mascarar(self.valor_atual)
        self.entrada_atual = self._formatar_valor(
            self.valor_atual,
            base=self.base_atual,
        )
        self.fechar_paineis()
        self._atualizar_tela()

    def _criar_painel_operacoes(
        self,
        operacoes: tuple[str, ...],
    ) -> tk.Frame:
        painel = tk.Frame(
            self,
            bg=Tema.COR_MENU,
            bd=1,
            relief="solid",
        )

        for linha, operacao in enumerate(operacoes):
            botao = tk.Button(
                painel,
                text=operacao,
                bg=Tema.COR_MENU,
                fg=Tema.COR_TEXTO,
                activebackground=Tema.COR_BOTAO_HOVER,
                activeforeground=Tema.COR_TEXTO,
                font=("Segoe UI", 10),
                relief="flat",
                bd=0,
                highlightthickness=0,
                anchor="w",
                padx=12,
                pady=8,
                cursor="hand2",
                command=lambda valor=operacao: self.ao_clicar(valor),
            )
            botao.grid(row=linha, column=0, sticky="ew")

        return painel

    def _criar_painel_word(self) -> tk.Frame:
        painel = tk.Frame(
            self,
            bg=Tema.COR_MENU,
            bd=1,
            relief="solid",
        )

        for linha, nome in enumerate(WORD_SIZES):
            botao = tk.Button(
                painel,
                text=nome,
                bg=(
                    Tema.COR_BOTAO_HOVER
                    if nome == self.tamanho_palavra
                    else Tema.COR_MENU
                ),
                fg=Tema.COR_TEXTO,
                activebackground=Tema.COR_BOTAO_HOVER,
                activeforeground=Tema.COR_TEXTO,
                font=("Segoe UI", 10),
                relief="flat",
                bd=0,
                highlightthickness=0,
                anchor="w",
                padx=12,
                pady=8,
                cursor="hand2",
                command=lambda valor=nome: self._selecionar_word(valor),
            )
            botao.grid(row=linha, column=0, sticky="ew")

        return painel

    def _criar_painel_memoria(self) -> tk.Frame:
        painel = tk.Frame(
            self,
            bg=Tema.COR_PAINEL_MEMORIA,
            bd=0,
        )
        self._atualizar_conteudo_painel_memoria(painel)
        return painel

    def _atualizar_conteudo_painel_memoria(
        self,
        painel: tk.Frame | None = None,
    ) -> None:
        painel = painel or self.frame_menu_memoria
        if not self._painel_existe(painel):
            return

        for widget in painel.winfo_children():
            widget.destroy()

        if self.memoria_valores:
            for ordem, (indice, valor) in enumerate(
                reversed(
                    list(enumerate(self.memoria_valores))
                )
            ):
                self._criar_linha_memoria(painel, indice, valor, ordem)
        else:
            mensagem = tk.Label(
                painel,
                text="Nao ha nada salvo na memoria",
                bg=Tema.COR_PAINEL_MEMORIA,
                fg=Tema.COR_TEXTO,
                font=("Segoe UI", 13),
            )
            mensagem.pack(fill="x", padx=15, pady=30)

        botao_lixeira = tk.Button(
            painel,
            text="🗑",
            bg=Tema.COR_PAINEL_MEMORIA,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_PAINEL_MEMORIA_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI Symbol", 15),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=self._limpar_memoria,
        )
        botao_lixeira.pack(side="bottom", anchor="e", padx=15, pady=12)

    def _criar_linha_memoria(
        self,
        painel: tk.Frame,
        indice: int,
        valor: int,
        ordem: int,
    ) -> None:
        linha = tk.Frame(
            painel,
            bg=Tema.COR_PAINEL_MEMORIA,
        )
        linha.pack(fill="x", padx=15, pady=(26 if ordem == 0 else 4, 3))
        linha.columnconfigure(0, weight=1)

        texto = self._formatar_valor_memoria(valor)
        botao_valor = tk.Button(
            linha,
            text=texto,
            bg=Tema.COR_PAINEL_MEMORIA,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_PAINEL_MEMORIA_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 16, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="e",
            padx=10,
            pady=7,
            cursor="hand2",
            command=lambda numero=valor: self._recuperar_memoria_painel(
                numero
            ),
        )
        botao_valor.grid(row=0, column=0, sticky="ew")

        controles = tk.Frame(
            linha,
            bg=Tema.COR_PAINEL_MEMORIA_HOVER,
        )
        controles.grid(row=0, column=1, sticky="e", padx=(4, 0))

        for coluna, (texto_botao, comando) in enumerate(
            (
                (
                    "MC",
                    lambda posicao=indice: self._apagar_memoria(posicao),
                ),
                (
                    "M+",
                    lambda posicao=indice: self._somar_memoria_item(
                        posicao
                    ),
                ),
                (
                    "M-",
                    lambda posicao=indice: self._subtrair_memoria_item(
                        posicao
                    ),
                ),
            )
        ):
            botao = tk.Button(
                controles,
                text=texto_botao,
                bg=Tema.COR_PAINEL_MEMORIA_HOVER,
                fg=Tema.COR_TEXTO,
                activebackground=Tema.COR_BOTAO_HOVER,
                activeforeground=Tema.COR_TEXTO,
                font=Tema.FONTE_BOTAO_MEMORIA,
                relief="flat",
                bd=0,
                highlightthickness=0,
                padx=8,
                pady=5,
                cursor="hand2",
                command=comando,
            )
            botao.grid(row=0, column=coluna, padx=(0 if coluna == 0 else 1, 0))

        controles.grid_remove()

        widgets_hover = [linha, botao_valor, controles]
        widgets_hover.extend(controles.winfo_children())
        for widget in widgets_hover:
            widget.bind(
                "<Enter>",
                lambda _evento, c=controles, l=linha, b=botao_valor: (
                    self._mostrar_acoes_memoria(l, b, c)
                ),
                add="+",
            )
            widget.bind(
                "<Leave>",
                lambda _evento, c=controles, l=linha, b=botao_valor: (
                    self._agendar_ocultar_acoes_memoria(l, b, c)
                ),
                add="+",
            )

    def _mostrar_acoes_memoria(
        self,
        linha: tk.Frame,
        botao_valor: tk.Button,
        controles: tk.Frame,
    ) -> None:
        if not linha.winfo_exists() or not controles.winfo_exists():
            return

        linha.config(bg=Tema.COR_PAINEL_MEMORIA_HOVER)
        botao_valor.config(bg=Tema.COR_PAINEL_MEMORIA_HOVER)
        controles.config(bg=Tema.COR_PAINEL_MEMORIA_HOVER)
        controles.grid()

    def _agendar_ocultar_acoes_memoria(
        self,
        linha: tk.Frame,
        botao_valor: tk.Button,
        controles: tk.Frame,
    ) -> None:
        self.after(
            80,
            lambda: self._ocultar_acoes_memoria(
                linha,
                botao_valor,
                controles,
            ),
        )

    def _ocultar_acoes_memoria(
        self,
        linha: tk.Frame,
        botao_valor: tk.Button,
        controles: tk.Frame,
    ) -> None:
        if not linha.winfo_exists() or not controles.winfo_exists():
            return

        if self._ponteiro_dentro_widget(linha):
            return

        linha.config(bg=Tema.COR_PAINEL_MEMORIA)
        botao_valor.config(bg=Tema.COR_PAINEL_MEMORIA)
        controles.grid_remove()

    def _ponteiro_dentro_widget(self, widget: tk.Widget) -> bool:
        return self._ponto_dentro_widget(
            widget,
            widget.winfo_pointerx(),
            widget.winfo_pointery(),
        )

    def _posicionar_painel_memoria(self) -> None:
        if not self._painel_existe(self.frame_menu_memoria):
            return

        self.update_idletasks()
        self.botao_memoria_menu.update_idletasks()

        posicao_y = (
            self.botao_memoria_menu.winfo_rooty()
            - self.winfo_rooty()
            + self.botao_memoria_menu.winfo_height()
            + 2
        )
        altura_disponivel = max(120, self.winfo_height() - posicao_y)

        self.frame_menu_memoria.place(
            x=0,
            y=posicao_y,
            relwidth=1,
            height=altura_disponivel,
        )
        self.frame_menu_memoria.lift()
        self._registrar_fechamento_memoria()

    def _aplicar_sombra_memoria(self) -> None:
        if self._estado_sombra_memoria:
            return

        cor_sombra = "#101318"
        widgets = [self]
        widgets.extend(self._coletar_widgets(self))

        for widget in widgets:
            if widget is self.frame_menu_memoria:
                continue

            try:
                chaves = set(widget.keys())
            except tk.TclError:
                continue

            estado_original: dict[str, str] = {}
            alteracoes: dict[str, str] = {}

            for opcao in (
                "background",
                "foreground",
                "activebackground",
                "activeforeground",
                "disabledforeground",
                "state",
            ):
                if opcao not in chaves:
                    continue

                try:
                    estado_original[opcao] = str(widget.cget(opcao))
                except tk.TclError:
                    continue

                if opcao in {"background", "activebackground"}:
                    alteracoes[opcao] = cor_sombra
                elif opcao in {
                    "foreground",
                    "activeforeground",
                    "disabledforeground",
                }:
                    alteracoes[opcao] = Tema.COR_TEXTO_DESATIVADO
                elif (
                    opcao == "state"
                    and isinstance(widget, tk.Button)
                    and widget is not self.botao_memoria_menu
                ):
                    alteracoes[opcao] = "disabled"

            if not alteracoes:
                continue

            try:
                widget.config(**alteracoes)
            except tk.TclError:
                continue

            self._estado_sombra_memoria.append((widget, estado_original))

    def _restaurar_sombra_memoria(self) -> None:
        for widget, estado in reversed(self._estado_sombra_memoria):
            try:
                if widget.winfo_exists():
                    widget.config(**estado)
            except tk.TclError:
                continue

        self._estado_sombra_memoria.clear()

    def _registrar_fechamento_memoria(self) -> None:
        if self._bind_clique_fora_memoria is not None:
            return

        self._bind_clique_fora_memoria = self.winfo_toplevel().bind(
            "<Button-1>",
            self._fechar_memoria_ao_clicar_fora,
            add="+",
        )

    def _remover_fechamento_memoria(self) -> None:
        if self._bind_clique_fora_memoria is None:
            return

        try:
            self.winfo_toplevel().unbind(
                "<Button-1>",
                self._bind_clique_fora_memoria,
            )
        except tk.TclError:
            pass

        self._bind_clique_fora_memoria = None

    def _fechar_memoria_ao_clicar_fora(
        self,
        evento: tk.Event,
    ) -> str | None:
        if not self._painel_existe(self.frame_menu_memoria):
            self._remover_fechamento_memoria()
            return None

        if self._ponto_dentro_widget(
            self.frame_menu_memoria,
            evento.x_root,
            evento.y_root,
        ):
            return None

        if self._ponto_dentro_widget(
            self.botao_memoria_menu,
            evento.x_root,
            evento.y_root,
        ):
            return None

        self._fechar_menu_memoria()
        return "break"

    def _ponto_dentro_widget(
        self,
        widget: tk.Widget,
        x_root: int,
        y_root: int,
    ) -> bool:
        if not widget.winfo_exists():
            return False

        x = widget.winfo_rootx()
        y = widget.winfo_rooty()
        largura = widget.winfo_width()
        altura = widget.winfo_height()

        return x <= x_root < x + largura and y <= y_root < y + altura

    def _coletar_widgets(self, widget: tk.Widget) -> list[tk.Widget]:
        widgets: list[tk.Widget] = []

        for filho in widget.winfo_children():
            widgets.append(filho)
            widgets.extend(self._coletar_widgets(filho))

        return widgets

    def _posicionar_painel(
        self,
        painel: tk.Frame,
        referencia: tk.Widget,
        largura: int | None = None,
    ) -> None:
        self.update_idletasks()
        referencia.update_idletasks()

        largura_final = largura or max(120, referencia.winfo_width())
        x = referencia.winfo_rootx() - self.winfo_rootx()
        y = (
            referencia.winfo_rooty()
            - self.winfo_rooty()
            + referencia.winfo_height()
            + 2
        )
        limite_direito = max(2, self.winfo_width() - largura_final - 8)
        x = max(8, min(x, limite_direito))

        painel.place(
            x=x,
            y=y,
            width=largura_final,
        )
        painel.lift()

    def _selecionar_word(self, nome: str) -> None:
        self.tamanho_palavra = nome
        self.bit_transporte = 0
        self.valor_atual = self._mascarar(self.valor_atual)
        self._fechar_menu_word()
        self._definir_valor(self.valor_atual)
        self.botao_word.config(text=self.tamanho_palavra)

    def _selecionar_base(self, base: str) -> None:
        self.base_atual = base
        self.entrada_atual = self._formatar_valor(
            self.valor_atual,
            base=base,
        )
        self.substituir_visor = True
        self._atualizar_tela()

    def _salvar_memoria(self) -> None:
        self.memoria_valores.append(self._valor_entrada_atual())
        self.substituir_visor = True
        self._atualizar_estado_memoria()
        self._atualizar_conteudo_painel_memoria()
        self._atualizar_tela()

    def _recuperar_memoria(self) -> None:
        if not self.memoria_valores:
            return

        self._definir_valor(self.memoria_valores[-1])
        self.substituir_visor = True

    def _limpar_memoria(self) -> None:
        self.memoria_valores.clear()
        self._atualizar_estado_memoria()
        self._atualizar_conteudo_painel_memoria()
        self._fechar_menu_memoria()
        self._atualizar_tela()

    def _somar_memoria(self) -> None:
        valor = self._valor_entrada_atual()
        if self.memoria_valores:
            self.memoria_valores[-1] = self._mascarar(
                self.memoria_valores[-1] + valor
            )
        else:
            self.memoria_valores.append(valor)

        self.substituir_visor = True
        self._atualizar_estado_memoria()
        self._atualizar_conteudo_painel_memoria()
        self._atualizar_tela()

    def _subtrair_memoria(self) -> None:
        valor = self._valor_entrada_atual()
        if self.memoria_valores:
            self.memoria_valores[-1] = self._mascarar(
                self.memoria_valores[-1] - valor
            )
        else:
            self.memoria_valores.append(self._mascarar(-valor))

        self.substituir_visor = True
        self._atualizar_estado_memoria()
        self._atualizar_conteudo_painel_memoria()
        self._atualizar_tela()

    def _recuperar_memoria_painel(self, valor: int) -> None:
        self._definir_valor(valor)
        self.substituir_visor = True
        self._fechar_menu_memoria()

    def _apagar_memoria(self, indice: int) -> None:
        if 0 <= indice < len(self.memoria_valores):
            del self.memoria_valores[indice]

        self._atualizar_estado_memoria()
        if self.memoria_valores:
            self._atualizar_conteudo_painel_memoria()
        else:
            self._fechar_menu_memoria()
        self._atualizar_tela()

    def _somar_memoria_item(self, indice: int) -> None:
        if not 0 <= indice < len(self.memoria_valores):
            return

        self.memoria_valores[indice] = self._mascarar(
            self.memoria_valores[indice] + self._valor_entrada_atual()
        )
        self.substituir_visor = True
        self._atualizar_conteudo_painel_memoria()
        self._atualizar_tela()

    def _subtrair_memoria_item(self, indice: int) -> None:
        if not 0 <= indice < len(self.memoria_valores):
            return

        self.memoria_valores[indice] = self._mascarar(
            self.memoria_valores[indice] - self._valor_entrada_atual()
        )
        self.substituir_visor = True
        self._atualizar_conteudo_painel_memoria()
        self._atualizar_tela()

    def _formatar_valor_memoria(self, valor: int) -> str:
        return self._formatar_valor(
            self._mascarar(valor),
            base=self.base_atual,
        )

    def _atualizar_estado_memoria(self) -> None:
        if not hasattr(self, "botao_memoria_menu"):
            return

        possui_memoria = bool(self.memoria_valores)
        self.botao_memoria_menu.config(
            state="normal" if possui_memoria else "disabled",
            fg=(
                Tema.COR_TEXTO
                if possui_memoria
                else Tema.COR_TEXTO_DESATIVADO
            ),
            disabledforeground=Tema.COR_TEXTO_DESATIVADO,
        )

    # ==========================================================
    # FORMATAÇÃO E ESTADO
    # ==========================================================

    def _atualizar_tela(self) -> None:
        self.valor_atual = self._mascarar(self.valor_atual)
        self.texto_visor.set(
            self._formatar_valor(
                self.valor_atual,
                base=self.base_atual,
            )
        )

        for base, label in self.labels_bases.items():
            label.config(
                text=self._formatar_valor(
                    self.valor_atual,
                    base=base,
                )
            )

        for base, botao in self.botoes_bases.items():
            ativo = base == self.base_atual
            botao.config(
                bg=Tema.COR_BOTAO_HOVER if ativo else Tema.COR_FUNDO,
                fg=Tema.COR_BOTAO_IGUAL if ativo else Tema.COR_TEXTO,
            )

        self._atualizar_estado_memoria()
        self.botao_word.config(text=self.tamanho_palavra)
        self.botao_shift.config(
            text=f"{self._rotulo_modo_shift()}  ⌄"
        )
        self._atualizar_visualizacao_inferior()
        self._atualizar_visualizacao_bits()
        self._atualizar_botoes_digitos()
        self._atualizar_botao_limpeza()
        self._atualizar_conteudo_painel_memoria()

    def _atualizar_visualizacao_inferior(self) -> None:
        if (
            self.frame_teclado is None
            or self.frame_bits is None
            or self.frame_menus is None
        ):
            return

        if self.visualizacao_atual == "bits":
            self.fechar_paineis()
            self.frame_menus.grid_remove()
            self.frame_area_inferior.grid(
                row=3,
                column=0,
                rowspan=2,
                sticky="nsew",
                padx=0,
                pady=0,
            )
            self.frame_bits.tkraise()
            self.indicador_teclado.grid_remove()
            self.indicador_bits.grid()
        else:
            self.frame_menus.grid(
                row=3,
                column=0,
                sticky="ew",
                padx=12,
                pady=(0, 5),
            )
            self.frame_area_inferior.grid(
                row=4,
                column=0,
                rowspan=1,
                sticky="nsew",
                padx=0,
                pady=0,
            )
            self.frame_teclado.tkraise()
            self.indicador_bits.grid_remove()
            self.indicador_teclado.grid()

    def _atualizar_visualizacao_bits(self) -> None:
        if not self.botoes_bits:
            return

        tamanho = WORD_SIZES[self.tamanho_palavra]
        valor = self._mascarar(self.valor_atual)

        for posicao, botao in self.botoes_bits.items():
            ativo = posicao < tamanho
            bit_ligado = bool(valor & (1 << posicao))
            botao.config(
                text="1" if bit_ligado and ativo else "0",
                state="normal" if ativo else "disabled",
                fg=(
                    Tema.COR_TEXTO
                    if ativo
                    else Tema.COR_TEXTO_DESATIVADO
                ),
                disabledforeground=Tema.COR_TEXTO_DESATIVADO,
            )

    def _atualizar_botoes_digitos(self) -> None:
        digitos_validos = self._digitos_validos()

        for texto, botao in self.botoes_principais.items():
            digito = texto.removeprefix("DIGIT_")

            if texto.startswith("DIGIT_") or texto in "0123456789":
                habilitado = digito in digitos_validos
                botao.config(
                    state="normal" if habilitado else "disabled",
                    bg=Tema.COR_BOTAO if habilitado else Tema.COR_BOTAO_DESATIVADO,
                    fg=Tema.COR_TEXTO if habilitado else Tema.COR_TEXTO_DESATIVADO,
                    disabledforeground=Tema.COR_TEXTO_DESATIVADO,
                )

        self.botoes_principais[","].config(
            state="disabled",
            bg=Tema.COR_BOTAO_DESATIVADO,
            fg=Tema.COR_TEXTO_DESATIVADO,
            disabledforeground=Tema.COR_TEXTO_DESATIVADO,
        )
        self._atualizar_botoes_parenteses()

    def _atualizar_botoes_parenteses(self) -> None:
        if "(" not in self.botoes_principais:
            return

        quantidade = len(self.pilha_parenteses)
        self.botoes_principais["("].config(
            text=f"({quantidade}" if quantidade else "(",
            state="normal",
            bg=Tema.COR_BOTAO,
            fg=Tema.COR_TEXTO,
            disabledforeground=Tema.COR_TEXTO_DESATIVADO,
        )

        self.botoes_principais[")"].config(
            state="normal",
            bg=Tema.COR_BOTAO,
            fg=Tema.COR_TEXTO,
            disabledforeground=Tema.COR_TEXTO_DESATIVADO,
        )

    def _definir_modo_limpeza_entrada(self, ativo: bool) -> None:
        self.modo_limpeza_entrada = ativo
        self._atualizar_botao_limpeza()

    def _atualizar_botao_limpeza(self) -> None:
        if "C" not in self.botoes_principais:
            return

        self.botoes_principais["C"].config(
            text="CE" if self.modo_limpeza_entrada else "C",
        )

    def _definir_valor(self, valor: int) -> None:
        self.valor_atual = self._mascarar(valor)
        self.entrada_atual = self._formatar_valor(
            self.valor_atual,
            base=self.base_atual,
        )
        self._atualizar_tela()

    def _valor_entrada_atual(self) -> int:
        return self._parse_entrada(self.entrada_atual)

    def _parse_entrada(self, texto: str) -> int:
        if texto in {"", "-"}:
            return 0

        base = BASES[self.base_atual]
        return self._mascarar(int(texto, base))

    def _formatar_valor(
        self,
        valor: int,
        base: str | None = None,
    ) -> str:
        base = base or self.base_atual
        valor = self._mascarar(valor)

        if base == "DEC":
            return str(self._to_signed(valor))

        if base == "HEX":
            return format(valor, "X")

        if base == "OCT":
            return format(valor, "o")

        return format(valor, "b")

    def _digitos_validos(self) -> set[str]:
        base = BASES[self.base_atual]
        digitos = "0123456789ABCDEF"[:base]
        return set(digitos)

    def _rotulo_modo_shift(self) -> str:
        rotulos = {
            "aritmetico": "Deslocamento de bit",
            "logico": "Deslocamento lógico",
            "circular": "Giro circular",
            "carry": "Giro com transporte",
        }
        return rotulos[self.modo_deslocamento]

    def _mascarar(self, valor: int) -> int:
        return valor & self._mascara()

    def _mascara(self) -> int:
        return (1 << WORD_SIZES[self.tamanho_palavra]) - 1

    def _to_signed(self, valor: int) -> int:
        bits = WORD_SIZES[self.tamanho_palavra]
        valor = self._mascarar(valor)
        sinal = 1 << (bits - 1)

        if valor & sinal:
            return valor - (1 << bits)

        return valor

    def _ao_alterar_texto_visor(self, *_args) -> None:
        self.after_idle(self._ajustar_fonte_visor)

    def _ajustar_fonte_visor(self) -> None:
        if not hasattr(self, "label_visor"):
            return

        if not hasattr(self, "fonte_visor_dinamica"):
            return

        texto = self.texto_visor.get()
        self.label_visor.update_idletasks()

        largura_disponivel = (
            self.label_visor.winfo_width()
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

    # ==========================================================
    # INTEGRAÇÃO
    # ==========================================================

    def fechar_paineis(self) -> None:
        self._fechar_menu_bitwise()
        self._fechar_menu_shift()
        self._fechar_menu_word()
        self._fechar_menu_memoria()

    def alternar_historico(self) -> None:
        self.fechar_paineis()

    def _focar_visor_para_teclado(self) -> None:
        self.focus_set()

    def _fechar_menu_bitwise(self) -> None:
        if self._painel_existe(self.frame_menu_bitwise):
            self.frame_menu_bitwise.destroy()

        self.frame_menu_bitwise = None

    def _fechar_menu_shift(self) -> None:
        if self._painel_existe(self.frame_menu_shift):
            self.frame_menu_shift.destroy()

        self.frame_menu_shift = None

    def _fechar_menu_word(self) -> None:
        if self._painel_existe(self.frame_menu_word):
            self.frame_menu_word.destroy()

        self.frame_menu_word = None

    def _fechar_menu_memoria(self) -> None:
        if self._painel_existe(self.frame_menu_memoria):
            self.frame_menu_memoria.destroy()

        self.frame_menu_memoria = None
        self._remover_fechamento_memoria()
        self._restaurar_sombra_memoria()
        self._atualizar_estado_memoria()

    @staticmethod
    def _painel_existe(painel: tk.Frame | None) -> bool:
        return painel is not None and bool(painel.winfo_exists())
