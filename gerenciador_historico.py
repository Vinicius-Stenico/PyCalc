import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass

from tema import Tema


@dataclass
class RegistroHistorico:
    expressao: str
    resultado: float


class GerenciadorHistorico:
    """
    Controla o armazenamento e o painel de histórico da calculadora.

    Responsabilidades:
    - armazenar as operações concluídas;
    - abrir e fechar o painel de histórico;
    - exibir as contas mais recentes primeiro;
    - limpar todo o histórico;
    - recuperar resultados para o visor.
    """

    def __init__(
        self,
        parent: tk.Widget,
        frame_referencia: tk.Widget,
        ao_recuperar_resultado: Callable[[float], None],
        ao_abrir_painel: Callable[[], None] | None = None,
    ) -> None:
        self.parent = parent
        self.frame_referencia = frame_referencia
        self.ao_recuperar_resultado = ao_recuperar_resultado
        self.ao_abrir_painel = ao_abrir_painel

        self.registros: list[RegistroHistorico] = []

        self.painel: tk.Frame | None = None
        self.canvas: tk.Canvas | None = None
        self.frame_lista: tk.Frame | None = None
        self.janela_canvas: int | None = None

    # ==========================================================
    # CONTROLE DOS REGISTROS
    # ==========================================================

    def adicionar(
        self,
        primeiro_numero: float,
        operador: str,
        segundo_numero: float,
        resultado: float,
    ) -> None:
        """Adiciona uma operação concluída ao histórico."""
        expressao = (
            f"{self._formatar_numero(primeiro_numero)} "
            f"{operador} "
            f"{self._formatar_numero(segundo_numero)}"
        )

        registro = RegistroHistorico(
            expressao=expressao,
            resultado=float(resultado),
        )

        self.registros.append(registro)
        self._atualizar_painel()

        print(
            "Histórico:",
            f"{registro.expressao} = "
            f"{self._formatar_numero(registro.resultado)}",
        )

    def adicionar_expressao(
        self,
        expressao: str,
        resultado: float,
    ) -> None:
        """
        Adiciona uma expressão já formatada.

        Útil para operações especiais, como:
        sqr(5), √25 e 1/4.
        """
        registro = RegistroHistorico(
            expressao=expressao,
            resultado=float(resultado),
        )

        self.registros.append(registro)
        self._atualizar_painel()

    def limpar_historico(self) -> None:
        """Apaga todas as operações salvas."""
        self.registros.clear()
        self._atualizar_painel()
        print("Histórico apagado")

    # ==========================================================
    # PAINEL
    # ==========================================================

    def alternar_painel(self) -> None:
        if self.painel_esta_aberto():
            self.fechar_painel()
        else:
            self.abrir_painel()

    def abrir_painel(self) -> None:
        if self.painel_esta_aberto():
            return

        if self.ao_abrir_painel is not None:
            self.ao_abrir_painel()

        self.parent.update_idletasks()
        self.frame_referencia.update_idletasks()

        posicao_y = (
            self.frame_referencia.winfo_rooty()
            - self.parent.winfo_rooty()
            + self.frame_referencia.winfo_height()
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

        self._criar_area_rolavel()
        self._criar_botao_lixeira()
        self._atualizar_painel()

    def fechar_painel(self) -> None:
        if self.painel_esta_aberto():
            self.painel.destroy()

        self.painel = None
        self.canvas = None
        self.frame_lista = None
        self.janela_canvas = None

    def painel_esta_aberto(self) -> bool:
        return (
            self.painel is not None
            and bool(self.painel.winfo_exists())
        )

    # ==========================================================
    # ÁREA ROLÁVEL
    # ==========================================================

    def _criar_area_rolavel(self) -> None:
        if self.painel is None:
            return

        container = tk.Frame(
            self.painel,
            bg=Tema.COR_PAINEL_MEMORIA,
        )
        container.pack(
            fill="both",
            expand=True,
            padx=0,
            pady=(0, 48),
        )

        self.canvas = tk.Canvas(
            container,
            bg=Tema.COR_PAINEL_MEMORIA,
            bd=0,
            highlightthickness=0,
        )
        self.canvas.pack(
            side="left",
            fill="both",
            expand=True,
        )

        barra_rolagem = tk.Scrollbar(
            container,
            orient="vertical",
            command=self.canvas.yview,
        )
        barra_rolagem.pack(
            side="right",
            fill="y",
        )

        self.canvas.configure(
            yscrollcommand=barra_rolagem.set,
        )

        self.frame_lista = tk.Frame(
            self.canvas,
            bg=Tema.COR_PAINEL_MEMORIA,
        )

        self.janela_canvas = self.canvas.create_window(
            0,
            0,
            window=self.frame_lista,
            anchor="nw",
        )

        self.frame_lista.bind(
            "<Configure>",
            self._atualizar_regiao_rolagem,
        )

        self.canvas.bind(
            "<Configure>",
            self._ajustar_largura_lista,
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            self._rolar_com_mouse,
        )

    def _atualizar_regiao_rolagem(
        self,
        evento: tk.Event,
    ) -> None:
        if self.canvas is None:
            return

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all"),
        )

    def _ajustar_largura_lista(
        self,
        evento: tk.Event,
    ) -> None:
        if (
            self.canvas is None
            or self.janela_canvas is None
        ):
            return

        self.canvas.itemconfigure(
            self.janela_canvas,
            width=evento.width,
        )

    def _rolar_com_mouse(
        self,
        evento: tk.Event,
    ) -> None:
        if (
            self.canvas is None
            or not self.painel_esta_aberto()
        ):
            return

        self.canvas.yview_scroll(
            int(-evento.delta / 120),
            "units",
        )

    # ==========================================================
    # ATUALIZAÇÃO DA INTERFACE
    # ==========================================================

    def _atualizar_painel(self) -> None:
        if (
            not self.painel_esta_aberto()
            or self.frame_lista is None
        ):
            return

        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        if self.registros:
            for registro in reversed(self.registros):
                self._criar_item_historico(registro)
        else:
            self._criar_mensagem_historico_vazio()

    def _criar_mensagem_historico_vazio(self) -> None:
        if self.frame_lista is None:
            return

        mensagem = tk.Label(
            self.frame_lista,
            text="Ainda não há histórico.",
            bg=Tema.COR_PAINEL_MEMORIA,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 11),
            anchor="w",
        )
        mensagem.pack(
            fill="x",
            padx=8,
            pady=12,
        )

    def _criar_item_historico(
        self,
        registro: RegistroHistorico,
    ) -> None:
        if self.frame_lista is None:
            return

        frame_item = tk.Frame(
            self.frame_lista,
            bg=Tema.COR_PAINEL_MEMORIA,
            cursor="hand2",
        )
        frame_item.pack(
            fill="x",
            padx=8,
            pady=(8, 2),
        )

        label_expressao = tk.Label(
            frame_item,
            text=f"{registro.expressao} =",
            bg=Tema.COR_PAINEL_MEMORIA,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 11),
            anchor="e",
        )
        label_expressao.pack(
            fill="x",
            padx=8,
        )

        label_resultado = tk.Label(
            frame_item,
            text=self._formatar_numero(
                registro.resultado
            ),
            bg=Tema.COR_PAINEL_MEMORIA,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 18, "bold"),
            anchor="e",
        )
        label_resultado.pack(
            fill="x",
            padx=8,
            pady=(0, 8),
        )

        widgets_clicaveis = (
            frame_item,
            label_expressao,
            label_resultado,
        )

        for widget in widgets_clicaveis:
            widget.bind(
                "<Button-1>",
                lambda evento,
                valor=registro.resultado:
                self._recuperar_do_historico(valor),
            )

            widget.bind(
                "<Enter>",
                lambda evento,
                frame=frame_item:
                self._alterar_cor_item(
                    frame,
                    Tema.COR_PAINEL_MEMORIA_HOVER,
                ),
            )

            widget.bind(
                "<Leave>",
                lambda evento,
                frame=frame_item:
                self._alterar_cor_item(
                    frame,
                    Tema.COR_PAINEL_MEMORIA,
                ),
            )

    def _alterar_cor_item(
        self,
        frame_item: tk.Frame,
        cor: str,
    ) -> None:
        frame_item.configure(bg=cor)

        for widget in frame_item.winfo_children():
            widget.configure(bg=cor)

    def _criar_botao_lixeira(self) -> None:
        if self.painel is None:
            return

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
            command=self.limpar_historico,
        )
        botao.place(
            relx=1,
            rely=1,
            x=-15,
            y=-12,
            anchor="se",
        )

    def _recuperar_do_historico(
        self,
        resultado: float,
    ) -> None:
        self.ao_recuperar_resultado(resultado)
        self.fechar_painel()

    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    @staticmethod
    def _formatar_numero(numero: float) -> str:
        numero = float(numero)

        if numero.is_integer():
            return str(int(numero))

        return str(numero)