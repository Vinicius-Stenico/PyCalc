from __future__ import annotations

import tkinter as tk
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from tema import Tema


UnidadeConversao = tuple[str, str, Decimal]

TECLADO_CONVERSOR = (
    ("CE", "⌫"),
    ("7", "8", "9"),
    ("4", "5", "6"),
    ("1", "2", "3"),
    ("", "0", ","),
)


class ConversorUnidades(tk.Frame):
    """Base reutilizável para conversores de unidades lineares.

    Subclasses precisam declarar:
    - UNIDADES: dict[codigo, (nome exibido, simbolo, fator na unidade base)]
    - UNIDADE_ORIGEM_PADRAO
    - UNIDADE_DESTINO_PADRAO
    """

    UNIDADES: dict[str, UnidadeConversao] = {}
    UNIDADE_ORIGEM_PADRAO = ""
    UNIDADE_DESTINO_PADRAO = ""
    CASAS_DECIMAIS_CONVERSAO = 12
    ALTURA_TECLADO = 220
    PERMITE_NEGATIVO = False

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=Tema.COR_FUNDO)

        if not self.UNIDADES:
            raise ValueError("Conversor sem unidades configuradas.")

        self.unidade_origem = self.UNIDADE_ORIGEM_PADRAO
        self.unidade_destino = self.UNIDADE_DESTINO_PADRAO
        self.valor_digitado = "0"
        self.campo_ativo = "origem"
        self.atualizando_campos = False

        self.frame_menu_unidade: tk.Frame | None = None
        self.alvo_menu_unidade: str | None = None
        self.canvas_menu_unidade: tk.Canvas | None = None
        self.scrollbar_menu_unidade: tk.Canvas | None = None
        self.thumb_menu_unidade: int | None = None
        self.scroll_drag_y = 0
        self.scroll_drag_inicio = 0.0
        self.bind_clique_fora_unidade: str | None = None

        self.texto_origem = tk.StringVar(value="0")
        self.texto_destino = tk.StringVar(value="0")
        self.texto_conversao = tk.StringVar()

        self.texto_origem.trace_add(
            "write",
            lambda *_args: self._ao_editar_valor("origem"),
        )
        self.texto_destino.trace_add(
            "write",
            lambda *_args: self._ao_editar_valor("destino"),
        )

        self._configurar_layout()
        self._criar_interface()
        self._atualizar_tela()

    # ==========================================================
    # CONSTRUÇÃO
    # ==========================================================

    def _configurar_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

    def _criar_interface(self) -> None:
        self.frame_conteudo = tk.Frame(self, bg=Tema.COR_FUNDO)
        self.frame_conteudo.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(8, 2),
        )
        self.frame_conteudo.columnconfigure(0, weight=0)
        self.frame_conteudo.columnconfigure(1, weight=1)

        self._criar_linha_valor(
            linha=0,
            simbolo_var=lambda: self.UNIDADES[self.unidade_origem][1],
            texto_var=self.texto_origem,
            destaque=True,
        )
        self.botao_origem = self._criar_botao_unidade(
            linha=1,
            comando=lambda: self._alternar_menu_unidade("origem"),
        )

        self._criar_linha_valor(
            linha=2,
            simbolo_var=lambda: self.UNIDADES[self.unidade_destino][1],
            texto_var=self.texto_destino,
            destaque=False,
        )
        self.botao_destino = self._criar_botao_unidade(
            linha=3,
            comando=lambda: self._alternar_menu_unidade("destino"),
        )

        label_conversao = tk.Label(
            self.frame_conteudo,
            textvariable=self.texto_conversao,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 9),
            anchor="w",
        )
        label_conversao.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(4, 4),
        )

        self._criar_teclado()

    def _criar_linha_valor(
        self,
        linha: int,
        simbolo_var,
        texto_var: tk.StringVar,
        destaque: bool,
    ) -> None:
        simbolo = tk.Label(
            self.frame_conteudo,
            text=simbolo_var(),
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 14),
            anchor="w",
        )
        simbolo.grid(
            row=linha,
            column=0,
            sticky="w",
            pady=(0 if linha == 0 else 6, 0),
        )

        valor = tk.Entry(
            self.frame_conteudo,
            textvariable=texto_var,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            insertbackground=Tema.COR_FUNDO,
            insertontime=0,
            insertofftime=0,
            selectbackground=Tema.COR_BOTAO_IGUAL,
            selectforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 30 if destaque else 25),
            relief="flat",
            bd=0,
            highlightthickness=0,
            justify="left",
        )
        valor.grid(
            row=linha,
            column=1,
            sticky="ew",
            padx=(10, 0),
            pady=(0 if linha == 0 else 6, 0),
        )

        if destaque:
            self.label_simbolo_origem = simbolo
            self.entrada_origem = valor
            valor.bind(
                "<FocusIn>",
                lambda _evento: self._selecionar_campo("origem"),
            )
        else:
            self.label_simbolo_destino = simbolo
            self.entrada_destino = valor
            valor.bind(
                "<FocusIn>",
                lambda _evento: self._selecionar_campo("destino"),
            )

    def _criar_botao_unidade(self, linha: int, comando) -> tk.Button:
        botao = tk.Button(
            self.frame_conteudo,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="w",
            padx=0,
            pady=4,
            cursor="hand2",
            command=comando,
        )
        botao.grid(
            row=linha,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 4),
        )
        return botao

    def _criar_teclado(self) -> None:
        frame = tk.Frame(self, bg=Tema.COR_FUNDO)
        frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=5,
            pady=(0, 5),
        )
        frame.grid_propagate(False)
        frame.configure(height=self.ALTURA_TECLADO)

        for coluna in range(3):
            frame.columnconfigure(
                coluna,
                weight=1,
                uniform="teclado_conversor",
                minsize=96,
            )

        for linha in range(len(TECLADO_CONVERSOR)):
            frame.rowconfigure(linha, weight=1, uniform="teclado_conversor")

        for linha, valores in enumerate(TECLADO_CONVERSOR):
            deslocamento = 1 if linha == 0 else 0

            for coluna, texto in enumerate(valores):
                if texto == "":
                    continue

                botao = self._criar_botao_teclado(frame, texto)
                botao.grid(
                    row=linha,
                    column=coluna + deslocamento,
                    sticky="nsew",
                    padx=1,
                    pady=1,
                )

    def _criar_botao_teclado(
        self,
        parent: tk.Widget,
        texto: str,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=texto,
            bg=Tema.COR_BOTAO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 17),
            width=4,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=lambda valor=texto: self.ao_clicar(valor),
        )

    # ==========================================================
    # EVENTOS
    # ==========================================================

    def ao_clicar(self, valor: str) -> None:
        self._fechar_menu_unidade()

        if valor.isdigit():
            self._inserir_digito(valor)
            return

        if valor == ",":
            self._inserir_decimal()
            return

        if valor == "CE":
            self.valor_digitado = "0"
            self._atualizar_tela()
            return

        if valor == "⌫":
            self._apagar_ultimo()

    def processar_tecla(self, event: tk.Event) -> str | None:
        if self.focus_get() in {self.entrada_origem, self.entrada_destino}:
            return None

        if event.keysym in {"Alt_L", "Alt_R", "Control_L", "Control_R"}:
            return None

        if event.keysym == "Escape":
            self.ao_clicar("CE")
            return "break"

        if event.keysym == "BackSpace":
            self.ao_clicar("⌫")
            return "break"

        if event.char and event.char.isdigit():
            self.ao_clicar(event.char)
            return "break"

        if event.char in {",", "."}:
            self.ao_clicar(",")
            return "break"

        if event.char == "-" and self.PERMITE_NEGATIVO:
            self._alternar_sinal()
            return "break"

        return None

    def _inserir_digito(self, digito: str) -> None:
        if self._campo_ativo_tem_selecao() or self.valor_digitado == "0":
            self.valor_digitado = digito
        else:
            self.valor_digitado += digito

        self._atualizar_tela()

    def _selecionar_campo(self, alvo: str) -> None:
        self.campo_ativo = alvo
        entrada = (
            self.entrada_origem
            if alvo == "origem"
            else self.entrada_destino
        )
        self.valor_digitado = self._normalizar_texto_valor(entrada.get())
        entrada.after_idle(lambda: entrada.select_range(0, "end"))

    def _ao_editar_valor(self, alvo: str) -> None:
        if self.atualizando_campos:
            return

        self.campo_ativo = alvo
        texto = (
            self.texto_origem.get()
            if alvo == "origem"
            else self.texto_destino.get()
        )
        self.valor_digitado = self._normalizar_texto_valor(texto)
        self._atualizar_tela()

    def _inserir_decimal(self) -> None:
        if self._campo_ativo_tem_selecao():
            self.valor_digitado = "0,"
            self._atualizar_tela()
            return

        if "," not in self.valor_digitado:
            self.valor_digitado += ","

        self._atualizar_tela()

    def _alternar_sinal(self) -> None:
        if self.valor_digitado.startswith("-"):
            self.valor_digitado = self.valor_digitado[1:] or "0"
        elif self.valor_digitado != "0":
            self.valor_digitado = f"-{self.valor_digitado}"
        else:
            self.valor_digitado = "-0"

        self._atualizar_tela()

    def _apagar_ultimo(self) -> None:
        if self._campo_ativo_tem_selecao() or len(self.valor_digitado) <= 1:
            self.valor_digitado = "0"
        else:
            self.valor_digitado = self.valor_digitado[:-1]
            if self.valor_digitado.endswith(","):
                self.valor_digitado = self.valor_digitado[:-1] or "0"

        self._atualizar_tela()

    def _campo_ativo_tem_selecao(self) -> bool:
        entrada = (
            self.entrada_origem
            if self.campo_ativo == "origem"
            else self.entrada_destino
        )
        try:
            return bool(entrada.selection_present())
        except tk.TclError:
            return False

    # ==========================================================
    # PAINEL DE UNIDADES
    # ==========================================================

    def _alternar_menu_unidade(self, alvo: str) -> None:
        if self._painel_existe(self.frame_menu_unidade):
            self._fechar_menu_unidade()
            return

        self.alvo_menu_unidade = alvo
        referencia = (
            self.botao_origem
            if alvo == "origem"
            else self.botao_destino
        )
        self.frame_menu_unidade = self._criar_painel_unidade(alvo)
        self._posicionar_painel(self.frame_menu_unidade, referencia)

    def _criar_painel_unidade(self, alvo: str) -> tk.Frame:
        painel = tk.Frame(self, bg=Tema.COR_MENU, bd=0)
        painel.columnconfigure(0, weight=1)
        painel.rowconfigure(0, weight=1)

        canvas = tk.Canvas(
            painel,
            bg=Tema.COR_MENU,
            highlightthickness=0,
            bd=0,
        )
        canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas_menu_unidade = canvas

        barra = tk.Canvas(
            painel,
            bg=Tema.COR_MENU,
            highlightthickness=0,
            bd=0,
            width=8,
        )
        barra.grid(row=0, column=1, sticky="ns")
        self.scrollbar_menu_unidade = barra
        self.thumb_menu_unidade = barra.create_rectangle(
            2,
            2,
            6,
            40,
            fill="#f4f4f4",
            outline="",
        )
        barra.tag_bind(
            self.thumb_menu_unidade,
            "<ButtonPress-1>",
            self._iniciar_arraste_scroll_unidade,
        )
        barra.tag_bind(
            self.thumb_menu_unidade,
            "<B1-Motion>",
            self._arrastar_scroll_unidade,
        )
        barra.bind("<ButtonPress-1>", self._clicar_scrollbar_unidade)
        barra.bind("<B1-Motion>", self._arrastar_scroll_unidade)
        canvas.configure(
            yscrollcommand=lambda primeiro, ultimo: (
                self._atualizar_scrollbar_unidade(primeiro, ultimo)
            )
        )

        conteudo = tk.Frame(canvas, bg=Tema.COR_MENU)
        janela = canvas.create_window((0, 0), window=conteudo, anchor="nw")

        conteudo.bind(
            "<Configure>",
            lambda _evento: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda evento: canvas.itemconfigure(janela, width=evento.width),
        )

        for widget in (canvas, painel, conteudo, barra):
            widget.bind("<MouseWheel>", self._rolar_menu_unidade)

        unidade_atual = (
            self.unidade_origem
            if alvo == "origem"
            else self.unidade_destino
        )

        for linha, codigo in enumerate(self.UNIDADES):
            nome, simbolo, _fator = self.UNIDADES[codigo]
            selecionado = codigo == unidade_atual
            cor_fundo = (
                Tema.COR_BOTAO_HOVER
                if selecionado
                else Tema.COR_MENU
            )

            item = tk.Frame(conteudo, bg=cor_fundo)
            item.grid(row=linha, column=0, sticky="ew", padx=7, pady=1)
            item.columnconfigure(1, weight=1)
            conteudo.columnconfigure(0, weight=1)
            item.bind("<MouseWheel>", self._rolar_menu_unidade)

            indicador = tk.Frame(
                item,
                bg=Tema.COR_BOTAO_IGUAL if selecionado else cor_fundo,
                width=3,
            )
            indicador.grid(row=0, column=0, sticky="ns")

            botao = tk.Button(
                item,
                text=f"{nome} ({simbolo})",
                bg=cor_fundo,
                fg=Tema.COR_TEXTO,
                activebackground=Tema.COR_BOTAO_HOVER,
                activeforeground=Tema.COR_TEXTO,
                font=("Segoe UI", 10),
                relief="flat",
                bd=0,
                highlightthickness=0,
                anchor="w",
                padx=10,
                pady=8,
                cursor="hand2",
                command=lambda unidade=codigo: self._selecionar_unidade(
                    alvo,
                    unidade,
                ),
            )
            botao.grid(row=0, column=1, sticky="ew")
            botao.bind("<MouseWheel>", self._rolar_menu_unidade)

        return painel

    def _selecionar_unidade(self, alvo: str, unidade: str) -> None:
        if alvo == "origem":
            self.unidade_origem = unidade
        else:
            self.unidade_destino = unidade

        self._fechar_menu_unidade()
        self._atualizar_tela()

    def _rolar_menu_unidade(self, evento: tk.Event) -> str:
        if self.canvas_menu_unidade is None:
            return "break"

        unidades = int(-1 * (evento.delta / 120))
        if unidades == 0:
            unidades = -1 if evento.delta > 0 else 1

        self.canvas_menu_unidade.yview_scroll(unidades, "units")
        return "break"

    def _clicar_scrollbar_unidade(self, evento: tk.Event) -> str:
        if (
            self.canvas_menu_unidade is None
            or self.scrollbar_menu_unidade is None
        ):
            return "break"

        altura = max(1, self.scrollbar_menu_unidade.winfo_height())
        destino = max(0.0, min(1.0, evento.y / altura))
        self.canvas_menu_unidade.yview_moveto(destino)
        self._iniciar_arraste_scroll_unidade(evento)
        return "break"

    def _iniciar_arraste_scroll_unidade(self, evento: tk.Event) -> str:
        self.scroll_drag_y = evento.y
        if self.canvas_menu_unidade is not None:
            self.scroll_drag_inicio = self.canvas_menu_unidade.yview()[0]
        else:
            self.scroll_drag_inicio = 0.0

        return "break"

    def _arrastar_scroll_unidade(self, evento: tk.Event) -> str:
        if (
            self.canvas_menu_unidade is None
            or self.scrollbar_menu_unidade is None
        ):
            return "break"

        altura = max(1, self.scrollbar_menu_unidade.winfo_height())
        delta = evento.y - self.scroll_drag_y
        destino = self.scroll_drag_inicio + (delta / altura)
        self.canvas_menu_unidade.yview_moveto(max(0.0, min(1.0, destino)))
        return "break"

    def _atualizar_scrollbar_unidade(
        self,
        primeiro: str,
        ultimo: str,
    ) -> None:
        if (
            self.scrollbar_menu_unidade is None
            or self.thumb_menu_unidade is None
        ):
            return

        inicio = float(primeiro)
        fim = float(ultimo)
        altura = max(1, self.scrollbar_menu_unidade.winfo_height())
        y1 = max(2, int(inicio * altura))
        y2 = min(altura - 2, int(fim * altura))
        if y2 - y1 < 28:
            y2 = min(altura - 2, y1 + 28)

        self.scrollbar_menu_unidade.coords(
            self.thumb_menu_unidade,
            2,
            y1,
            6,
            y2,
        )

    # ==========================================================
    # CONVERSÃO, FORMATAÇÃO E ESTADO
    # ==========================================================

    def _atualizar_tela(self) -> None:
        valor = self._valor_decimal()

        convertido = (
            self._converter_valor(
                valor,
                self.unidade_origem,
                self.unidade_destino,
            )
            if self.campo_ativo == "origem"
            else self._converter_valor(
                valor,
                self.unidade_destino,
                self.unidade_origem,
            )
        )

        simbolo_origem = self.UNIDADES[self.unidade_origem][1]
        simbolo_destino = self.UNIDADES[self.unidade_destino][1]

        self.label_simbolo_origem.config(text=simbolo_origem)
        self.label_simbolo_destino.config(text=simbolo_destino)

        self.botao_origem.config(
            text=f"{self.UNIDADES[self.unidade_origem][0]}  ⌄"
        )
        self.botao_destino.config(
            text=f"{self.UNIDADES[self.unidade_destino][0]}  ⌄"
        )

        self.atualizando_campos = True
        if self.campo_ativo == "origem":
            self.texto_origem.set(self._formatar_entrada())
            self.texto_destino.set(self._formatar_decimal(convertido))
        else:
            self.texto_destino.set(self._formatar_entrada())
            self.texto_origem.set(self._formatar_decimal(convertido))
        self.atualizando_campos = False

        self.texto_conversao.set(
            self._texto_conversao()
        )

    @classmethod
    def _converter_valor(
        cls,
        valor: Decimal,
        unidade_origem: str,
        unidade_destino: str,
    ) -> Decimal:
        return valor * cls._fator_conversao(
            unidade_origem,
            unidade_destino,
        )

    def _texto_conversao(self) -> str:
        simbolo_origem = self.UNIDADES[self.unidade_origem][1]
        simbolo_destino = self.UNIDADES[self.unidade_destino][1]
        convertido = self._converter_valor(
            Decimal("1"),
            self.unidade_origem,
            self.unidade_destino,
        )
        return (
            f"1 {simbolo_origem} = "
            f"{self._formatar_decimal(convertido)} "
            f"{simbolo_destino}"
        )

    @classmethod
    def _fator_conversao(
        cls,
        unidade_origem: str,
        unidade_destino: str,
    ) -> Decimal:
        fator_origem = cls.UNIDADES[unidade_origem][2]
        fator_destino = cls.UNIDADES[unidade_destino][2]
        return fator_origem / fator_destino

    def _valor_decimal(self) -> Decimal:
        texto = self.valor_digitado.replace(",", ".")
        try:
            return Decimal(texto)
        except InvalidOperation:
            return Decimal("0")

    @staticmethod
    def _converter_reverso(
        valor: Decimal,
        fator: Decimal,
    ) -> Decimal:
        if fator == 0:
            return Decimal("0")

        return valor / fator

    def _formatar_entrada(self) -> str:
        return self.valor_digitado

    def _normalizar_texto_valor(self, texto: str) -> str:
        texto = texto.strip().replace(".", ",")
        filtrado = []
        decimal_usado = False
        sinal_usado = False

        for indice, caractere in enumerate(texto):
            if caractere.isdigit():
                filtrado.append(caractere)
            elif caractere == "," and not decimal_usado:
                filtrado.append(",")
                decimal_usado = True
            elif (
                caractere == "-"
                and self.PERMITE_NEGATIVO
                and indice == 0
                and not sinal_usado
            ):
                filtrado.append("-")
                sinal_usado = True

        resultado = "".join(filtrado)
        if resultado in {"", ",", "-", "-,"}:
            return "0"

        return resultado

    @classmethod
    def _formatar_decimal(
        cls,
        valor: Decimal,
        casas: int | None = None,
    ) -> str:
        if valor == 0:
            return "0"

        casas = cls.CASAS_DECIMAIS_CONVERSAO if casas is None else casas
        valor_absoluto = abs(valor)

        if valor_absoluto < Decimal("1e-12") or valor_absoluto >= Decimal("1e16"):
            texto = format(valor.normalize(), "E")
            mantissa, expoente = texto.split("E")
            mantissa = mantissa.rstrip("0").rstrip(".")
            expoente = str(int(expoente))
            return f"{mantissa.replace('.', ',')}e{expoente}"

        quantizador = Decimal("1").scaleb(-casas)
        try:
            valor_arredondado = valor.quantize(
                quantizador,
                rounding=ROUND_HALF_UP,
            )
        except InvalidOperation:
            valor_arredondado = valor.normalize()

        texto = f"{valor_arredondado:f}"

        if "." in texto:
            texto = texto.rstrip("0").rstrip(".")

        return texto.replace(".", ",") or "0"

    def _posicionar_painel(
        self,
        painel: tk.Frame,
        referencia: tk.Widget,
    ) -> None:
        self.update_idletasks()
        referencia.update_idletasks()

        x = referencia.winfo_rootx() - self.winfo_rootx()
        y_referencia = (
            referencia.winfo_rooty()
            - self.winfo_rooty()
            + referencia.winfo_height()
            + 2
        )
        y = max(8, min(y_referencia, 78))
        largura = max(300, self.winfo_width() - 8)
        altura = max(180, self.winfo_height() - y - 8)

        painel.place(
            x=max(4, min(x, self.winfo_width() - largura - 4)),
            y=y,
            width=largura,
            height=altura,
        )
        painel.lift()
        self._registrar_clique_fora_unidade()

    # ==========================================================
    # INTEGRAÇÃO
    # ==========================================================

    def fechar_paineis(self) -> None:
        self._fechar_menu_unidade()

    def ao_exibir(self) -> None:
        self._atualizar_tela()

    def alternar_historico(self) -> None:
        self.fechar_paineis()

    def _focar_visor_para_teclado(self) -> None:
        self.focus_set()

    def _fechar_menu_unidade(self) -> None:
        if self._painel_existe(self.frame_menu_unidade):
            self.frame_menu_unidade.destroy()

        self.frame_menu_unidade = None
        self.alvo_menu_unidade = None
        self.canvas_menu_unidade = None
        self.scrollbar_menu_unidade = None
        self.thumb_menu_unidade = None
        self._remover_clique_fora_unidade()

    def _registrar_clique_fora_unidade(self) -> None:
        if self.bind_clique_fora_unidade is not None:
            return

        self.bind_clique_fora_unidade = self.winfo_toplevel().bind(
            "<Button-1>",
            self._fechar_unidade_ao_clicar_fora,
            add="+",
        )

    def _remover_clique_fora_unidade(self) -> None:
        if self.bind_clique_fora_unidade is None:
            return

        try:
            self.winfo_toplevel().unbind(
                "<Button-1>",
                self.bind_clique_fora_unidade,
            )
        except tk.TclError:
            pass

        self.bind_clique_fora_unidade = None

    def _fechar_unidade_ao_clicar_fora(
        self,
        evento: tk.Event,
    ) -> str | None:
        if not self._painel_existe(self.frame_menu_unidade):
            self._remover_clique_fora_unidade()
            return None

        if self._ponto_dentro_widget(
            self.frame_menu_unidade,
            evento.x_root,
            evento.y_root,
        ):
            return None

        if self._ponto_dentro_widget(
            self.botao_origem,
            evento.x_root,
            evento.y_root,
        ):
            return None

        if self._ponto_dentro_widget(
            self.botao_destino,
            evento.x_root,
            evento.y_root,
        ):
            return None

        self._fechar_menu_unidade()
        return "break"

    @staticmethod
    def _ponto_dentro_widget(
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

    @staticmethod
    def _painel_existe(painel: tk.Frame | None) -> bool:
        return painel is not None and bool(painel.winfo_exists())
