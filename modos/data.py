import calendar
import tkinter as tk
from datetime import date

from tema import Tema


MESES = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)

DIAS_SEMANA = ("seg", "ter", "qua", "qui", "sex", "sáb", "dom")

MODO_DIFERENCA = "Diferença entre datas"
MODO_SOMA = "Adicionar ou subtrair dias"


class CalculadoraData(tk.Frame):
    """Modo de cálculo de data."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=Tema.COR_FUNDO)

        hoje = date.today()
        self.data_inicial = hoje
        self.data_final = hoje
        self.data_base = hoje

        self.modo_atual = tk.StringVar(value=MODO_DIFERENCA)
        self.operacao_soma = tk.StringVar(value="Adicionar")

        self.valor_anos = tk.IntVar(value=0)
        self.valor_meses = tk.IntVar(value=0)
        self.valor_dias = tk.IntVar(value=0)

        self.frame_menu_modo: tk.Frame | None = None
        self.frame_calendario: tk.Frame | None = None
        self.alvo_calendario: str | None = None
        self.mes_calendario = hoje.month
        self.ano_calendario = hoje.year

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
        self.frame_conteudo = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        self.frame_conteudo.grid(
            row=0,
            column=0,
            sticky="new",
            padx=22,
            pady=(16, 0),
        )
        self.frame_conteudo.columnconfigure(0, weight=1)

        self.botao_modo = tk.Button(
            self.frame_conteudo,
            text=f"{self.modo_atual.get()}  ⌄",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 11),
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="w",
            padx=0,
            pady=6,
            cursor="hand2",
            command=self._alternar_menu_modo,
        )
        self.botao_modo.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 16),
        )

        self.frame_diferenca = tk.Frame(
            self.frame_conteudo,
            bg=Tema.COR_FUNDO,
        )
        self.frame_soma = tk.Frame(
            self.frame_conteudo,
            bg=Tema.COR_FUNDO,
        )

        self._criar_tela_diferenca()
        self._criar_tela_soma()

    def _criar_tela_diferenca(self) -> None:
        self.frame_diferenca.columnconfigure(0, weight=1)

        self._criar_rotulo(
            self.frame_diferenca,
            texto="De",
            linha=0,
        )
        self.botao_data_inicial = self._criar_botao_data(
            parent=self.frame_diferenca,
            comando=lambda: self._abrir_calendario(
                "inicial",
                self.botao_data_inicial,
                self.data_inicial,
            ),
        )
        self.botao_data_inicial.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 22),
        )

        self._criar_rotulo(
            self.frame_diferenca,
            texto="Até",
            linha=2,
        )
        self.botao_data_final = self._criar_botao_data(
            parent=self.frame_diferenca,
            comando=lambda: self._abrir_calendario(
                "final",
                self.botao_data_final,
                self.data_final,
            ),
        )
        self.botao_data_final.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 26),
        )

        self._criar_rotulo(
            self.frame_diferenca,
            texto="Diferença",
            linha=4,
        )
        self.label_resultado_diferenca = tk.Label(
            self.frame_diferenca,
            text="",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 11),
            anchor="w",
            justify="left",
        )
        self.label_resultado_diferenca.grid(
            row=5,
            column=0,
            sticky="ew",
        )
        self.label_total_dias = tk.Label(
            self.frame_diferenca,
            text="",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
        )
        self.label_total_dias.grid(
            row=6,
            column=0,
            sticky="ew",
            pady=(5, 0),
        )

    def _criar_tela_soma(self) -> None:
        self.frame_soma.columnconfigure(0, weight=1)
        self.frame_soma.columnconfigure(1, weight=1)
        self.frame_soma.columnconfigure(2, weight=1)

        self._criar_rotulo(
            self.frame_soma,
            texto="De",
            linha=0,
            colunas=3,
        )
        self.botao_data_base = self._criar_botao_data(
            parent=self.frame_soma,
            comando=lambda: self._abrir_calendario(
                "base",
                self.botao_data_base,
                self.data_base,
            ),
        )
        self.botao_data_base.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(0, 20),
        )

        self._criar_rotulo(
            self.frame_soma,
            texto="Operação",
            linha=2,
            colunas=3,
        )
        frame_operacao = tk.Frame(
            self.frame_soma,
            bg=Tema.COR_FUNDO,
        )
        frame_operacao.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(0, 18),
        )
        frame_operacao.columnconfigure(0, weight=1)
        frame_operacao.columnconfigure(1, weight=1)

        self.botao_adicionar = self._criar_botao_alternancia(
            frame_operacao,
            "Adicionar",
        )
        self.botao_adicionar.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 4),
        )
        self.botao_subtrair = self._criar_botao_alternancia(
            frame_operacao,
            "Subtrair",
        )
        self.botao_subtrair.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(4, 0),
        )

        self._criar_rotulo(
            self.frame_soma,
            texto="Anos",
            linha=4,
            coluna=0,
        )
        self._criar_rotulo(
            self.frame_soma,
            texto="Meses",
            linha=4,
            coluna=1,
        )
        self._criar_rotulo(
            self.frame_soma,
            texto="Dias",
            linha=4,
            coluna=2,
        )

        self._criar_spinbox(self.valor_anos).grid(
            row=5,
            column=0,
            sticky="ew",
            padx=(0, 4),
            pady=(0, 24),
        )
        self._criar_spinbox(self.valor_meses).grid(
            row=5,
            column=1,
            sticky="ew",
            padx=4,
            pady=(0, 24),
        )
        self._criar_spinbox(self.valor_dias).grid(
            row=5,
            column=2,
            sticky="ew",
            padx=(4, 0),
            pady=(0, 24),
        )

        self._criar_rotulo(
            self.frame_soma,
            texto="Data",
            linha=6,
            colunas=3,
        )
        self.label_resultado_soma = tk.Label(
            self.frame_soma,
            text="",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 11),
            anchor="w",
        )
        self.label_resultado_soma.grid(
            row=7,
            column=0,
            columnspan=3,
            sticky="ew",
        )

    def _criar_rotulo(
        self,
        parent: tk.Widget,
        texto: str,
        linha: int,
        coluna: int = 0,
        colunas: int = 1,
    ) -> tk.Label:
        label = tk.Label(
            parent,
            text=texto,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 10),
            anchor="w",
        )
        label.grid(
            row=linha,
            column=coluna,
            columnspan=colunas,
            sticky="ew",
            pady=(0, 8),
        )
        return label

    def _criar_botao_data(
        self,
        parent: tk.Widget,
        comando,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text="",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 11),
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="w",
            padx=0,
            pady=6,
            cursor="hand2",
            command=comando,
        )

    def _criar_botao_alternancia(
        self,
        parent: tk.Widget,
        valor: str,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=valor,
            bg=Tema.COR_BOTAO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=lambda: self._selecionar_operacao_soma(valor),
        )

    def _criar_spinbox(self, variavel: tk.IntVar) -> tk.Spinbox:
        spinbox = tk.Spinbox(
            self.frame_soma,
            from_=0,
            to=9999,
            textvariable=variavel,
            bg=Tema.COR_BOTAO,
            fg=Tema.COR_TEXTO,
            buttonbackground=Tema.COR_BOTAO,
            insertbackground=Tema.COR_TEXTO,
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 11),
            justify="center",
            command=self._atualizar_tela,
        )
        spinbox.bind("<KeyRelease>", lambda _event: self._atualizar_tela())
        spinbox.bind("<FocusOut>", lambda _event: self._normalizar_spinbox())
        return spinbox

    # ==========================================================
    # INTERAÇÃO
    # ==========================================================

    def _alternar_menu_modo(self) -> None:
        if self._painel_existe(self.frame_menu_modo):
            self._fechar_menu_modo()
            return

        self.fechar_paineis()

        self.frame_menu_modo = tk.Frame(
            self,
            bg=Tema.COR_MENU,
            bd=1,
            relief="solid",
        )

        for linha, modo in enumerate((MODO_DIFERENCA, MODO_SOMA)):
            botao = tk.Button(
                self.frame_menu_modo,
                text=modo,
                bg=(
                    Tema.COR_BOTAO_HOVER
                    if modo == self.modo_atual.get()
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
                pady=9,
                cursor="hand2",
                command=lambda valor=modo: self._selecionar_modo_data(
                    valor
                ),
            )
            botao.grid(row=linha, column=0, sticky="ew")

        self._posicionar_painel(
            painel=self.frame_menu_modo,
            referencia=self.botao_modo,
            largura=max(self.botao_modo.winfo_width(), 220),
        )

    def _selecionar_modo_data(self, modo: str) -> None:
        self.modo_atual.set(modo)
        self._fechar_menu_modo()
        self._atualizar_tela()

    def _selecionar_operacao_soma(self, operacao: str) -> None:
        self.operacao_soma.set(operacao)
        self._atualizar_tela()

    def _abrir_calendario(
        self,
        alvo: str,
        referencia: tk.Widget,
        data_atual: date,
    ) -> None:
        if (
            self._painel_existe(self.frame_calendario)
            and self.alvo_calendario == alvo
        ):
            self._fechar_calendario()
            return

        self.fechar_paineis()
        self.alvo_calendario = alvo
        self.mes_calendario = data_atual.month
        self.ano_calendario = data_atual.year
        self._criar_calendario(referencia)

    def _criar_calendario(self, referencia: tk.Widget) -> None:
        if self._painel_existe(self.frame_calendario):
            self.frame_calendario.destroy()

        painel = tk.Frame(
            self,
            bg=Tema.COR_MENU,
            bd=1,
            relief="solid",
        )
        self.frame_calendario = painel

        cabecalho = tk.Frame(painel, bg=Tema.COR_MENU)
        cabecalho.grid(
            row=0,
            column=0,
            columnspan=7,
            sticky="ew",
            padx=4,
            pady=(4, 2),
        )
        cabecalho.columnconfigure(1, weight=1)

        self._criar_botao_calendario(
            cabecalho,
            "‹",
            lambda: self._mudar_mes(-1, referencia),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            cabecalho,
            text=f"{MESES[self.mes_calendario - 1]} de {self.ano_calendario}",
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=1, sticky="ew", padx=8)

        self._criar_botao_calendario(
            cabecalho,
            "›",
            lambda: self._mudar_mes(1, referencia),
        ).grid(row=0, column=2, sticky="e")

        for coluna, dia in enumerate(DIAS_SEMANA):
            tk.Label(
                painel,
                text=dia,
                bg=Tema.COR_MENU,
                fg=Tema.COR_TEXTO_SECUNDARIO,
                font=("Segoe UI", 8),
                width=4,
            ).grid(
                row=1,
                column=coluna,
                padx=1,
                pady=(4, 2),
            )

        calendario = calendar.Calendar(firstweekday=0)
        for linha, semana in enumerate(
            calendario.monthdayscalendar(
                self.ano_calendario,
                self.mes_calendario,
            ),
            start=2,
        ):
            for coluna, dia in enumerate(semana):
                if dia == 0:
                    tk.Label(
                        painel,
                        text="",
                        bg=Tema.COR_MENU,
                        width=4,
                    ).grid(row=linha, column=coluna, padx=1, pady=1)
                    continue

                data_botao = date(
                    self.ano_calendario,
                    self.mes_calendario,
                    dia,
                )
                ativo = data_botao == self._obter_data_alvo()
                botao = self._criar_botao_calendario(
                    painel,
                    str(dia),
                    lambda valor=data_botao: self._selecionar_data(valor),
                    ativo=ativo,
                )
                botao.grid(
                    row=linha,
                    column=coluna,
                    sticky="nsew",
                    padx=1,
                    pady=1,
                )

        self._posicionar_painel(
            painel=painel,
            referencia=referencia,
            largura=250,
        )

    def _criar_botao_calendario(
        self,
        parent: tk.Widget,
        texto: str,
        comando,
        ativo: bool = False,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=texto,
            bg=Tema.COR_BOTAO_IGUAL if ativo else Tema.COR_BOTAO,
            fg="#000000" if ativo else Tema.COR_TEXTO,
            activebackground=(
                Tema.COR_BOTAO_IGUAL_HOVER
                if ativo
                else Tema.COR_BOTAO_HOVER
            ),
            activeforeground="#000000" if ativo else Tema.COR_TEXTO,
            font=("Segoe UI", 9),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=comando,
        )

    def _posicionar_painel(
        self,
        painel: tk.Frame,
        referencia: tk.Widget,
        largura: int,
    ) -> None:
        self.update_idletasks()
        referencia.update_idletasks()

        x = referencia.winfo_rootx() - self.winfo_rootx()
        y = (
            referencia.winfo_rooty()
            - self.winfo_rooty()
            + referencia.winfo_height()
            + 2
        )
        limite_direito = max(2, self.winfo_width() - largura - 8)
        x = max(8, min(x, limite_direito))

        painel.place(
            x=x,
            y=y,
            width=largura,
        )
        painel.lift()

    def _mudar_mes(self, deslocamento: int, referencia: tk.Widget) -> None:
        mes = self.mes_calendario + deslocamento
        ano = self.ano_calendario

        if mes < 1:
            mes = 12
            ano -= 1
        elif mes > 12:
            mes = 1
            ano += 1

        self.mes_calendario = mes
        self.ano_calendario = ano
        self._criar_calendario(referencia)

    def _selecionar_data(self, valor: date) -> None:
        if self.alvo_calendario == "inicial":
            self.data_inicial = valor
        elif self.alvo_calendario == "final":
            self.data_final = valor
        elif self.alvo_calendario == "base":
            self.data_base = valor

        self._fechar_calendario()
        self._atualizar_tela()

    # ==========================================================
    # CÁLCULOS
    # ==========================================================

    def _atualizar_tela(self) -> None:
        self.botao_modo.config(text=f"{self.modo_atual.get()}  ⌄")

        self.frame_diferenca.grid_forget()
        self.frame_soma.grid_forget()

        if self.modo_atual.get() == MODO_DIFERENCA:
            self.frame_diferenca.grid(
                row=1,
                column=0,
                sticky="new",
            )
            self._atualizar_diferenca()
        else:
            self.frame_soma.grid(
                row=1,
                column=0,
                sticky="new",
            )
            self._atualizar_soma()

    def _atualizar_diferenca(self) -> None:
        self.botao_data_inicial.config(
            text=f"{self._formatar_data(self.data_inicial)}  ▣"
        )
        self.botao_data_final.config(
            text=f"{self._formatar_data(self.data_final)}  ▣"
        )

        diferenca = self._calcular_diferenca(
            self.data_inicial,
            self.data_final,
        )
        self.label_resultado_diferenca.config(text=diferenca[0])
        self.label_total_dias.config(text=diferenca[1])

    def _atualizar_soma(self) -> None:
        self.botao_data_base.config(
            text=f"{self._formatar_data(self.data_base)}  ▣"
        )
        self._atualizar_botoes_operacao()
        resultado = self._calcular_soma_data()
        self.label_resultado_soma.config(
            text=self._formatar_data(resultado)
        )

    def _calcular_diferenca(
        self,
        data_inicial: date,
        data_final: date,
    ) -> tuple[str, str]:
        if data_inicial == data_final:
            return "Mesmas datas", ""

        inicio, fim = sorted((data_inicial, data_final))
        total_dias = (fim - inicio).days

        anos = fim.year - inicio.year
        meses = fim.month - inicio.month
        dias = fim.day - inicio.day

        if dias < 0:
            mes_anterior = fim.month - 1
            ano_mes_anterior = fim.year

            if mes_anterior == 0:
                mes_anterior = 12
                ano_mes_anterior -= 1

            dias += calendar.monthrange(
                ano_mes_anterior,
                mes_anterior,
            )[1]
            meses -= 1

        if meses < 0:
            anos -= 1
            meses += 12

        partes = []
        if anos:
            partes.append(self._plural(anos, "ano", "anos"))
        if meses:
            partes.append(self._plural(meses, "mês", "meses"))
        if dias:
            partes.append(self._plural(dias, "dia", "dias"))

        return (
            self._juntar_partes(partes),
            f"Total: {self._plural(total_dias, 'dia', 'dias')}",
        )

    def _calcular_soma_data(self) -> date:
        self._normalizar_spinbox()

        anos = self.valor_anos.get()
        meses = self.valor_meses.get()
        dias = self.valor_dias.get()

        fator = 1 if self.operacao_soma.get() == "Adicionar" else -1

        resultado = self._adicionar_meses(
            self.data_base,
            fator * (anos * 12 + meses),
        )
        return resultado + self._delta_dias(fator * dias)

    @staticmethod
    def _adicionar_meses(data_base: date, meses: int) -> date:
        mes_zero = data_base.month - 1 + meses
        ano = data_base.year + mes_zero // 12
        mes = mes_zero % 12 + 1
        dia = min(data_base.day, calendar.monthrange(ano, mes)[1])
        return date(ano, mes, dia)

    @staticmethod
    def _delta_dias(dias: int):
        from datetime import timedelta

        return timedelta(days=dias)

    def _normalizar_spinbox(self) -> None:
        for variavel in (
            self.valor_anos,
            self.valor_meses,
            self.valor_dias,
        ):
            try:
                valor = int(variavel.get())
            except (tk.TclError, ValueError):
                valor = 0

            variavel.set(max(0, valor))

    def _atualizar_botoes_operacao(self) -> None:
        for valor, botao in (
            ("Adicionar", self.botao_adicionar),
            ("Subtrair", self.botao_subtrair),
        ):
            ativo = valor == self.operacao_soma.get()
            botao.config(
                bg=Tema.COR_BOTAO_IGUAL if ativo else Tema.COR_BOTAO,
                fg="#000000" if ativo else Tema.COR_TEXTO,
                activebackground=(
                    Tema.COR_BOTAO_IGUAL_HOVER
                    if ativo
                    else Tema.COR_BOTAO_HOVER
                ),
                activeforeground="#000000" if ativo else Tema.COR_TEXTO,
            )

    # ==========================================================
    # INTEGRAÇÃO
    # ==========================================================

    def fechar_paineis(self) -> None:
        self._fechar_menu_modo()
        self._fechar_calendario()

    def alternar_historico(self) -> None:
        self.fechar_paineis()

    def processar_tecla(self, _event: tk.Event) -> None:
        return None

    def _fechar_menu_modo(self) -> None:
        if self._painel_existe(self.frame_menu_modo):
            self.frame_menu_modo.destroy()

        self.frame_menu_modo = None

    def _fechar_calendario(self) -> None:
        if self._painel_existe(self.frame_calendario):
            self.frame_calendario.destroy()

        self.frame_calendario = None
        self.alvo_calendario = None

    @staticmethod
    def _painel_existe(painel: tk.Frame | None) -> bool:
        return painel is not None and bool(painel.winfo_exists())

    # ==========================================================
    # FORMATAÇÃO
    # ==========================================================

    def _obter_data_alvo(self) -> date:
        if self.alvo_calendario == "inicial":
            return self.data_inicial

        if self.alvo_calendario == "final":
            return self.data_final

        return self.data_base

    @staticmethod
    def _formatar_data(valor: date) -> str:
        return f"{valor.day} de {MESES[valor.month - 1]} de {valor.year}"

    @staticmethod
    def _plural(valor: int, singular: str, plural: str) -> str:
        palavra = singular if abs(valor) == 1 else plural
        return f"{valor} {palavra}"

    @staticmethod
    def _juntar_partes(partes: list[str]) -> str:
        if not partes:
            return "0 dias"

        if len(partes) == 1:
            return partes[0]

        return ", ".join(partes[:-1]) + f" e {partes[-1]}"
