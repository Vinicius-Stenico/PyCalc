import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from time import perf_counter

from recursos import caminho_recurso
from tema import Tema


class MenuLateral:
    """
    Controla o menu lateral rolável.

    Responsabilidades:
    - abrir e fechar o menu;
    - criar seções e opções;
    - manter Configurações fixa no rodapé;
    - selecionar modos;
    - controlar a rolagem pelo mouse.
    """

    TAMANHO_ICONE_MENU = 24

    # ÍCONE MODO PADRÃO
    ICONE_PADRAO_MENU = "modo:padrao"
    ICONE_PADRAO_FALLBACK = "▣"

    # ÍCONE MODO CIENTÍFICO
    ICONE_CIENTIFICO_MENU = "modo:cientifica"
    ICONE_CIENTIFICO_FALLBACK = "⚗"

    # ÍCONE MODO REPRESENTAÇÃO GRÁFICA
    ICONE_GRAFICO_MENU = "modo:grafico"
    ICONE_GRAFICO_FALLBACK = "⌁"

    # ÍCONE MODO PROGRAMADOR
    ICONE_PROGRAMADOR_MENU = "modo:programador"
    ICONE_PROGRAMADOR_FALLBACK = "</>"

    # ÍCONE MODO CÁLCULO DE DATA
    ICONE_DATA_MENU = "modo:data"
    ICONE_DATA_FALLBACK = "▦"

    # ÍCONES DOS CONVERSORES
    ICONE_MOEDA_MENU = "conversor:moeda"
    ICONE_VOLUME_MENU = "conversor:volume"
    ICONE_COMPRIMENTO_MENU = "conversor:comprimento"
    ICONE_PESO_MENU = "conversor:peso"
    ICONE_TEMPERATURA_MENU = "conversor:temperatura"
    ICONE_ENERGIA_MENU = "conversor:energia"
    ICONE_AREA_MENU = "conversor:area"
    ICONE_VELOCIDADE_MENU = "conversor:velocidade"
    ICONE_TEMPO_MENU = "conversor:tempo"
    ICONE_POTENCIA_MENU = "conversor:potencia"
    ICONE_DADOS_MENU = "conversor:dados"
    ICONE_PRESSAO_MENU = "conversor:pressao"
    ICONE_ANGULO_MENU = "conversor:angulo"

    ICONES_FALLBACK = {
        ICONE_PADRAO_MENU: "▣",
        ICONE_CIENTIFICO_MENU: "⚗",
        ICONE_GRAFICO_MENU: "⌁",
        ICONE_PROGRAMADOR_MENU: "</>",
        ICONE_DATA_MENU: "▦",
        ICONE_MOEDA_MENU: "♧",
        ICONE_VOLUME_MENU: "⬡",
        ICONE_COMPRIMENTO_MENU: "▥",
        ICONE_PESO_MENU: "⚖",
        ICONE_TEMPERATURA_MENU: "🌡",
        ICONE_ENERGIA_MENU: "⚡",
        ICONE_AREA_MENU: "▱",
        ICONE_VELOCIDADE_MENU: "✈",
        ICONE_TEMPO_MENU: "◷",
        ICONE_POTENCIA_MENU: "ϟ",
        ICONE_DADOS_MENU: "▧",
        ICONE_PRESSAO_MENU: "◒",
        ICONE_ANGULO_MENU: "∠",
    }

    ICONES_POR_TEMA = {
        ICONE_PADRAO_MENU: {
            "escuro": "icons/modos_icons/dark_mode/01_padrao_dark_mode.png",
            "claro": "icons/modos_icons/light_mode/01_padrao_light_mode.png",
        },
        ICONE_CIENTIFICO_MENU: {
            "escuro": "icons/modos_icons/dark_mode/02_cientifica_dark_mode.png",
            "claro": "icons/modos_icons/light_mode/02_cientifica_light_mode.png",
        },
        ICONE_GRAFICO_MENU: {
            "escuro": "icons/modos_icons/dark_mode/03_representacao_grafica_dark_mode.png",
            "claro": "icons/modos_icons/light_mode/03_representacao_grafica_light_mode.png",
        },
        ICONE_PROGRAMADOR_MENU: {
            "escuro": "icons/modos_icons/dark_mode/04_programador_dark_mode.png",
            "claro": "icons/modos_icons/light_mode/04_programador_light_mode.png",
        },
        ICONE_DATA_MENU: {
            "escuro": "icons/modos_icons/dark_mode/05_data_dark_mode.png",
            "claro": "icons/modos_icons/light_mode/05_data_light_mode.png",
        },
        ICONE_MOEDA_MENU: {
            "escuro": "icons/conversores_icons/dark_mode/06_moeda_dark_mode.png",
            "claro": "icons/conversores_icons/light_mode/06_moeda_light_mode.png",
        },
        ICONE_VOLUME_MENU: {
            "escuro": "icons/conversores_icons/dark_mode/07_volume_dark_mode.png",
            "claro": "icons/conversores_icons/light_mode/07_volume_light_mode.png",
        },
        ICONE_COMPRIMENTO_MENU: {
            "escuro": "icons/conversores_icons/dark_mode/08_comprimento_dark_mode.png",
            "claro": "icons/conversores_icons/light_mode/08_comprimento_light_mode.png",
        },
        ICONE_PESO_MENU: {
            "escuro": "icons/conversores_icons/dark_mode/09_peso_dark_mode.png",
            "claro": "icons/conversores_icons/light_mode/09_peso_light_mode.png",
        },
        ICONE_TEMPERATURA_MENU: {
            "escuro": "icons/conversores_icons/dark_mode/10_temperatura_dark_mode.png",
            "claro": "icons/conversores_icons/light_mode/10_temperatura_light_mode.png",
        },
        ICONE_ENERGIA_MENU: {
            "escuro": "icons/conversores_icons/dark_mode/11_energia_dark_mode.png",
            "claro": "icons/conversores_icons/light_mode/11_energia_light_mode.png",
        },
        ICONE_AREA_MENU: {
            "escuro": "icons/conversores_icons/dark_mode/12_area_dark_mode.png",
            "claro": "icons/conversores_icons/light_mode/12_area_light_mode.png",
        },
        ICONE_VELOCIDADE_MENU: {
            "escuro": "icons/conversores_icons/dark_mode/13_velocidade_dark_mode.png",
            "claro": "icons/conversores_icons/light_mode/13_velocidade_light_mode.png",
        },
        ICONE_TEMPO_MENU: {
            "escuro": "icons/conversores_icons/dark_mode/14_tempo_dark_mode.png",
            "claro": "icons/conversores_icons/light_mode/14_tempo_light_mode.png",
        },
        ICONE_POTENCIA_MENU: {
            "escuro": "icons/conversores_icons/dark_mode/15_potencia_dark_mode.png",
            "claro": "icons/conversores_icons/light_mode/15_potencia_light_mode.png",
        },
        ICONE_DADOS_MENU: {
            "escuro": "icons/conversores_icons/dark_mode/16_dados_dark_mode.png",
            "claro": "icons/conversores_icons/light_mode/16_dados_light_mode.png",
        },
        ICONE_PRESSAO_MENU: {
            "escuro": "icons/conversores_icons/dark_mode/17_pressao_dark_mode.png",
            "claro": "icons/conversores_icons/light_mode/17_pressao_light_mode.png",
        },
        ICONE_ANGULO_MENU: {
            "escuro": "icons/conversores_icons/dark_mode/18_angulo_dark_mode.png",
            "claro": "icons/conversores_icons/light_mode/18_angulo_light_mode.png",
        },
    }

    OPCOES_CALCULADORA = (
        (ICONE_PADRAO_MENU, "Padrão"),
        (ICONE_CIENTIFICO_MENU, "Científica"),
        (ICONE_GRAFICO_MENU, "Representação gráfica"),
        (ICONE_PROGRAMADOR_MENU, "Programador"),
        (ICONE_DATA_MENU, "Cálculo de data"),
    )

    OPCOES_CONVERSOR = (
        (ICONE_MOEDA_MENU, "Moeda"),
        (ICONE_VOLUME_MENU, "Volume"),
        (ICONE_COMPRIMENTO_MENU, "Comprimento"),
        (ICONE_PESO_MENU, "Peso e massa"),
        (ICONE_TEMPERATURA_MENU, "Temperatura"),
        (ICONE_ENERGIA_MENU, "Energia"),
        (ICONE_AREA_MENU, "Área"),
        (ICONE_VELOCIDADE_MENU, "Velocidade"),
        (ICONE_TEMPO_MENU, "Tempo"),
        (ICONE_POTENCIA_MENU, "Potência"),
        (ICONE_DADOS_MENU, "Dados"),
        (ICONE_PRESSAO_MENU, "Pressão"),
        (ICONE_ANGULO_MENU, "Ângulo"),
    )

    def __init__(
        self,
        parent: tk.Widget,
        label_modo: tk.Label,
        antes_de_abrir: Callable[[], None] | None = None,
        ao_selecionar: Callable[[str], None] | None = None,
    ) -> None:
        self.parent = parent
        self.label_modo = label_modo
        self.antes_de_abrir = antes_de_abrir
        self.ao_selecionar = ao_selecionar

        self.aberto = False
        self.animando = False

        self.proporcao_menu_aberto = 0.80
        self.duracao_abertura_ms = 220
        self.duracao_fechamento_ms = 320
        self.intervalo_animacao_ms = 10

        self.largura_painel = 0

        self.painel: tk.Frame | None = None
        self.canvas: tk.Canvas | None = None
        self.animacao_id: str | None = None

        self.acao_apos_fechar: Callable[[], None] | None = None

        self.barra_rolagem: tk.Canvas | None = None
        self.indicador_rolagem: int | None = None
        self.deslocamento_arraste_barra = 0
        self.imagens_menu: list[tk.PhotoImage] = []

        self.bind_mousewheel_id: str | None = None
        self.bind_scroll_up_id: str | None = None
        self.bind_scroll_down_id: str | None = None

    # ==========================================================
    # ABERTURA E FECHAMENTO
    # ==========================================================

    def alternar(self) -> None:
        """Abre ou fecha o menu lateral."""
        if self.animando:
            return

        if self.aberto:
            self.fechar()
        else:
            self.abrir()

    def abrir(self) -> None:
        """Cria o menu fora da tela e inicia a entrada lateral."""
        if self.aberto or self.animando:
            return

        if self.antes_de_abrir is not None:
            self.antes_de_abrir()

        self.parent.update_idletasks()

        self.largura_painel = max(
            1,
            int(
                self.parent.winfo_width()
                * self.proporcao_menu_aberto
            ),
        )

        self.animando = True

        self.painel = tk.Frame(
            self.parent,
            bg=Tema.COR_MENU,
            bd=0,
        )
        self.painel.place(
            x=-self.largura_painel,
            y=0,
            width=self.largura_painel,
            relheight=1,
        )
        self.painel.lift()

        self._criar_conteudo()

        inicio = perf_counter()
        self._animar_abertura(inicio)

    def fechar(
        self,
        acao_apos_fechar: Callable[[], None] | None = None,
    ) -> None:
        """Inicia a saída lateral do menu."""
        if self.animando:
            return

        if acao_apos_fechar is not None:
            self.acao_apos_fechar = acao_apos_fechar

        if (
            self.painel is None
            or not self.painel.winfo_exists()
        ):
            self._finalizar_fechamento()
            return

        self.animando = True
        self._desativar_rolagem_mouse()

        inicio = perf_counter()
        self._animar_fechamento(inicio)

    # ==========================================================
    # CONSTRUÇÃO DO MENU
    # ==========================================================

    def _criar_conteudo(self) -> None:
        self._criar_cabecalho()
        self._criar_rodape_configuracoes()
        frame_opcoes = self._criar_area_rolavel()

        self._criar_titulo_secao(frame_opcoes, "Calculadora", (10, 5))
        for icone, nome in self.OPCOES_CALCULADORA:
            self._criar_opcao(frame_opcoes, icone, nome)

        self._criar_titulo_secao(frame_opcoes, "Conversor", (14, 5))
        for icone, nome in self.OPCOES_CONVERSOR:
            self._criar_opcao(frame_opcoes, icone, nome)

    def _criar_cabecalho(self) -> None:
        cabecalho = tk.Frame(
            self.painel,
            bg=Tema.COR_MENU,
            height=50,
        )
        cabecalho.pack(fill="x", side="top")
        cabecalho.pack_propagate(False)

        botao_fechar = tk.Button(
            cabecalho,
            text="☰",
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_MENU_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI Symbol", 18),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=self.fechar,
        )
        botao_fechar.pack(side="left", padx=(8, 10), pady=5)

        titulo = tk.Label(
            cabecalho,
            text="Calculadora",
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 12, "bold"),
        )
        titulo.pack(side="left", pady=5)

    def _criar_rodape_configuracoes(self) -> None:
        rodape = tk.Frame(self.painel, bg=Tema.COR_MENU)
        rodape.pack(fill="x", side="bottom")

        botao = tk.Button(
            rodape,
            text="⚙    Configurações",
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_MENU_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=Tema.FONTE_MENU,
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="w",
            padx=15,
            pady=12,
            cursor="hand2",
            command=lambda: self._selecionar("Configurações"),
        )
        botao.pack(fill="x", padx=6, pady=(2, 6))

    def _criar_area_rolavel(self) -> tk.Frame:
        """
        Cria a área rolável mantendo cabeçalho e rodapé fixos.

        A barra lateral é desenhada em um Canvas para ficar fina,
        semelhante à barra exibida na referência.
        """
        area = tk.Frame(
            self.painel,
            bg=Tema.COR_MENU,
        )
        area.pack(
            fill="both",
            expand=True,
        )

        area.rowconfigure(0, weight=1)
        area.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            area,
            bg=Tema.COR_MENU,
            highlightthickness=0,
            bd=0,
            yscrollincrement=28,
        )
        self.canvas.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.barra_rolagem = tk.Canvas(
            area,
            width=8,
            bg=Tema.COR_MENU,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.barra_rolagem.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(2, 3),
        )

        self.indicador_rolagem = self.barra_rolagem.create_rectangle(
            2,
            0,
            6,
            30,
            fill=Tema.COR_TITULO_SECAO,
            outline="",
        )

        frame_opcoes = tk.Frame(
            self.canvas,
            bg=Tema.COR_MENU,
        )

        janela_opcoes = self.canvas.create_window(
            (0, 0),
            window=frame_opcoes,
            anchor="nw",
        )

        self.canvas.configure(
            yscrollcommand=self._atualizar_barra_rolagem,
        )

        frame_opcoes.bind(
            "<Configure>",
            lambda _evento: self._atualizar_regiao_rolagem(),
        )
        self.canvas.bind(
            "<Configure>",
            lambda evento: self._redimensionar_area_interna(
                janela_opcoes,
                evento.width,
            ),
        )

        self.barra_rolagem.bind(
            "<Button-1>",
            self._iniciar_arraste_barra,
        )
        self.barra_rolagem.bind(
            "<B1-Motion>",
            self._arrastar_barra,
        )

        self.parent.after_idle(
            self._atualizar_regiao_rolagem
        )

        return frame_opcoes

    def _redimensionar_area_interna(
        self,
        janela_opcoes: int,
        largura: int,
    ) -> None:
        """Mantém as opções com a mesma largura útil do Canvas."""
        if self.canvas is None:
            return

        if not self.canvas.winfo_exists():
            return

        self.canvas.itemconfigure(
            janela_opcoes,
            width=largura,
        )
        self._atualizar_regiao_rolagem()

    def _atualizar_regiao_rolagem(self) -> None:
        """Atualiza os limites do conteúdo que pode ser rolado."""
        if self.canvas is None:
            return

        if not self.canvas.winfo_exists():
            return

        self.canvas.update_idletasks()
        limites = self.canvas.bbox("all")

        if limites is None:
            return

        self.canvas.configure(
            scrollregion=limites,
        )

        primeiro, ultimo = self.canvas.yview()
        self._atualizar_barra_rolagem(
            str(primeiro),
            str(ultimo),
        )

    def _atualizar_barra_rolagem(
        self,
        primeiro: str,
        ultimo: str,
    ) -> None:
        """Sincroniza o indicador vertical com a posição do Canvas."""
        if (
            self.barra_rolagem is None
            or self.indicador_rolagem is None
        ):
            return

        if not self.barra_rolagem.winfo_exists():
            return

        inicio = float(primeiro)
        fim = float(ultimo)

        if inicio <= 0.0 and fim >= 1.0:
            self.barra_rolagem.grid_remove()
            return

        self.barra_rolagem.grid()

        self.barra_rolagem.update_idletasks()
        altura_barra = max(
            self.barra_rolagem.winfo_height(),
            1,
        )

        topo = inicio * altura_barra
        base = fim * altura_barra

        altura_minima = 32
        if base - topo < altura_minima:
            base = min(
                altura_barra,
                topo + altura_minima,
            )
            topo = max(
                0,
                base - altura_minima,
            )

        self.barra_rolagem.coords(
            self.indicador_rolagem,
            2,
            topo,
            6,
            base,
        )

    def _iniciar_arraste_barra(
        self,
        evento: tk.Event,
    ) -> None:
        """Inicia o arraste ou move a barra até o ponto clicado."""
        if (
            self.barra_rolagem is None
            or self.indicador_rolagem is None
        ):
            return

        coordenadas = self.barra_rolagem.coords(
            self.indicador_rolagem
        )
        if len(coordenadas) != 4:
            return

        _x1, topo, _x2, base = coordenadas

        if topo <= evento.y <= base:
            self.deslocamento_arraste_barra = int(
                evento.y - topo
            )
        else:
            self.deslocamento_arraste_barra = int(
                (base - topo) / 2
            )
            self._mover_barra_para(evento.y)

    def _arrastar_barra(
        self,
        evento: tk.Event,
    ) -> None:
        """Move o conteúdo conforme o indicador é arrastado."""
        self._mover_barra_para(evento.y)

    def _mover_barra_para(self, posicao_y: int) -> None:
        """Converte a posição da barra em uma fração de rolagem."""
        if (
            self.canvas is None
            or self.barra_rolagem is None
            or self.indicador_rolagem is None
        ):
            return

        coordenadas = self.barra_rolagem.coords(
            self.indicador_rolagem
        )
        if len(coordenadas) != 4:
            return

        _x1, topo_atual, _x2, base_atual = coordenadas
        altura_indicador = base_atual - topo_atual
        altura_barra = max(
            self.barra_rolagem.winfo_height(),
            1,
        )

        novo_topo = (
            posicao_y
            - self.deslocamento_arraste_barra
        )
        limite_topo = max(
            0,
            altura_barra - altura_indicador,
        )
        novo_topo = max(
            0,
            min(novo_topo, limite_topo),
        )

        fracao = novo_topo / altura_barra
        self.canvas.yview_moveto(fracao)

    def _criar_titulo_secao(
        self,
        container: tk.Widget,
        texto: str,
        margem_vertical: tuple[int, int],
    ) -> None:
        titulo = tk.Label(
            container,
            text=texto,
            bg=Tema.COR_MENU,
            fg=Tema.COR_TITULO_SECAO,
            font=Tema.FONTE_TITULO_MENU,
            anchor="w",
        )
        titulo.pack(
            fill="x",
            padx=17,
            pady=margem_vertical,
        )

    def _criar_opcao(
        self,
        container: tk.Widget,
        icone: str,
        nome: str,
    ) -> None:
        imagem = self._carregar_icone_imagem_menu(icone)
        texto = f"    {nome}" if imagem is not None else f"{self._icone_texto(icone)}    {nome}"

        cor_fundo = (
            Tema.COR_MENU_HOVER
            if nome == self.label_modo.cget("text")
            else Tema.COR_MENU
        )

        botao = tk.Button(
            container,
            text=texto,
            bg=cor_fundo,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_MENU_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=Tema.FONTE_MENU,
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="w",
            padx=15,
            pady=9,
            cursor="hand2",
            command=lambda modo=nome: self._selecionar(modo),
        )

        if imagem is not None:
            botao.config(
                image=imagem,
                compound="left",
            )

        botao.pack(fill="x", padx=6, pady=1)

    def _carregar_icone_imagem_menu(self, icone: str) -> tk.PhotoImage | None:
        if icone not in self.ICONES_POR_TEMA:
            return None

        caminho = self._caminho_icone_tema(icone)
        if not caminho.exists():
            if icone == self.ICONE_PADRAO_MENU:
                return self._criar_icone_padrao_fallback()
            return None
        
        try:
            imagem = self._padronizar_icone_menu(
                tk.PhotoImage(file=str(caminho))
            )
        except tk.TclError:
            if icone == self.ICONE_PADRAO_MENU:
                imagem = self._criar_icone_padrao_fallback()
            else:
                return None

        self.imagens_menu.append(imagem)
        return imagem

    def _caminho_icone_tema(self, icone: str) -> Path:
        tema_atual = "claro" if Tema.TEMA_ATUAL == "claro" else "escuro"
        caminho_relativo = self.ICONES_POR_TEMA[icone][tema_atual]
        return caminho_recurso(*Path(caminho_relativo).parts)

    def _padronizar_icone_menu(self, imagem: tk.PhotoImage) -> tk.PhotoImage:
        tamanho = self.TAMANHO_ICONE_MENU
        if imagem.width() == tamanho and imagem.height() == tamanho:
            return imagem

        icone = tk.PhotoImage(width=tamanho, height=tamanho)
        x = max(0, (tamanho - imagem.width()) // 2)
        y = max(0, (tamanho - imagem.height()) // 2)
        largura = min(imagem.width(), tamanho)
        altura = min(imagem.height(), tamanho)
        icone.tk.call(
            icone,
            "copy",
            imagem,
            "-from",
            0,
            0,
            largura,
            altura,
            "-to",
            x,
            y,
        )
        return icone

    def _criar_icone_padrao_fallback(self) -> tk.PhotoImage:
        imagem = tk.PhotoImage(
            width=self.TAMANHO_ICONE_MENU,
            height=self.TAMANHO_ICONE_MENU,
        )
        cor = "#1192b3"

        imagem.put(cor, to=(8, 5, 16, 6))
        imagem.put(cor, to=(8, 18, 16, 19))
        imagem.put(cor, to=(8, 5, 9, 19))
        imagem.put(cor, to=(15, 5, 16, 19))
        imagem.put(cor, to=(10, 7, 14, 9))

        for y in (11, 14, 17):
            for x in (9, 12, 15):
                imagem.put(cor, to=(x, y, x + 1, y + 1))

        return imagem

    def _icone_texto(self, icone: str) -> str:
        return self.ICONES_FALLBACK.get(icone, icone)

    # ==========================================================
    # SELEÇÃO DE MODOS
    # ==========================================================

    def _selecionar(self, modo: str) -> None:
        modos_calculadora = {
            nome for _icone, nome in self.OPCOES_CALCULADORA
        }

        if modo in modos_calculadora:
            self.label_modo.config(text=modo)

        def executar_selecao() -> None:
            if self.ao_selecionar is not None:
                self.ao_selecionar(modo)
            
        if self.aberto and not self.animando:
            self.fechar(
                acao_apos_fechar=executar_selecao,
            )
        else:
            executar_selecao()

    # ==========================================================
    # ROLAGEM
    # ==========================================================

    def _ativar_rolagem_mouse(self) -> None:
        """
        Ativa a roda do mouse enquanto o menu estiver aberto.

        O evento é vinculado à janela principal para continuar
        funcionando quando o cursor estiver sobre botões e labels.
        """
        if self.canvas is None:
            return

        janela = self.parent.winfo_toplevel()

        self.bind_mousewheel_id = janela.bind(
            "<MouseWheel>",
            self._rolar_com_mouse,
            add="+",
        )
        self.bind_scroll_up_id = janela.bind(
            "<Button-4>",
            self._rolar_linux,
            add="+",
        )
        self.bind_scroll_down_id = janela.bind(
            "<Button-5>",
            self._rolar_linux,
            add="+",
        )

    def _desativar_rolagem_mouse(self) -> None:
        """Remove apenas os eventos criados pelo menu lateral."""
        janela = self.parent.winfo_toplevel()

        if self.bind_mousewheel_id is not None:
            janela.unbind(
                "<MouseWheel>",
                self.bind_mousewheel_id,
            )

        if self.bind_scroll_up_id is not None:
            janela.unbind(
                "<Button-4>",
                self.bind_scroll_up_id,
            )

        if self.bind_scroll_down_id is not None:
            janela.unbind(
                "<Button-5>",
                self.bind_scroll_down_id,
            )

        self.bind_mousewheel_id = None
        self.bind_scroll_up_id = None
        self.bind_scroll_down_id = None

    def _rolar_com_mouse(
        self,
        evento: tk.Event,
    ) -> str | None:
        """Rola o conteúdo no Windows e no macOS."""
        if not self._pode_rolar():
            return None

        if evento.delta == 0:
            return None

        passos = int(-evento.delta / 120)

        if passos == 0:
            passos = -1 if evento.delta > 0 else 1

        self.canvas.yview_scroll(
            passos * 3,
            "units",
        )
        return "break"

    def _rolar_linux(
        self,
        evento: tk.Event,
    ) -> str | None:
        """Rola o conteúdo em sistemas que usam Button-4 e Button-5."""
        if not self._pode_rolar():
            return None

        direcao = -1 if evento.num == 4 else 1

        self.canvas.yview_scroll(
            direcao * 3,
            "units",
        )
        return "break"

    def _pode_rolar(self) -> bool:
        """Confirma que o menu está aberto e o cursor está sobre ele."""
        if (
            not self.aberto
            or self.canvas is None
            or not self.canvas.winfo_exists()
        ):
            return False

        if not self._cursor_esta_sobre_menu():
            return False

        primeiro, ultimo = self.canvas.yview()
        return not (
            primeiro <= 0.0
            and ultimo >= 1.0
        )

    def _cursor_esta_sobre_menu(self) -> bool:
        """Verifica se o ponteiro está dentro dos limites do painel."""
        if not self._painel_existe():
            return False

        posicao_x = self.parent.winfo_pointerx()
        posicao_y = self.parent.winfo_pointery()

        esquerda = self.painel.winfo_rootx()
        topo = self.painel.winfo_rooty()
        direita = esquerda + self.painel.winfo_width()
        inferior = topo + self.painel.winfo_height()

        return (
            esquerda <= posicao_x < direita
            and topo <= posicao_y < inferior
        )

    # ==========================================================
    # ANIMAÇÃO
    # ==========================================================

    def _animar_abertura(
        self,
        inicio: float,
    ) -> None:
        """Desliza o painel da esquerda até a posição aberta."""
        if not self._painel_existe():
            self._cancelar_estado_animacao()
            return

        progresso = self._calcular_progresso(
            inicio,
            self.duracao_abertura_ms,
        )
        progresso_suave = self._ease_out_cubico(progresso)

        posicao_inicial = -self.largura_painel
        posicao_x = round(
            posicao_inicial
            + (0 - posicao_inicial) * progresso_suave
        )

        self.painel.place_configure(x=posicao_x)

        if progresso < 1:
            self.animacao_id = self.parent.after(
                self.intervalo_animacao_ms,
                lambda: self._animar_abertura(inicio),
            )
            return

        self.painel.place_configure(x=0)
        self.aberto = True
        self.animando = False
        self.animacao_id = None

        self._ativar_rolagem_mouse()

    def _animar_fechamento(
        self,
        inicio: float,
    ) -> None:
        """Desliza o painel para fora da tela antes de destruí-lo."""
        if not self._painel_existe():
            self._finalizar_fechamento()
            return

        progresso = self._calcular_progresso(
            inicio,
            self.duracao_fechamento_ms,
        )
        progresso_suave = self._ease_in_out_cubico(progresso)

        posicao_final = -self.largura_painel
        posicao_x = round(
            posicao_final * progresso_suave
        )

        self.painel.place_configure(x=posicao_x)

        if progresso < 1:
            self.animacao_id = self.parent.after(
                self.intervalo_animacao_ms,
                lambda: self._animar_fechamento(inicio),
            )
            return

        self.painel.place_configure(x=posicao_final)
        self._finalizar_fechamento()

    def _finalizar_fechamento(self) -> None:
        """Destrói o menu e executa a ação pendente."""
        self._desativar_rolagem_mouse()

        if self._painel_existe():
            self.painel.destroy()

        self.painel = None
        self.canvas = None
        self.barra_rolagem = None
        self.indicador_rolagem = None
        self.animacao_id = None
        self.largura_painel = 0

        self.aberto = False
        self.animando = False

        acao = self.acao_apos_fechar
        self.acao_apos_fechar = None

        if acao is not None:
            acao()

    def _cancelar_estado_animacao(self) -> None:
        """Restaura os estados caso o painel deixe de existir."""
        self.painel = None
        self.canvas = None
        self.barra_rolagem = None
        self.indicador_rolagem = None
        self.animacao_id = None
        self.largura_painel = 0
        self.aberto = False
        self.animando = False

    def _painel_existe(self) -> bool:
        return (
            self.painel is not None
            and bool(self.painel.winfo_exists())
        )

    @staticmethod
    def _calcular_progresso(
        inicio: float,
        duracao_ms: int,
    ) -> float:
        tempo_decorrido_ms = (
            perf_counter() - inicio
        ) * 1000

        if duracao_ms <= 0:
            return 1.0

        return min(
            tempo_decorrido_ms / duracao_ms,
            1.0,
        )

    @staticmethod
    def _ease_out_cubico(progresso: float) -> float:
        """Começa rápido e desacelera ao terminar."""
        return 1 - (1 - progresso) ** 3

    @staticmethod
    def _ease_in_out_cubico(progresso: float) -> float:
        """Começa e termina suavemente."""
        if progresso < 0.5:
            return 4 * progresso ** 3

        return 1 - ((-2 * progresso + 2) ** 3) / 2
