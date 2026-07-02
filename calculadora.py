import tkinter as tk

from configuracoes import ConfiguracoesApp, TelaConfiguracoes
from menu_lateral import MenuLateral
from recursos import caminho_recurso
from modos.padrao import CalculadoraPadrao
from modos.cientifica import CalculadoraCientifica
from modos.data import CalculadoraData
from modos.moeda import CalculadoraMoeda
from modos.volume import CalculadoraVolume
from modos.comprimento import CalculadoraComprimento
from modos.peso_e_massa import CalculadoraPesoEMassa
from modos.temperatura import CalculadoraTemperatura
from modos.energia import CalculadoraEnergia
from modos.area import CalculadoraArea
from modos.velocidade import CalculadoraVelocidade
from modos.tempo import CalculadoraTempo
from modos.potencia import CalculadoraPotencia
from modos.dados import CalculadoraDados
from modos.pressao import CalculadoraPressao
from modos.angulo import CalculadoraAngulo
from modos.programador import CalculadoraProgramador
from modos.representacao_grafica import CalculadoraRepresentacaoGrafica
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

    def __init__(
        self,
        master: tk.Tk,
        configuracoes_app: ConfiguracoesApp | None = None,
    ) -> None:
        self.configuracoes_app = configuracoes_app or ConfiguracoesApp()
        self.configuracoes_app.aplicar_preferencia()

        super().__init__(master, bg=Tema.COR_FUNDO)
        self.pack(fill="both", expand=True)

        self.nome_modo_atual = "Padrão"
        self.nome_modo_antes_configuracoes = "Padrão"
        self.modo_atual: tk.Frame | None = None
        self.instancias_modos: dict[str, tk.Frame] = {}
        self.tela_configuracoes: TelaConfiguracoes | None = None
        self.configuracoes_abertas = False
        self.icone_topo: tk.PhotoImage | None = None

        # Relaciona o nome exibido no menu à classe responsável pelo modo.
        # Novos modos devem ser adicionados aqui quando forem implementados.
        self.modos_disponiveis: dict[str, type[tk.Frame]] = {
            "Padrão": CalculadoraPadrao,
            "Científica": CalculadoraCientifica,
            "Representação gráfica": CalculadoraRepresentacaoGrafica,
            "Programador": CalculadoraProgramador,
            "Cálculo de data": CalculadoraData,
            "Moeda": CalculadoraMoeda,
            "Volume": CalculadoraVolume,
            "Comprimento": CalculadoraComprimento,
            "Peso e massa": CalculadoraPesoEMassa,
            "Temperatura": CalculadoraTemperatura,
            "Energia": CalculadoraEnergia,
            "Área": CalculadoraArea,
            "Velocidade": CalculadoraVelocidade,
            "Tempo": CalculadoraTempo,
            "Potência": CalculadoraPotencia,
            "Dados": CalculadoraDados,
            "Pressão": CalculadoraPressao,
            "Ângulo": CalculadoraAngulo,
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
        self.frame_topo = tk.Frame(
            self,
            bg=Tema.COR_TOPO,
        )
        self.frame_topo.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(8, 0),
        )

        self.frame_topo.columnconfigure(0, weight=0)
        self.frame_topo.columnconfigure(1, weight=0)
        self.frame_topo.columnconfigure(2, weight=1)
        self.frame_topo.columnconfigure(3, weight=0)
        self.frame_topo.columnconfigure(4, weight=0)

        self.botao_menu = tk.Button(
            self.frame_topo,
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
        self.botao_menu.grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 10),
        )

        self.icone_topo = self._carregar_icone_topo()
        self.label_icone_topo = tk.Label(
            self.frame_topo,
            image=self.icone_topo,
            bg=Tema.COR_TOPO,
        )
        self.label_icone_topo.grid(
            row=0,
            column=1,
            sticky="w",
            padx=(0, 8),
        )
        self.label_icone_topo.grid_remove()

        self.label_modo = tk.Label(
            self.frame_topo,
            text=self.nome_modo_atual,
            bg=Tema.COR_TOPO,
            fg=Tema.COR_TEXTO,
            font=Tema.FONTE_TOPO,
        )
        self.label_modo.grid(
            row=0,
            column=2,
            sticky="w",
        )

        self.frame_acoes_modo = tk.Frame(
            self.frame_topo,
            bg=Tema.COR_TOPO,
        )
        self.frame_acoes_modo.grid(
            row=0,
            column=3,
            sticky="e",
            padx=(4, 4),
        )

        self.botao_historico = tk.Button(
            self.frame_topo,
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
        self.botao_historico.grid(
            row=0,
            column=4,
            sticky="e",
        )

    def _carregar_icone_topo(self) -> tk.PhotoImage | None:
        caminho_icone = caminho_recurso("icons", "PyCalc_main.png")
        if not caminho_icone.exists():
            return None

        imagem = tk.PhotoImage(file=str(caminho_icone))
        fator = max(1, int(max(imagem.width(), imagem.height()) / 20))
        if fator > 1:
            imagem = imagem.subsample(fator, fator)
        return imagem

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

        self.tela_configuracoes = TelaConfiguracoes(
            self.area_modo,
            preferencia_tema=self.configuracoes_app.preferencia_tema,
            ao_alterar_tema=self._alterar_tema_configuracoes,
            ao_voltar=self._voltar_configuracoes,
        )
        self.tela_configuracoes.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        self.tela_configuracoes.grid_remove()

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

        if not hasattr(self.modo_atual, "historico"):
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
        if nome_modo == "Configurações":
            self._abrir_configuracoes()
            return

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
            modo.grid_remove()
            self.instancias_modos[nome_modo] = modo

        self.area_modo.update_idletasks()

    def _carregar_modo(self, nome_modo: str) -> None:
        """Mostra o modo solicitado sem reconstruir o layout a cada troca."""
        self._fechar_paineis_modo_atual()
        self.configuracoes_abertas = False

        self.modo_atual = self.instancias_modos[nome_modo]
        self._exibir_frame_modo(self.modo_atual)
        self.modo_atual.tkraise()

        self.nome_modo_atual = nome_modo
        self.label_modo.config(text=nome_modo)
        self._configurar_topo_modo()
        self._atualizar_acoes_modo()
        self._atualizar_botao_historico()
        self._notificar_modo_exibido()
        self._focar_visor_modo_atual()

    def _abrir_configuracoes(self) -> None:
        if self.tela_configuracoes is None:
            return

        self._fechar_paineis_modo_atual()

        if not self.configuracoes_abertas:
            self.nome_modo_antes_configuracoes = self.nome_modo_atual

        self.configuracoes_abertas = True
        self.modo_atual = self.tela_configuracoes
        self._exibir_frame_modo(self.tela_configuracoes)
        self.tela_configuracoes.atualizar_preferencia(
            self.configuracoes_app.preferencia_tema
        )
        self.tela_configuracoes.tkraise()
        self.tela_configuracoes.ao_exibir()

        self._configurar_topo_configuracoes()

    def _voltar_configuracoes(self) -> None:
        destino = self.nome_modo_antes_configuracoes
        if destino not in self.instancias_modos:
            destino = "Padrão"

        self._carregar_modo(destino)

    def _configurar_topo_configuracoes(self) -> None:
        self.botao_menu.config(
            text="←",
            command=self._voltar_configuracoes,
            bg=Tema.COR_TOPO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
        )
        self.label_icone_topo.grid()
        self.label_modo.config(
            text="Calculadora",
            bg=Tema.COR_TOPO,
            fg=Tema.COR_TEXTO,
        )
        self.frame_acoes_modo.grid_remove()
        self.botao_historico.grid_remove()

    def _configurar_topo_modo(self) -> None:
        self.botao_menu.config(
            text="☰",
            command=self._alternar_menu,
            bg=Tema.COR_TOPO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
        )
        self.label_icone_topo.grid_remove()
        self.label_modo.config(bg=Tema.COR_TOPO, fg=Tema.COR_TEXTO)
        self.frame_acoes_modo.grid()

    def _exibir_frame_modo(self, frame_visivel: tk.Frame) -> None:
        for frame in self.instancias_modos.values():
            if frame is not frame_visivel and frame.winfo_manager():
                frame.grid_remove()

        if (
            self.tela_configuracoes is not None
            and self.tela_configuracoes is not frame_visivel
            and self.tela_configuracoes.winfo_manager()
        ):
            self.tela_configuracoes.grid_remove()

        if not frame_visivel.winfo_manager():
            frame_visivel.grid(row=0, column=0, sticky="nsew")

    def _notificar_modo_exibido(self) -> None:
        if self.modo_atual is None:
            return

        ao_exibir = getattr(self.modo_atual, "ao_exibir", None)
        if callable(ao_exibir):
            ao_exibir()

    def _atualizar_botao_historico(self) -> None:
        if not hasattr(self, "botao_historico"):
            return

        if (
            self.modo_atual is not None
            and hasattr(self.modo_atual, "historico")
        ):
            self.botao_historico.grid()
        else:
            self.botao_historico.grid_remove()

    def _atualizar_acoes_modo(self) -> None:
        if not hasattr(self, "frame_acoes_modo"):
            return

        for filho in self.frame_acoes_modo.winfo_children():
            filho.destroy()

        if self.modo_atual is None:
            return

        criar_acoes_topo = getattr(
            self.modo_atual,
            "criar_acoes_topo",
            None,
        )

        if callable(criar_acoes_topo):
            criar_acoes_topo(self.frame_acoes_modo)

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

    def _alterar_tema_configuracoes(self, preferencia: str) -> None:
        cores_anteriores = Tema.cores_tema()
        self.configuracoes_app.definir_tema(preferencia)
        self.configuracoes_app.aplicar_preferencia()
        self._atualizar_tema_global(cores_anteriores)

    def _atualizar_tema_global(self, cores_anteriores: dict[str, str]) -> None:
        cores_novas = Tema.cores_tema()
        self.master.configure(bg=Tema.COR_FUNDO)
        self._atualizar_widget_tema(self, cores_anteriores, cores_novas)

        if self.configuracoes_abertas:
            self._configurar_topo_configuracoes()
        else:
            self._configurar_topo_modo()
            self.label_modo.config(text=self.nome_modo_atual)
            self._atualizar_botao_historico()

        for modo in self.instancias_modos.values():
            grafico = getattr(modo, "grafico", None)
            redesenhar = getattr(grafico, "redesenhar", None)
            if callable(redesenhar):
                redesenhar()

        if self.tela_configuracoes is not None:
            self.tela_configuracoes.atualizar_tema()

    def _atualizar_widget_tema(
        self,
        widget: tk.Widget,
        cores_anteriores: dict[str, str],
        cores_novas: dict[str, str],
    ) -> None:
        mapa_cores = {
            valor.lower(): cores_novas[chave]
            for chave, valor in cores_anteriores.items()
            if chave in cores_novas
        }
        opcoes = (
            "background",
            "foreground",
            "activebackground",
            "activeforeground",
            "disabledforeground",
            "insertbackground",
            "selectbackground",
            "selectforeground",
            "highlightbackground",
            "highlightcolor",
            "troughcolor",
        )

        for opcao in opcoes:
            try:
                valor_atual = str(widget.cget(opcao)).lower()
            except tk.TclError:
                continue

            nova_cor = mapa_cores.get(valor_atual)
            if nova_cor is not None:
                try:
                    widget.config(**{opcao: nova_cor})
                except tk.TclError:
                    pass

        if isinstance(widget, tk.Button):
            widget._hover_ativo = False

        for filho in widget.winfo_children():
            self._atualizar_widget_tema(filho, cores_anteriores, cores_novas)

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
    configuracoes_app = ConfiguracoesApp()
    configuracoes_app.aplicar_preferencia()

    janela = tk.Tk()
    janela.title("Calculadora")
    janela.geometry("340x560")
    janela.minsize(320, 520)
    janela.configure(bg=Tema.COR_FUNDO)

    caminho_icone = caminho_recurso("icons", "PyCalc_main.png")

    icone = None

    if caminho_icone.exists():
        icone = tk.PhotoImage(file=str(caminho_icone))
        janela.iconphoto(True, icone)

    Calculadora(janela, configuracoes_app)

    return janela, icone


def main() -> None:
    """Inicia a aplicação."""
    janela, _icone = criar_janela()
    janela.mainloop()


if __name__ == "__main__":
    main()
