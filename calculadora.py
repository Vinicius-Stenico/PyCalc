import tkinter as tk
from pathlib import Path

from menu_lateral import MenuLateral
from modos.padrao import CalculadoraPadrao
from modos.cientifica import CalculadoraCientifica
from modos.data import CalculadoraData
from tema import Tema


class Calculadora(tk.Frame):
    """
    Controla a aplicação e coordena a troca entre os modos.

    Responsabilidades:
    - criar o cabeçalho geral;
    - manter o nome e a referência do modo atual;
    - abrir e fechar o menu lateral;
    - carregar o modo selecionado;
    - criar e configurar a janela principal.

    A interface e as regras específicas de cada modo ficam nos arquivos
    da pasta modos.
    """

    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, bg=Tema.COR_FUNDO)
        self.pack(fill="both", expand=True)

        self.nome_modo_atual = "Padrão"
        self.modo_atual: tk.Frame | None = None
        self.instancias_modos: dict[str, tk.Frame] = {}

        # Relaciona o nome exibido no menu à classe responsável pelo modo.
        # Novos modos devem ser adicionados aqui quando forem implementados.
        self.modos_disponiveis: dict[str, type[tk.Frame]] = {
            "Padrão": CalculadoraPadrao,
            "Científica": CalculadoraCientifica,
            "Cálculo de data": CalculadoraData,
        }

        self._configurar_interacao_botoes()
        self._configurar_atalhos_teclado()
        self._configurar_layout()
        self._criar_topo()
        self._criar_area_modo()
        self._criar_menu_lateral()

        self._precarregar_modos()
        self._carregar_modo("Padrão")

    # ==========================================================
    # CONSTRUÇÃO DA APLICAÇÃO
    # ==========================================================

    def _configurar_interacao_botoes(self) -> None:
        """
        Aplica o efeito de hover a todos os botões da aplicação.

        O efeito também alcança botões criados posteriormente pelos modos,
        menus e painéis temporários.
        """
        self.bind_class(
            "Button",
            "<Enter>",
            self._ao_entrar_botao,
            add="+",
        )
        self.bind_class(
            "Button",
            "<Leave>",
            self._ao_sair_botao,
            add="+",
        )

    def _configurar_atalhos_teclado(self) -> None:
        """Encaminha teclas ao modo aberto no momento."""
        self.master.bind_all("<KeyPress>", self._ao_pressionar_tecla)

    def _ao_pressionar_tecla(self, evento: tk.Event) -> str | None:
        if self._tratar_atalho_modo(evento):
            return "break"

        if self.modo_atual is None:
            return None

        processar_tecla = getattr(
            self.modo_atual,
            "processar_tecla",
            None,
        )

        if callable(processar_tecla):
            return processar_tecla(evento)

        return None

    def _tratar_atalho_modo(self, evento: tk.Event) -> bool:
        if not self._ctrl_alt_pressionados(evento):
            return False

        if self._foco_esta_no_visor():
            return False

        if evento.keysym in {"1", "KP_1"}:
            self.selecionar_modo("Padrão")
            return True

        if evento.keysym in {"2", "KP_2"}:
            self.selecionar_modo("Científica")
            return True

        return False

    @staticmethod
    def _ctrl_alt_pressionados(evento: tk.Event) -> bool:
        return bool(evento.state & 0x0004 and evento.state & 0x0008)

    def _foco_esta_no_visor(self) -> bool:
        widget_focado = self.master.focus_get()
        return (
            self.modo_atual is not None
            and widget_focado == getattr(self.modo_atual, "visor", None)
        )

    def _ao_entrar_botao(self, evento: tk.Event) -> None:
        """Usa a cor ativa do botão enquanto o mouse estiver sobre ele."""
        botao = evento.widget

        if not isinstance(botao, tk.Button):
            return

        botao.config(cursor="arrow")

        if str(botao.cget("state")) == "disabled":
            return

        if getattr(botao, "_hover_ativo", False):
            return

        botao._hover_ativo = True
        botao._cor_fundo_antes_hover = str(
            botao.cget("background")
        )
        botao._cor_texto_antes_hover = str(
            botao.cget("foreground")
        )
        botao._cor_fundo_hover = str(
            botao.cget("activebackground")
        )
        botao._cor_texto_hover = str(
            botao.cget("activeforeground")
        )

        botao.config(
            bg=botao._cor_fundo_hover,
            fg=botao._cor_texto_hover,
        )

    def _ao_sair_botao(self, evento: tk.Event) -> None:
        """Restaura a aparência anterior quando o mouse deixa o botão."""
        botao = evento.widget

        if not isinstance(botao, tk.Button):
            return

        botao.config(cursor="arrow")

        if not getattr(botao, "_hover_ativo", False):
            return

        cor_fundo_atual = str(botao.cget("background"))
        cor_texto_atual = str(botao.cget("foreground"))

        # Se o clique alterou permanentemente a cor do botão, a nova
        # aparência é preservada ao sair com o mouse.
        if cor_fundo_atual == botao._cor_fundo_hover:
            botao.config(bg=botao._cor_fundo_antes_hover)

        if cor_texto_atual == botao._cor_texto_hover:
            botao.config(fg=botao._cor_texto_antes_hover)

        botao._hover_ativo = False

    def _configurar_layout(self) -> None:
        """Configura o cabeçalho e a área ocupada pelo modo atual."""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

    def _criar_topo(self) -> None:
        """Cria o cabeçalho compartilhado por todos os modos."""
        frame_topo = tk.Frame(
            self,
            bg=Tema.COR_TOPO,
        )
        frame_topo.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(8, 0),
        )

        frame_topo.columnconfigure(0, weight=0)
        frame_topo.columnconfigure(1, weight=1)
        frame_topo.columnconfigure(2, weight=0)

        botao_menu = tk.Button(
            frame_topo,
            text="☰",
            bg=Tema.COR_TOPO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=Tema.FONTE_ICONE_TOPO,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=self._alternar_menu,
        )
        botao_menu.grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 10),
        )

        self.label_modo = tk.Label(
            frame_topo,
            text=self.nome_modo_atual,
            bg=Tema.COR_TOPO,
            fg=Tema.COR_TEXTO,
            font=Tema.FONTE_TOPO,
        )
        self.label_modo.grid(
            row=0,
            column=1,
            sticky="w",
        )
        botao_historico = tk.Button(
            frame_topo,
            text="↺",
            bg=Tema.COR_TOPO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI Symbol", 16),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=self._alternar_historico,
        )
        botao_historico.grid(
            row=0,
            column=2,
            sticky="e",
        )

    def _criar_area_modo(self) -> None:
        """Cria o contêiner onde o modo selecionado será exibido."""
        self.area_modo = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        self.area_modo.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

        self.area_modo.columnconfigure(0, weight=1)
        self.area_modo.rowconfigure(0, weight=1)

    def _criar_menu_lateral(self) -> None:
        """Cria o menu responsável pela seleção dos modos."""
        self.menu_lateral = MenuLateral(
            parent=self,
            label_modo=self.label_modo,
            antes_de_abrir=self._fechar_paineis_modo_atual,
            ao_selecionar=self.selecionar_modo,
        )

    # ==========================================================
    # CONTROLE DO MENU
    # ==========================================================

    def _alternar_menu(self) -> None:
        """Abre ou fecha o menu lateral."""
        self.menu_lateral.alternar()

    def _alternar_historico(self) -> None:
        """Solicita ao modo atual que abra ou feche seu histórico."""
        if self.modo_atual is None:
            return

        alternar_historico = getattr(
            self.modo_atual,
            "alternar_historico",
            None,
        )

        if callable(alternar_historico):
            alternar_historico()

    def selecionar_modo(self, nome_modo: str) -> None:
        """
        Recebe a opção escolhida no menu e carrega o modo correspondente.
        """
        if nome_modo not in self.modos_disponiveis:
            print(f"{nome_modo} ainda não foi implementado")

            # Mantém o título coerente com o modo que continua aberto.
            self.label_modo.config(text=self.nome_modo_atual)
            return

        self._carregar_modo(nome_modo)

    # ==========================================================
    # TROCA DE MODOS
    # ==========================================================

    def _precarregar_modos(self) -> None:
        """Cria todos os modos antes da primeira troca visível."""
        for nome_modo, classe_modo in self.modos_disponiveis.items():
            modo = classe_modo(self.area_modo)
            modo.grid(
                row=0,
                column=0,
                sticky="nsew",
            )
            self.instancias_modos[nome_modo] = modo

        self.area_modo.update_idletasks()

    def _carregar_modo(self, nome_modo: str) -> None:
        """Mostra o modo solicitado sem reconstruir o layout a cada troca."""
        self._fechar_paineis_modo_atual()

        self.modo_atual = self.instancias_modos[nome_modo]
        self.modo_atual.tkraise()

        self.nome_modo_atual = nome_modo
        self.label_modo.config(text=nome_modo)
        self._focar_visor_modo_atual()

    def _focar_visor_modo_atual(self) -> None:
        if self.modo_atual is None:
            return

        focar_visor = getattr(
            self.modo_atual,
            "_focar_visor_para_teclado",
            None,
        )

        if callable(focar_visor):
            self.after_idle(focar_visor)

    def _destruir_modo_atual(self) -> None:
        """Fecha os painéis e remove o modo que está sendo exibido."""
        self._fechar_paineis_modo_atual()

        if (
            self.modo_atual is not None
            and self.modo_atual.winfo_exists()
        ):
            return

        return

    def _fechar_paineis_modo_atual(self) -> None:
        """
        Solicita ao modo atual que feche seus painéis temporários.

        Cada modo pode implementar o método fechar_paineis quando precisar
        limpar elementos antes da abertura do menu ou da troca de modo.
        """
        if self.modo_atual is None:
            return

        fechar_paineis = getattr(
            self.modo_atual,
            "fechar_paineis",
            None,
        )

        if callable(fechar_paineis):
            fechar_paineis()


# ==============================================================
# INICIALIZAÇÃO DO PROGRAMA
# ==============================================================


def criar_janela() -> tuple[tk.Tk, tk.PhotoImage | None]:
    """Cria e configura a janela principal da aplicação."""
    janela = tk.Tk()
    janela.title("Calculadora")
    janela.geometry("340x560")
    janela.minsize(320, 520)
    janela.configure(bg=Tema.COR_FUNDO)

    pasta_projeto = Path(__file__).resolve().parent
    caminho_icone = pasta_projeto / "icons" / "calculator.png"

    icone = None

    if caminho_icone.exists():
        icone = tk.PhotoImage(file=str(caminho_icone))
        janela.iconphoto(True, icone)

    Calculadora(janela)

    return janela, icone


def main() -> None:
    """Inicia a aplicação."""
    janela, _icone = criar_janela()
    janela.mainloop()


if __name__ == "__main__":
    main()
