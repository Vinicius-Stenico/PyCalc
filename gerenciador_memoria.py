import tkinter as tk
from collections.abc import Callable

from tema import Tema


class GerenciadorMemoria:
    """
    Controla os comandos de memória e o painel de histórico.

    Responsabilidades:
    - MS, MR, MC, M+ e M-;
    - armazenamento da lista de memórias;
    - criação dos botões de memória;
    - abertura e atualização do painel M⌄;
    - bloqueio visual dos botões de memória.
    """

    COMANDOS = ("MC", "MR", "M+", "M-", "MS", "M⌄")

    def __init__(
        self,
        parent: tk.Widget,
        obter_texto_visor: Callable[[], str],
        ao_recuperar_valor: Callable[[float], None],
        ao_clicar_botao: Callable[[str], None],
        ao_marcar_substituicao: Callable[[], None],
    ) -> None:
        self.parent = parent
        self.obter_texto_visor = obter_texto_visor
        self.ao_recuperar_valor = ao_recuperar_valor
        self.ao_clicar_botao = ao_clicar_botao
        self.ao_marcar_substituicao = ao_marcar_substituicao
        
        self.valores: list[float] = []
        self.botoes: dict[str, tk.Button] = {}
        self.painel: tk.Frame | None = None
        self.frame_memoria: tk.Frame | None = None
        self.bloqueado_por_erro = False

    # ==========================================================
    # CRIAÇÃO DA INTERFACE
    # ==========================================================

    def criar_botoes(self, linha: int = 3) -> None:
        """Cria a linha MC, MR, M+, M-, MS e M⌄."""
        self.frame_memoria = tk.Frame(self.parent, bg=Tema.COR_FUNDO)
        self.frame_memoria.grid(
            row=linha,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=8,
            pady=(0, 2),
        )

        for coluna, texto in enumerate(self.COMANDOS):
            self.frame_memoria.columnconfigure(coluna, weight=1)

            botao = tk.Button(
                self.frame_memoria,
                text=texto,
                font=Tema.FONTE_BOTAO_MEMORIA,
                bg=Tema.COR_FUNDO,
                fg=Tema.COR_TEXTO,
                activebackground=Tema.COR_BOTAO_HOVER,
                activeforeground=Tema.COR_TEXTO,
                relief="flat",
                bd=0,
                highlightthickness=0,
                cursor="hand2",
                command=lambda valor=texto: self.ao_clicar_botao(valor),
            )
            botao.grid(
                row=0,
                column=coluna,
                padx=2,
                pady=0,
                sticky="ew",
                ipady=2,
            )

            self.botoes[texto] = botao

        self._aplicar_estado_botoes()

    # ==========================================================
    # COMANDOS DE MEMÓRIA
    # ==========================================================

    def tratar_comando(self, comando: str) -> bool:
        """
        Processa um comando de memória.

        Retorna True quando o valor recebido pertence ao grupo de memória.
        """
        if comando not in self.COMANDOS:
            return False

        if comando == "MC":
            self.limpar_memorias()

        elif comando == "MR":
            self.recuperar_ultima_memoria()

        elif comando == "MS":
            self.salvar_valor_atual()

        elif comando == "M+":
            self.somar_valor_atual()

        elif comando == "M-":
            self.subtrair_valor_atual()

        elif comando == "M⌄":
            self.alternar_painel()

        return True

    def salvar_valor_atual(self) -> None:
        """Adiciona o valor atual do visor à lista de memórias."""
        numero = self._obter_numero_visor()
        if numero is None:
            return

        self.valores.append(numero)
        self.ao_marcar_substituicao()
        self._aplicar_estado_botoes()

        print("Número salvo na memória:", numero)
        print("Memórias:", self.valores)

    def recuperar_ultima_memoria(self) -> None:
        """Envia a memória mais recente de volta para a calculadora."""
        if not self.valores:
            return

        self.ao_recuperar_valor(self.valores[-1])

    def limpar_memorias(self) -> None:
        """Apaga todos os valores salvos."""
        self.valores.clear()
        self._atualizar_painel()
        self._aplicar_estado_botoes()
        print("Memória apagada")

    def somar_valor_atual(self) -> None:
        """Soma o valor do visor à memória mais recente."""
        numero = self._obter_numero_visor()
        if numero is None:
            return

        if self.valores:
            self.valores[-1] += numero
        else:
            self.valores.append(numero)

        self.ao_marcar_substituicao()
        self._atualizar_painel()
        self._aplicar_estado_botoes()
        print("Memória atual:", self.valores[-1])

    def subtrair_valor_atual(self) -> None:
        """Subtrai o valor do visor da memória mais recente."""
        numero = self._obter_numero_visor()
        if numero is None:
            return

        if self.valores:
            self.valores[-1] -= numero
        else:
            self.valores.append(-numero)

        self.ao_marcar_substituicao()
        self._atualizar_painel()
        self._aplicar_estado_botoes()
        print("Memória atual:", self.valores[-1])

    def _obter_numero_visor(self) -> float | None:
        try:
            return float(self.obter_texto_visor())
        except ValueError:
            print("O visor não contém um número válido")
            return None

    # ==========================================================
    # PAINEL DE HISTÓRICO
    # ==========================================================

    def alternar_painel(self) -> None:
        if self.painel_esta_aberto():
            self.fechar_painel()
        else:
            self.abrir_painel()

    def abrir_painel(self) -> None:
        if self.painel_esta_aberto():
            return
        
        if self.frame_memoria is None:
            return
        
        self.parent.update_idletasks()
        self.frame_memoria.update_idletasks()

        posicao_y = (
            self.frame_memoria.winfo_rooty()
            - self.parent.winfo_rooty()
            + self.frame_memoria.winfo_height()
        )

        altura_disponivel = (
            self.parent.winfo_height()
            - posicao_y
        )

        self.painel = tk.Frame(
            self.parent,
            bg=Tema.COR_PAINEL_MEMORIA,
            bd=0,
        )
        self.painel.place(
            x=0,
            y=posicao_y,
            relwidth=1,
            height=altura_disponivel,
        )
        self.painel.lift()

        self._aplicar_estado_botoes()
        self._atualizar_painel()

    def fechar_painel(self) -> None:
        if self.painel_esta_aberto():
            self.painel.destroy()

        self.painel = None
        self._aplicar_estado_botoes()

    def painel_esta_aberto(self) -> bool:
        return self.painel is not None and bool(self.painel.winfo_exists())

    def _atualizar_painel(self) -> None:
        if not self.painel_esta_aberto():
            return

        for widget in self.painel.winfo_children():
            widget.destroy()

        if self.valores:
            for numero in reversed(self.valores):
                self._criar_botao_valor(numero)
        else:
            self._criar_mensagem_memoria_vazia()

        self._criar_botao_lixeira()

    def _criar_mensagem_memoria_vazia(self) -> None:
        mensagem = tk.Label(
            self.painel,
            text="Não há nada salvo na memória",
            bg=Tema.COR_PAINEL_MEMORIA,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 13),
        )
        mensagem.pack(fill="x", padx=15, pady=30)

    def _criar_botao_valor(self, numero: float) -> None:
        botao = tk.Button(
            self.painel,
            text=self._formatar_numero(numero),
            bg=Tema.COR_PAINEL_MEMORIA,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_PAINEL_MEMORIA_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 17, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="e",
            cursor="hand2",
            command=lambda valor=numero: self._recuperar_do_painel(valor),
        )
        botao.pack(fill="x", padx=15, pady=4, ipady=6)

    def _criar_botao_lixeira(self) -> None:
        botao = tk.Button(
            self.painel,
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
            command=self.limpar_memorias,
        )
        botao.pack(side="bottom", anchor="e", padx=15, pady=12)

    def _recuperar_do_painel(self, numero: float) -> None:
        self.ao_recuperar_valor(numero)
        self.fechar_painel()

    # ==========================================================
    # ESTADO DOS BOTÕES
    # ==========================================================

    def bloquear_por_erro(self) -> None:
        self.bloqueado_por_erro = True
        self._aplicar_estado_botoes()

    def desbloquear_apos_erro(self) -> None:
        self.bloqueado_por_erro = False
        self._aplicar_estado_botoes()

    def _aplicar_estado_botoes(self) -> None:
        painel_aberto = self.painel_esta_aberto()
        possui_memoria = bool(self.valores)

        for nome, botao in self.botoes.items():
            if self.bloqueado_por_erro:
                botao.config(
                    state="disabled",
                    bg=Tema.COR_BOTAO_DESATIVADO,
                    disabledforeground=Tema.COR_TEXTO_DESATIVADO,
                )
                continue

            sem_memoria = (
                not possui_memoria
                and nome in {"MC", "MR", "M⌄"}
            )
            bloqueado_pelo_painel = (
                painel_aberto
                and nome != "M⌄"
            )
            desativado = sem_memoria or bloqueado_pelo_painel

            botao.config(
                state="disabled" if desativado else "normal",
                bg=Tema.COR_FUNDO,
                fg=Tema.COR_TEXTO,
                disabledforeground=Tema.COR_TEXTO_DESATIVADO,
            )

    @staticmethod
    def _formatar_numero(numero: float) -> str:
        numero = float(numero)
        return str(int(numero)) if numero.is_integer() else str(numero)
