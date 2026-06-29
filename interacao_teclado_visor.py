import tkinter as tk

from tema import Tema


BACKSPACE_CALCULADORA = "\u232b"
DIVISAO_CALCULADORA = "\u00f7"
MULTIPLICACAO_CALCULADORA = "\u00d7"
RAIZ_QUADRADA = "\u221ax"

CONTROL_MASK = 0x0004


class InteracaoTecladoVisorMixin:
    """Adiciona teclado e edicao direta do visor aos modos da calculadora."""

    def _configurar_visor_editavel(self) -> None:
        self.visor.config(
            insertbackground=Tema.COR_VISOR,
            insertontime=0,
            insertofftime=0,
            selectbackground=Tema.COR_BOTAO_IGUAL,
            selectforeground="#000000",
        )
        self.visor.bind("<KeyPress>", self.processar_tecla)
        self.visor.bind("<ButtonRelease-1>", self._ao_clicar_visor)
        self.visor.bind("<FocusIn>", self._ao_focar_visor)

    def _ao_acionar_botao_calculadora(self, valor: str) -> None:
        self.ao_clicar(valor)
        self._focar_visor_para_teclado()

    def processar_tecla(self, event: tk.Event) -> str | None:
        if self._eh_tecla_modificadora(event):
            return None

        if self._tratar_atalho_controle(event):
            return "break"

        if self._tratar_atalho_funcao(event):
            return "break"

        if event.keysym in {"Left", "Right", "Home", "End"}:
            return None

        if event.keysym in {"Return", "KP_Enter"}:
            self.ao_clicar("=")
            return "break"

        if event.keysym == "Escape":
            self.ao_clicar("C")
            return "break"

        if event.keysym == "BackSpace":
            if self._visor_esta_com_foco():
                self._apagar_no_visor(backspace=True)
            else:
                self.ao_clicar(BACKSPACE_CALCULADORA)
            return "break"

        if event.keysym == "Delete":
            if self._visor_esta_com_foco() and self._visor_tem_selecao():
                self._apagar_no_visor(backspace=False)
            else:
                self.ao_clicar("CE")
            return "break"

        valor = self._valor_calculadora_para_tecla(event)

        if valor is None:
            return "break" if event.widget == self.visor else None

        if valor.isdigit() or valor == ".":
            if self._visor_esta_com_foco():
                self._digitar_no_visor(valor)
            else:
                self.ao_clicar(valor)
            return "break"

        self.ao_clicar(valor)
        return "break"

    def _tratar_atalho_controle(self, event: tk.Event) -> bool:
        if not self._controle_pressionado(event):
            return False

        tecla = event.keysym.lower()

        if tecla == "a":
            self._selecionar_todo_visor()
            return True

        if tecla == "c":
            self._copiar_visor()
            return True

        if tecla == "v":
            self._colar_no_visor()
            return True

        if tecla == "x":
            self._copiar_visor()
            self._definir_texto_visor("0")
            return True

        if tecla in {"backspace", "delete"}:
            self.ao_clicar("CE")
            return True

        comandos_memoria = {
            "l": "MC",
            "r": "MR",
            "m": "MS",
            "p": "M+",
            "q": "M-",
        }

        comando_memoria = comandos_memoria.get(tecla)
        if comando_memoria is not None:
            self.ao_clicar(comando_memoria)
            return True

        if tecla == "h":
            self.alternar_historico()
            return True

        if tecla == "d" and self._shift_pressionado(event):
            self.historico.limpar_historico()
            return True

        return False

    def _tratar_atalho_funcao(self, event: tk.Event) -> bool:
        if event.keysym == "F9":
            self.ao_clicar("+/-")
            return True

        if event.keysym in {"F3", "F4", "F5"}:
            modo = {
                "F3": "DEG",
                "F4": "RAD",
                "F5": "GRAD",
            }[event.keysym]

            if hasattr(self, "modo_angular"):
                self.modo_angular = modo
                self.botao_modo_angular.config(text=modo)
                return True

        return False

    def _valor_calculadora_para_tecla(
        self,
        event: tk.Event,
    ) -> str | None:
        if event.char and event.char.isdigit():
            return event.char

        mapa_por_char = {
            "+": "+",
            "-": "-",
            "*": MULTIPLICACAO_CALCULADORA,
            "x": MULTIPLICACAO_CALCULADORA,
            "X": MULTIPLICACAO_CALCULADORA,
            "/": DIVISAO_CALCULADORA,
            "=": "=",
            "%": "%",
            ".": ".",
            ",": ".",
            "@": RAIZ_QUADRADA,
            "r": "1/x",
            "R": "1/x",
            "q": "x\u00b2",
            "Q": "x\u00b2",
            "(": "(",
            ")": ")",
        }

        if event.char in mapa_por_char:
            return mapa_por_char[event.char]

        mapa_por_keysym = {
            "KP_Add": "+",
            "KP_Subtract": "-",
            "KP_Multiply": MULTIPLICACAO_CALCULADORA,
            "KP_Divide": DIVISAO_CALCULADORA,
            "KP_Decimal": ".",
        }

        return mapa_por_keysym.get(event.keysym)

    def _digitar_no_visor(self, valor: str) -> None:
        if getattr(self, "resultado_indefinido", False):
            self._limpar_resultado_indefinido(valor)
            return

        texto_atual = self.texto_visor.get()

        if (
            self.substituir_visor
            and not self._visor_tem_selecao()
        ) or (
            valor.isdigit()
            and texto_atual == "0"
            and not self._visor_tem_selecao()
        ) or texto_atual == "Erro":
            texto_atual = "0"
            inicio = 0
            fim = len(texto_atual)
        else:
            inicio, fim = self._intervalo_selecao_ou_cursor()

        texto_sem_selecao = texto_atual[:inicio] + texto_atual[fim:]

        if valor == "." and "." in texto_sem_selecao:
            return

        novo_texto = texto_atual[:inicio] + valor + texto_atual[fim:]

        if novo_texto.startswith("."):
            novo_texto = "0" + novo_texto
            inicio += 1

        if novo_texto.startswith("-."):
            novo_texto = "-0" + novo_texto[1:]
            inicio += 1

        self._definir_texto_visor(novo_texto, inicio + len(valor))

    def _apagar_no_visor(self, backspace: bool) -> None:
        if getattr(self, "resultado_indefinido", False):
            self._limpar_resultado_indefinido("0")
            return

        texto_atual = self.texto_visor.get()

        if self._visor_tem_selecao():
            inicio, fim = self._intervalo_selecao_ou_cursor()
        else:
            cursor = self.visor.index(tk.INSERT)

            if backspace:
                if cursor <= 0:
                    return

                inicio = cursor - 1
                fim = cursor
            else:
                if cursor >= len(texto_atual):
                    return

                inicio = cursor
                fim = cursor + 1

        novo_texto = texto_atual[:inicio] + texto_atual[fim:]

        if novo_texto in {"", "-"}:
            novo_texto = "0"
            inicio = len(novo_texto)

        self._definir_texto_visor(novo_texto, inicio)

    def _definir_texto_visor(
        self,
        texto: str,
        cursor: int | None = None,
    ) -> bool:
        texto = texto.replace(",", ".")

        if not self._texto_visor_valido(texto):
            return False

        self.texto_visor.set(texto)
        self.numero_atual = float(texto)
        self.substituir_visor = False

        if hasattr(self, "_mostrar_botao_ce"):
            self._mostrar_botao_ce()

        self.visor.focus_set()

        if cursor is not None:
            self.visor.icursor(max(0, min(cursor, len(texto))))

        return True

    def _texto_visor_valido(self, texto: str) -> bool:
        if texto.count(".") > 1:
            return False

        if texto in {"", "-", ".", "-."}:
            return False

        try:
            float(texto)
        except ValueError:
            return False

        return True

    def _intervalo_selecao_ou_cursor(self) -> tuple[int, int]:
        if self._visor_tem_selecao():
            return (
                self.visor.index(tk.SEL_FIRST),
                self.visor.index(tk.SEL_LAST),
            )

        cursor = self.visor.index(tk.INSERT)
        return cursor, cursor

    def _selecionar_todo_visor(self) -> None:
        self.visor.focus_set()
        self.visor.selection_range(0, tk.END)
        self.visor.icursor(tk.END)

    def _copiar_visor(self) -> None:
        self.clipboard_clear()
        self.clipboard_append(self.texto_visor.get())

    def _colar_no_visor(self) -> None:
        try:
            texto = self.clipboard_get().strip()
        except tk.TclError:
            return

        texto = texto.replace(",", ".")

        if not self._texto_visor_valido(texto):
            return

        self._definir_texto_visor(texto, len(texto))

    def _ao_clicar_visor(self, _event: tk.Event) -> None:
        self.memoria.fechar_painel()
        self.historico.fechar_painel()

    def _ao_focar_visor(self, _event: tk.Event) -> None:
        self.visor.icursor(tk.END)

    def _visor_esta_com_foco(self) -> bool:
        return self.focus_get() == self.visor

    def _focar_visor_para_teclado(self) -> None:
        if self.visor.winfo_exists():
            self.visor.focus_set()
            self.visor.selection_clear()
            self.visor.icursor(tk.END)

    def _visor_tem_selecao(self) -> bool:
        try:
            self.visor.index(tk.SEL_FIRST)
            self.visor.index(tk.SEL_LAST)
        except tk.TclError:
            return False

        return True

    @staticmethod
    def _controle_pressionado(event: tk.Event) -> bool:
        return bool(event.state & CONTROL_MASK)

    @staticmethod
    def _shift_pressionado(event: tk.Event) -> bool:
        return bool(event.state & 0x0001)

    @staticmethod
    def _eh_tecla_modificadora(event: tk.Event) -> bool:
        return event.keysym in {
            "Alt_L",
            "Alt_R",
            "Control_L",
            "Control_R",
            "Shift_L",
            "Shift_R",
        }
