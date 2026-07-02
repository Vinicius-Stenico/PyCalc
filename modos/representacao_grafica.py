from __future__ import annotations

from dataclasses import dataclass
import itertools
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from modos.grafico_motor import (
    ExpressaoCompilada,
    ExpressaoInvalida,
    compilar_expressao,
    quebrar_descontinuidades,
)
from tema import Tema


GRADE_TECLADO = (
    ("2nd", "π", "e", "C", "⌫"),
    ("x²", "1/x", "|x|", "x", "y"),
    ("√x", "(", ")", "=", "÷"),
    ("xʸ", "7", "8", "9", "×"),
    ("10ˣ", "4", "5", "6", "−"),
    ("log", "1", "2", "3", "+"),
    ("ln", "+/-", "0", ",", "↵"),
)

ROTULOS_SEGUNDO_TECLADO = {
    "x²": "x³",
    "√x": "∛x",
    "xʸ": "ʸ√x",
    "10ˣ": "2ˣ",
    "log": "logᵧx",
    "ln": "eˣ",
}

LARGURA_MINIMA_GRAFICO = 1e-6
LARGURA_MAXIMA_GRAFICO = 1e9


@dataclass
class ItemExpressao:
    texto: tk.StringVar
    erro: tk.StringVar
    visivel: tk.BooleanVar
    cor: str
    compilada: ExpressaoCompilada | None = None
    frame: tk.Frame | None = None
    entrada: tk.Entry | None = None
    placeholder_ativo: bool = False


class CalculadoraRepresentacaoGrafica(tk.Frame):
    """Modo de representação gráfica."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=Tema.COR_FUNDO)

        self.tela_atual = "grafico"
        self.xlim = [-10.0, 10.0]
        self.ylim = [-10.0, 10.0]
        self.unidade_angular = tk.StringVar(value="radianos")
        self.tema_grafico = tk.StringVar(value="claro")
        self.espessura_linha = tk.DoubleVar(value=2.0)

        self.itens: list[ItemExpressao] = []
        self.item_ativo: ItemExpressao | None = None
        self.ciclo_cores = itertools.cycle(Tema.CORES_CURVAS_GRAFICO)
        self.segundo_ativo = False
        self.hiperbolico_ativo = False

        self.frame_acoes_topo: tk.Frame | None = None
        self.botao_acao_grafico: tk.Button | None = None
        self.botao_acao_editor: tk.Button | None = None

        self._configurar_layout()
        self._criar_interface()
        self.adicionar_expressao()
        self.mostrar_tela("grafico")

    # ==========================================================
    # INTEGRAÇÃO COM A APLICAÇÃO
    # ==========================================================

    def criar_acoes_topo(self, parent: tk.Widget) -> None:
        self.frame_acoes_topo = tk.Frame(parent, bg=Tema.COR_TOPO)
        self.frame_acoes_topo.pack(side="right", padx=(0, 2))

        self.botao_acao_grafico = self._criar_botao_acao_topo(
            self.frame_acoes_topo,
            "⌁",
            lambda: self.mostrar_tela("grafico"),
        )
        self.botao_acao_editor = self._criar_botao_acao_topo(
            self.frame_acoes_topo,
            "fₓ",
            lambda: self.mostrar_tela("editor"),
        )
        self._atualizar_acoes_topo()

    def ao_exibir(self) -> None:
        self.grafico.redesenhar()

    def fechar_paineis(self) -> None:
        self.grafico.fechar_configuracoes()
        self.editor.teclado.fechar_menu()

    def processar_tecla(self, evento: tk.Event) -> str | None:
        if evento.keysym == "Escape":
            self.fechar_paineis()
            return "break"

        if self.tela_atual != "editor":
            return None

        widget = self.winfo_toplevel().focus_get()
        if isinstance(widget, tk.Entry) and evento.keysym == "Return":
            self.validar_item_ativo()
            return "break"

        return None

    def _focar_visor_para_teclado(self) -> None:
        if self.tela_atual == "editor":
            self.editor.focar_entrada_ativa()

    # ==========================================================
    # CONSTRUÇÃO
    # ==========================================================

    def _configurar_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def _criar_interface(self) -> None:
        self.container = tk.Frame(self, bg=Tema.COR_FUNDO)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

        self.grafico = PainelGrafico(self.container, self)
        self.editor = EditorExpressoes(self.container, self)

        self.grafico.grid(row=0, column=0, sticky="nsew")
        self.editor.grid(row=0, column=0, sticky="nsew")

    def _criar_botao_acao_topo(
        self,
        parent: tk.Widget,
        texto: str,
        comando,
    ) -> tk.Button:
        botao = tk.Button(
            parent,
            text=texto,
            width=4,
            bg=Tema.COR_BOTAO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_IGUAL_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=comando,
        )
        botao.pack(side="left", padx=1, ipady=2)
        return botao

    # ==========================================================
    # EXPRESSÕES
    # ==========================================================

    def adicionar_expressao(self) -> ItemExpressao:
        item = ItemExpressao(
            texto=tk.StringVar(),
            erro=tk.StringVar(),
            visivel=tk.BooleanVar(value=True),
            cor=next(self.ciclo_cores),
        )
        self.itens.append(item)
        self.editor.recriar_lista_expressoes()
        self.editor.definir_placeholder(item)
        self.item_ativo = item
        self.after_idle(self.editor.focar_entrada_ativa)
        return item

    def remover_expressao(self, item: ItemExpressao) -> None:
        if item in self.itens:
            self.itens.remove(item)

        if not self.itens:
            self.adicionar_expressao()
            return

        if self.item_ativo == item:
            self.item_ativo = self.itens[-1]

        self.editor.recriar_lista_expressoes()
        self.grafico.redesenhar()

    def texto_real(self, item: ItemExpressao) -> str:
        if item.placeholder_ativo:
            return ""
        return item.texto.get().strip()

    def validar_item(
        self,
        item: ItemExpressao,
        silencioso: bool = False,
    ) -> bool:
        texto = self.texto_real(item)
        if not texto:
            item.compilada = None
            item.erro.set("" if silencioso else "Insira uma expressão.")
            self.editor.atualizar_estado_item(item)
            self.grafico.redesenhar()
            return False

        try:
            item.compilada = compilar_expressao(texto)
        except ExpressaoInvalida as erro:
            item.compilada = None
            item.erro.set(str(erro))
            self.editor.atualizar_estado_item(item)
            self.grafico.redesenhar()
            return False

        item.erro.set("")
        self.editor.atualizar_estado_item(item)
        self.grafico.redesenhar()
        return True

    def validar_item_ativo(self) -> bool:
        if self.item_ativo is None:
            return False

        return self.validar_item(self.item_ativo)

    def alternar_visibilidade(self, item: ItemExpressao) -> None:
        item.visivel.set(not item.visivel.get())
        self.editor.recriar_lista_expressoes()
        self.grafico.redesenhar()

    # ==========================================================
    # NAVEGAÇÃO
    # ==========================================================

    def mostrar_tela(self, tela: str) -> None:
        self.tela_atual = tela
        if tela == "grafico":
            self.grafico.tkraise()
            self.grafico.redesenhar()
        else:
            self.editor.tkraise()
            self.after_idle(self.editor.focar_entrada_ativa)

        self._atualizar_acoes_topo()

    def _atualizar_acoes_topo(self) -> None:
        botoes = {
            "grafico": self.botao_acao_grafico,
            "editor": self.botao_acao_editor,
        }

        for tela, botao in botoes.items():
            if botao is None:
                continue

            ativo = tela == self.tela_atual
            botao.config(
                bg=Tema.COR_BOTAO_IGUAL if ativo else Tema.COR_BOTAO,
                fg=Tema.COR_GRAFICO_TEXTO_ESCURO if ativo else Tema.COR_TEXTO,
                activebackground=(
                    Tema.COR_BOTAO_IGUAL_HOVER
                    if ativo
                    else Tema.COR_BOTAO_HOVER
                ),
            )


class PainelGrafico(tk.Frame):
    """Área cartesiana com Matplotlib embutido."""

    def __init__(
        self,
        parent: tk.Widget,
        controlador: CalculadoraRepresentacaoGrafica,
    ) -> None:
        super().__init__(parent, bg=Tema.COR_FUNDO)
        self.controlador = controlador

        self.arrastando = False
        self.inicio_arraste: tuple[int, int] | None = None
        self.xlim_inicial: tuple[float, float] | None = None
        self.ylim_inicial: tuple[float, float] | None = None
        self.rastreamento_ativo = False
        self.dados_linhas: list[
            tuple[ItemExpressao, np.ndarray, np.ndarray]
        ] = []
        self.marcador_rastreamento = None
        self.anotacao_rastreamento = None
        self.painel_config: tk.Frame | None = None
        self.bind_clique_fora: str | None = None
        self.bind_escape: str | None = None

        self._configurar_layout()
        self._criar_figura()
        self._criar_barras_flotantes()

    def _configurar_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def _criar_figura(self) -> None:
        self.figura = Figure(figsize=(4, 4), dpi=100)
        self.eixos = self.figura.add_subplot(111)
        self.figura.subplots_adjust(
            left=0.075,
            right=0.965,
            bottom=0.075,
            top=0.965,
        )

        self.canvas = FigureCanvasTkAgg(self.figura, master=self)
        self.widget_canvas = self.canvas.get_tk_widget()
        self.widget_canvas.grid(row=0, column=0, sticky="nsew")

        self.canvas.mpl_connect("button_press_event", self._ao_apertar_mouse)
        self.canvas.mpl_connect("button_release_event", self._ao_soltar_mouse)
        self.canvas.mpl_connect("motion_notify_event", self._ao_mover_mouse)
        self.canvas.mpl_connect("scroll_event", self._ao_rolar_mouse)

    def _criar_barras_flotantes(self) -> None:
        self.barra_superior = tk.Frame(
            self,
            bg=Tema.COR_GRAFICO_BARRA,
            bd=0,
        )
        self.barra_superior.place(
            relx=1.0,
            y=8,
            anchor="ne",
            x=-8,
        )

        self.botao_rastrear = self._criar_botao_flutuante(
            self.barra_superior,
            "⌖",
            self._alternar_rastreamento,
        )
        self._criar_botao_flutuante(
            self.barra_superior,
            "⇩",
            self.exportar_png,
        )
        self._criar_botao_flutuante(
            self.barra_superior,
            "⚙",
            self.alternar_configuracoes,
        )

        self.barra_zoom = tk.Frame(self, bg=Tema.COR_GRAFICO_BARRA, bd=0)
        self.barra_zoom.place(
            relx=1.0,
            rely=1.0,
            anchor="se",
            x=-8,
            y=-8,
        )

        self._criar_botao_flutuante(
            self.barra_zoom,
            "+",
            lambda: self.aplicar_zoom(0.75),
        ).pack_configure(side="top")
        self._criar_botao_flutuante(
            self.barra_zoom,
            "−",
            lambda: self.aplicar_zoom(1.25),
        ).pack_configure(side="top")
        self._criar_botao_flutuante(
            self.barra_zoom,
            "⌂",
            self.redefinir_visualizacao,
        ).pack_configure(side="top")

    def _criar_botao_flutuante(
        self,
        parent: tk.Widget,
        texto: str,
        comando,
    ) -> tk.Button:
        botao = tk.Button(
            parent,
            text=texto,
            width=3,
            bg=Tema.COR_GRAFICO_BARRA,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI Symbol", 12),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=comando,
        )
        botao.pack(side="left", padx=1, pady=1, ipady=2)
        return botao

    # ==========================================================
    # DESENHO
    # ==========================================================

    def redesenhar(self) -> None:
        if not self.winfo_exists():
            return

        self.eixos.clear()
        self.dados_linhas.clear()
        cores = self._cores_atuais()

        xmin, xmax = self.controlador.xlim
        ymin, ymax = self.controlador.ylim
        largura = xmax - xmin
        altura = ymax - ymin

        self.eixos.set_facecolor(cores["fundo"])
        self.figura.patch.set_facecolor(cores["fundo"])
        self.eixos.set_xlim(xmin, xmax)
        self.eixos.set_ylim(ymin, ymax)
        self.eixos.set_aspect("equal", adjustable="box")
        self.eixos.grid(True, color=cores["grade"], linewidth=0.8)
        self.eixos.axhline(0, color=cores["eixo"], linewidth=1.1)
        self.eixos.axvline(0, color=cores["eixo"], linewidth=1.1)
        self.eixos.xaxis.set_major_locator(MaxNLocator(nbins=7))
        self.eixos.yaxis.set_major_locator(MaxNLocator(nbins=7))
        self.eixos.tick_params(colors=cores["texto"], labelsize=8)

        for borda in self.eixos.spines.values():
            borda.set_color(cores["borda"])
            borda.set_linewidth(0.8)

        self._desenhar_marcas_eixos(xmin, xmax, ymin, ymax, cores)
        self._desenhar_expressoes(xmin, xmax, ymin, ymax, altura)
        self.canvas.draw_idle()

    def _cores_atuais(self) -> dict[str, str]:
        if self.controlador.tema_grafico.get() == "app":
            return {
                "fundo": Tema.COR_FUNDO,
                "grade": Tema.COR_BOTAO_HOVER,
                "eixo": Tema.COR_TEXTO_SECUNDARIO,
                "texto": Tema.COR_TEXTO_SECUNDARIO,
                "borda": Tema.COR_BOTAO_HOVER,
                "anotacao_fundo": Tema.COR_MENU,
                "anotacao_texto": Tema.COR_TEXTO,
            }

        return {
            "fundo": Tema.COR_GRAFICO_FUNDO,
            "grade": Tema.COR_GRAFICO_GRADE,
            "eixo": Tema.COR_GRAFICO_EIXO,
            "texto": Tema.COR_GRAFICO_TEXTO,
            "borda": Tema.COR_GRAFICO_BORDA,
            "anotacao_fundo": Tema.COR_GRAFICO_FUNDO,
            "anotacao_texto": Tema.COR_GRAFICO_TEXTO_ESCURO,
        }

    def _desenhar_marcas_eixos(
        self,
        xmin: float,
        xmax: float,
        ymin: float,
        ymax: float,
        cores: dict[str, str],
    ) -> None:
        largura = xmax - xmin
        altura = ymax - ymin

        self.eixos.annotate(
            "",
            xy=(xmax, 0),
            xytext=(xmax - largura * 0.06, 0),
            arrowprops={"arrowstyle": "->", "color": cores["eixo"]},
        )
        self.eixos.annotate(
            "",
            xy=(0, ymax),
            xytext=(0, ymax - altura * 0.06),
            arrowprops={"arrowstyle": "->", "color": cores["eixo"]},
        )
        self.eixos.text(
            xmax - largura * 0.04,
            -altura * 0.06,
            "x",
            color=cores["texto"],
        )
        self.eixos.text(
            largura * 0.025,
            ymax - altura * 0.06,
            "y",
            color=cores["texto"],
        )
        self.eixos.text(
            largura * 0.015,
            -altura * 0.055,
            "0",
            color=cores["texto"],
            fontsize=8,
        )

    def _desenhar_expressoes(
        self,
        xmin: float,
        xmax: float,
        ymin: float,
        ymax: float,
        altura: float,
    ) -> None:
        for item in self.controlador.itens:
            if (
                item.compilada is None
                or not item.visivel.get()
            ):
                continue

            try:
                if item.compilada.tipo == "explicita":
                    self._desenhar_funcao(item, xmin, xmax, altura)
                elif item.compilada.tipo == "implicita":
                    self._desenhar_implicita(item, xmin, xmax, ymin, ymax)
                else:
                    self._desenhar_desigualdade(
                        item,
                        xmin,
                        xmax,
                        ymin,
                        ymax,
                    )
            except Exception:
                item.erro.set("Não foi possível desenhar esta expressão.")
                self.controlador.editor.atualizar_estado_item(item)

    def _desenhar_funcao(
        self,
        item: ItemExpressao,
        xmin: float,
        xmax: float,
        altura: float,
    ) -> None:
        xs = np.linspace(xmin, xmax, 1400)
        ys = item.compilada.avaliar_y(
            xs,
            self.controlador.unidade_angular.get(),
        )
        ys = quebrar_descontinuidades(ys, altura)

        self.eixos.plot(
            xs,
            ys,
            color=item.cor,
            linewidth=self.controlador.espessura_linha.get(),
        )
        self.dados_linhas.append((item, xs, ys))

    def _desenhar_implicita(
        self,
        item: ItemExpressao,
        xmin: float,
        xmax: float,
        ymin: float,
        ymax: float,
    ) -> None:
        xs = np.linspace(xmin, xmax, 240)
        ys = np.linspace(ymin, ymax, 240)
        grade_x, grade_y = np.meshgrid(xs, ys)
        valores = item.compilada.avaliar_diferenca(
            grade_x,
            grade_y,
            self.controlador.unidade_angular.get(),
        )

        if np.all(np.isnan(valores)):
            return

        self.eixos.contour(
            grade_x,
            grade_y,
            valores,
            levels=[0],
            colors=[item.cor],
            linewidths=self.controlador.espessura_linha.get(),
        )

    def _desenhar_desigualdade(
        self,
        item: ItemExpressao,
        xmin: float,
        xmax: float,
        ymin: float,
        ymax: float,
    ) -> None:
        xs = np.linspace(xmin, xmax, 220)
        ys = np.linspace(ymin, ymax, 220)
        grade_x, grade_y = np.meshgrid(xs, ys)
        mascara = item.compilada.avaliar_desigualdade(
            grade_x,
            grade_y,
            self.controlador.unidade_angular.get(),
        )
        diferenca = item.compilada.avaliar_diferenca(
            grade_x,
            grade_y,
            self.controlador.unidade_angular.get(),
        )

        self.eixos.contourf(
            grade_x,
            grade_y,
            mascara.astype(float),
            levels=[0.5, 1.5],
            colors=[item.cor],
            alpha=0.16,
        )
        self.eixos.contour(
            grade_x,
            grade_y,
            diferenca,
            levels=[0],
            colors=[item.cor],
            linewidths=max(1.0, self.controlador.espessura_linha.get() - 0.5),
            linestyles=(
                "--" if item.compilada.operador in {"<", ">"} else "-"
            ),
        )

    # ==========================================================
    # INTERAÇÃO DO GRÁFICO
    # ==========================================================

    def _ao_apertar_mouse(self, evento) -> None:
        if evento.inaxes != self.eixos or evento.button != 1:
            return

        if self.rastreamento_ativo:
            self._atualizar_rastreamento(evento)
            return

        self.arrastando = True
        self.inicio_arraste = (evento.x, evento.y)
        self.xlim_inicial = tuple(self.controlador.xlim)
        self.ylim_inicial = tuple(self.controlador.ylim)

    def _ao_soltar_mouse(self, _evento) -> None:
        self.arrastando = False
        self.inicio_arraste = None
        self.xlim_inicial = None
        self.ylim_inicial = None

    def _ao_mover_mouse(self, evento) -> None:
        if self.rastreamento_ativo and evento.inaxes == self.eixos:
            self._atualizar_rastreamento(evento)
            return

        if (
            not self.arrastando
            or self.inicio_arraste is None
            or self.xlim_inicial is None
            or self.ylim_inicial is None
        ):
            return

        largura_pixels = max(self.widget_canvas.winfo_width(), 1)
        altura_pixels = max(self.widget_canvas.winfo_height(), 1)
        dx_pixels = evento.x - self.inicio_arraste[0]
        dy_pixels = evento.y - self.inicio_arraste[1]

        xmin, xmax = self.xlim_inicial
        ymin, ymax = self.ylim_inicial
        largura = xmax - xmin
        altura = ymax - ymin

        dx = dx_pixels * largura / largura_pixels
        dy = dy_pixels * altura / altura_pixels

        self.controlador.xlim = [xmin - dx, xmax - dx]
        self.controlador.ylim = [ymin - dy, ymax - dy]
        self.redesenhar()

    def _ao_rolar_mouse(self, evento) -> None:
        if evento.inaxes != self.eixos:
            return

        fator = 0.85 if evento.button == "up" else 1.18
        centro = (
            evento.xdata if evento.xdata is not None else 0,
            evento.ydata if evento.ydata is not None else 0,
        )
        self.aplicar_zoom(fator, centro)

    def aplicar_zoom(
        self,
        fator: float,
        centro: tuple[float, float] | None = None,
    ) -> None:
        xmin, xmax = self.controlador.xlim
        ymin, ymax = self.controlador.ylim
        cx, cy = centro or ((xmin + xmax) / 2, (ymin + ymax) / 2)

        nova_largura = (xmax - xmin) * fator
        nova_altura = (ymax - ymin) * fator
        if (
            not np.isfinite(nova_largura)
            or not np.isfinite(nova_altura)
            or nova_largura <= 0
            or nova_altura <= 0
        ):
            return

        nova_largura = min(
            max(nova_largura, LARGURA_MINIMA_GRAFICO),
            LARGURA_MAXIMA_GRAFICO,
        )
        nova_altura = min(
            max(nova_altura, LARGURA_MINIMA_GRAFICO),
            LARGURA_MAXIMA_GRAFICO,
        )

        self.controlador.xlim = [
            cx - nova_largura / 2,
            cx + nova_largura / 2,
        ]
        self.controlador.ylim = [
            cy - nova_altura / 2,
            cy + nova_altura / 2,
        ]
        self.redesenhar()

    def redefinir_visualizacao(self) -> None:
        self.controlador.xlim = [-10.0, 10.0]
        self.controlador.ylim = [-10.0, 10.0]
        self.redesenhar()

    # ==========================================================
    # BARRA SUPERIOR
    # ==========================================================

    def _alternar_rastreamento(self) -> None:
        self.rastreamento_ativo = not self.rastreamento_ativo
        self.botao_rastrear.config(
            bg=(
                Tema.COR_BOTAO_IGUAL
                if self.rastreamento_ativo
                else Tema.COR_GRAFICO_BARRA
            ),
            fg=(
                Tema.COR_GRAFICO_TEXTO_ESCURO
                if self.rastreamento_ativo
                else Tema.COR_TEXTO
            ),
        )

        if not self.rastreamento_ativo:
            self._limpar_rastreamento()

    def _atualizar_rastreamento(self, evento) -> None:
        if not self.dados_linhas or evento.xdata is None or evento.ydata is None:
            return

        melhor: tuple[float, ItemExpressao, float, float] | None = None
        altura = self.controlador.ylim[1] - self.controlador.ylim[0]

        for item, xs, ys in self.dados_linhas:
            if len(xs) == 0:
                continue

            distancias_x = np.abs(xs - evento.xdata)
            indice = int(np.nanargmin(distancias_x))
            y = ys[indice]
            if not np.isfinite(y):
                continue

            distancia = abs(y - evento.ydata)
            if melhor is None or distancia < melhor[0]:
                melhor = (distancia, item, xs[indice], y)

        if melhor is None or melhor[0] > altura * 0.08:
            self._limpar_rastreamento()
            return

        _distancia, item, x, y = melhor
        cores = self._cores_atuais()
        self._limpar_rastreamento(desenhar=False)
        (self.marcador_rastreamento,) = self.eixos.plot(
            [x],
            [y],
            "o",
            color=item.cor,
            markersize=7,
        )
        self.anotacao_rastreamento = self.eixos.annotate(
            f"({x:.4g}, {y:.4g})",
            xy=(x, y),
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=9,
            color=cores["anotacao_texto"],
            bbox={
                "boxstyle": "round,pad=0.25",
                "facecolor": cores["anotacao_fundo"],
                "edgecolor": item.cor,
            },
        )
        self.canvas.draw_idle()

    def _limpar_rastreamento(self, desenhar: bool = True) -> None:
        if self.marcador_rastreamento is not None:
            self.marcador_rastreamento.remove()
            self.marcador_rastreamento = None

        if self.anotacao_rastreamento is not None:
            self.anotacao_rastreamento.remove()
            self.anotacao_rastreamento = None

        if desenhar:
            self.canvas.draw_idle()

    def exportar_png(self) -> None:
        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar gráfico",
            defaultextension=".png",
            filetypes=(("Imagem PNG", "*.png"),),
        )
        if not caminho:
            return

        try:
            self.figura.savefig(
                caminho,
                dpi=160,
                facecolor=self.figura.get_facecolor(),
            )
        except Exception as exc:
            messagebox.showerror(
                "Exportar gráfico",
                f"Não foi possível salvar a imagem.\n{exc}",
                parent=self,
            )

    # ==========================================================
    # CONFIGURAÇÕES
    # ==========================================================

    def alternar_configuracoes(self) -> None:
        if self.painel_config is not None and self.painel_config.winfo_exists():
            self.fechar_configuracoes()
            return

        self._abrir_configuracoes()

    def _abrir_configuracoes(self) -> None:
        self.fechar_configuracoes()

        painel = tk.Frame(
            self,
            bg=Tema.COR_MENU,
            bd=1,
            relief="solid",
            highlightthickness=0,
        )
        painel.place(relx=1.0, y=46, x=-8, anchor="ne", width=245)
        painel.lift()
        self.painel_config = painel

        titulo = tk.Label(
            painel,
            text="Opções de gráfico",
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        )
        titulo.pack(fill="x", padx=12, pady=(10, 8))

        self.vars_limites = {
            "X-Mín.": tk.StringVar(value=f"{self.controlador.xlim[0]:g}"),
            "X-Máx.": tk.StringVar(value=f"{self.controlador.xlim[1]:g}"),
            "Y-Mín.": tk.StringVar(value=f"{self.controlador.ylim[0]:g}"),
            "Y-Máx.": tk.StringVar(value=f"{self.controlador.ylim[1]:g}"),
        }
        self.entradas_limites: dict[str, tk.Entry] = {}
        self.label_erro_config = tk.Label(
            painel,
            text="",
            bg=Tema.COR_MENU,
            fg=Tema.COR_ERRO,
            font=("Segoe UI", 8),
            anchor="w",
        )

        grade = tk.Frame(painel, bg=Tema.COR_MENU)
        grade.pack(fill="x", padx=12)
        for indice, (rotulo, variavel) in enumerate(self.vars_limites.items()):
            linha = indice // 2
            coluna = (indice % 2) * 2
            tk.Label(
                grade,
                text=rotulo,
                bg=Tema.COR_MENU,
                fg=Tema.COR_TEXTO_SECUNDARIO,
                font=("Segoe UI", 8),
            ).grid(row=linha, column=coluna, sticky="w", pady=3)
            entrada = tk.Entry(
                grade,
                textvariable=variavel,
                width=8,
                bg=Tema.COR_BOTAO,
                fg=Tema.COR_TEXTO,
                insertbackground=Tema.COR_TEXTO,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=Tema.COR_BOTAO_HOVER,
                highlightcolor=Tema.COR_BOTAO_IGUAL,
                font=("Segoe UI", 9),
            )
            entrada.grid(
                row=linha,
                column=coluna + 1,
                sticky="ew",
                padx=(4, 8),
                pady=3,
            )
            self.entradas_limites[rotulo] = entrada
            entrada.bind("<Return>", lambda _e: self._aplicar_limites())
            entrada.bind("<FocusOut>", lambda _e: self._aplicar_limites())

        self.label_erro_config.pack(fill="x", padx=12, pady=(2, 4))

        self._criar_radio_grupo(
            painel,
            "Unidades angulares",
            self.controlador.unidade_angular,
            (("Radianos", "radianos"), ("Graus", "graus"), ("Grados", "grados")),
            self.redesenhar,
        )

        tk.Label(
            painel,
            text="Espessura da linha",
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(8, 0))
        escala = tk.Scale(
            painel,
            from_=1,
            to=5,
            resolution=0.25,
            orient="horizontal",
            variable=self.controlador.espessura_linha,
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_IGUAL,
            highlightthickness=0,
            troughcolor=Tema.COR_BOTAO,
            command=lambda _valor: self.redesenhar(),
        )
        escala.pack(fill="x", padx=12)

        self._criar_radio_grupo(
            painel,
            "Tema do gráfico",
            self.controlador.tema_grafico,
            (("Sempre claro", "claro"), ("Combinar tema do aplicativo", "app")),
            self.redesenhar,
        )

        janela = self.winfo_toplevel()
        self.bind_clique_fora = janela.bind(
            "<Button-1>",
            self._fechar_config_ao_clicar_fora,
            add="+",
        )
        self.bind_escape = janela.bind(
            "<Escape>",
            lambda _e: self.fechar_configuracoes(),
            add="+",
        )

    def _criar_radio_grupo(
        self,
        parent: tk.Widget,
        titulo: str,
        variavel: tk.StringVar,
        opcoes: tuple[tuple[str, str], ...],
        comando,
    ) -> None:
        tk.Label(
            parent,
            text=titulo,
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(8, 0))

        frame = tk.Frame(parent, bg=Tema.COR_MENU)
        frame.pack(fill="x", padx=8)
        for texto, valor in opcoes:
            tk.Radiobutton(
                frame,
                text=texto,
                value=valor,
                variable=variavel,
                bg=Tema.COR_MENU,
                fg=Tema.COR_TEXTO,
                selectcolor=Tema.COR_MENU,
                activebackground=Tema.COR_MENU,
                activeforeground=Tema.COR_TEXTO,
                font=("Segoe UI", 9),
                command=comando,
            ).pack(anchor="w")

    def _aplicar_limites(self) -> None:
        valores: dict[str, float] = {}
        campos_invalidos: set[str] = set()

        for rotulo, variavel in self.vars_limites.items():
            texto = variavel.get().strip().replace(",", ".")
            try:
                valor = float(texto)
            except ValueError:
                campos_invalidos.add(rotulo)
                continue

            if not np.isfinite(valor):
                campos_invalidos.add(rotulo)
                continue

            valores[rotulo] = valor

        if campos_invalidos:
            self._marcar_campos_limite(campos_invalidos)
            self.label_erro_config.config(text="Use apenas valores numéricos finitos.")
            return

        xmin = valores["X-Mín."]
        xmax = valores["X-Máx."]
        ymin = valores["Y-Mín."]
        ymax = valores["Y-Máx."]

        if xmin >= xmax or ymin >= ymax:
            campos_invalidos = set()
            if xmin >= xmax:
                campos_invalidos.update(("X-Mín.", "X-Máx."))
            if ymin >= ymax:
                campos_invalidos.update(("Y-Mín.", "Y-Máx."))
            self._marcar_campos_limite(campos_invalidos)
            self.label_erro_config.config(
                text="O mínimo deve ser menor que o máximo."
            )
            return

        self._marcar_campos_limite(set())
        self.label_erro_config.config(text="")
        self.controlador.xlim = [xmin, xmax]
        self.controlador.ylim = [ymin, ymax]
        self.redesenhar()

    def _marcar_campos_limite(self, campos_invalidos: set[str]) -> None:
        for rotulo, entrada in getattr(self, "entradas_limites", {}).items():
            entrada.config(
                highlightbackground=(
                    Tema.COR_ERRO
                    if rotulo in campos_invalidos
                    else Tema.COR_BOTAO_HOVER
                ),
                highlightcolor=(
                    Tema.COR_ERRO
                    if rotulo in campos_invalidos
                    else Tema.COR_BOTAO_IGUAL
                ),
            )

    def _fechar_config_ao_clicar_fora(self, evento: tk.Event) -> None:
        if self.painel_config is None:
            return

        widget = evento.widget
        while widget is not None:
            if widget == self.painel_config:
                return
            widget = getattr(widget, "master", None)

        self.fechar_configuracoes()

    def fechar_configuracoes(self) -> None:
        janela = self.winfo_toplevel()
        if self.bind_clique_fora is not None:
            janela.unbind("<Button-1>", self.bind_clique_fora)
            self.bind_clique_fora = None

        if self.bind_escape is not None:
            janela.unbind("<Escape>", self.bind_escape)
            self.bind_escape = None

        if self.painel_config is not None and self.painel_config.winfo_exists():
            self.painel_config.destroy()

        self.painel_config = None


class EditorExpressoes(tk.Frame):
    """Editor de expressões e teclado matemático."""

    def __init__(
        self,
        parent: tk.Widget,
        controlador: CalculadoraRepresentacaoGrafica,
    ) -> None:
        super().__init__(parent, bg=Tema.COR_FUNDO)
        self.controlador = controlador
        self._configurar_layout()
        self._criar_interface()

    def _configurar_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

    def _criar_interface(self) -> None:
        self.frame_lista = tk.Frame(self, bg=Tema.COR_FUNDO)
        self.frame_lista.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=8,
            pady=(8, 6),
        )
        self.frame_lista.columnconfigure(0, weight=1)

        self.teclado = TecladoMatematico(self, self.controlador)
        self.teclado.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 4))

    def recriar_lista_expressoes(self) -> None:
        for filho in self.frame_lista.winfo_children():
            filho.destroy()

        for linha, item in enumerate(self.controlador.itens):
            self._criar_linha_item(linha, item)

        botao_adicionar = tk.Button(
            self.frame_lista,
            text="+ Expressão",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_BOTAO_IGUAL,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_BOTAO_IGUAL,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="w",
            cursor="hand2",
            command=self.controlador.adicionar_expressao,
        )
        botao_adicionar.grid(
            row=len(self.controlador.itens),
            column=0,
            sticky="ew",
            pady=(6, 0),
        )

    def _criar_linha_item(self, linha: int, item: ItemExpressao) -> None:
        frame = tk.Frame(
            self.frame_lista,
            bg=Tema.COR_FUNDO,
            highlightthickness=1,
            highlightbackground=Tema.COR_BOTAO_HOVER,
        )
        frame.grid(row=linha, column=0, sticky="ew", pady=4)
        frame.columnconfigure(2, weight=1)
        item.frame = frame

        faixa = tk.Frame(frame, bg=item.cor, width=5)
        faixa.grid(row=0, column=0, rowspan=2, sticky="ns")

        bloco_f = tk.Label(
            frame,
            text="f",
            bg=Tema.COR_BOTAO,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 15, "italic"),
            width=3,
        )
        bloco_f.grid(row=0, column=1, sticky="ns", padx=(6, 0), pady=6)

        entrada = tk.Entry(
            frame,
            textvariable=item.texto,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            insertbackground=Tema.COR_TEXTO,
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 16),
        )
        entrada.grid(row=0, column=2, sticky="ew", padx=8, pady=(8, 2))
        item.entrada = entrada
        entrada.bind("<FocusIn>", lambda _e, it=item: self._ao_focar(it))
        entrada.bind("<FocusOut>", lambda _e, it=item: self._ao_desfocar(it))
        entrada.bind("<Return>", lambda _e, it=item: self._validar_enter(it))
        entrada.bind("<KeyRelease>", lambda _e, it=item: self._validar_digitacao(it))

        botao_visivel = tk.Button(
            frame,
            text="●" if item.visivel.get() else "○",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI Symbol", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=lambda it=item: self.controlador.alternar_visibilidade(it),
        )
        botao_visivel.grid(row=0, column=3, padx=(0, 2))

        botao_excluir = tk.Button(
            frame,
            text="✕",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=lambda it=item: self.controlador.remover_expressao(it),
        )
        botao_excluir.grid(row=0, column=4, padx=(0, 6))

        label_erro = tk.Label(
            frame,
            textvariable=item.erro,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_ERRO,
            font=("Segoe UI", 8),
            anchor="w",
        )
        label_erro.grid(
            row=1,
            column=2,
            columnspan=3,
            sticky="ew",
            padx=8,
            pady=(0, 5),
        )

        self.atualizar_estado_item(item)

    def _validar_enter(self, item: ItemExpressao) -> str:
        self.controlador.item_ativo = item
        self.controlador.validar_item(item)
        return "break"

    def _validar_digitacao(self, item: ItemExpressao) -> None:
        if item.placeholder_ativo:
            return

        self.controlador.item_ativo = item
        if self.controlador.texto_real(item):
            self.controlador.validar_item(item, silencioso=True)

    def _ao_focar(self, item: ItemExpressao) -> None:
        self.controlador.item_ativo = item
        if item.placeholder_ativo:
            item.placeholder_ativo = False
            item.texto.set("")
            if item.entrada is not None:
                item.entrada.config(fg=Tema.COR_TEXTO)

        self.atualizar_estado_item(item)

    def _ao_desfocar(self, item: ItemExpressao) -> None:
        if not item.texto.get().strip():
            self.definir_placeholder(item)

    def definir_placeholder(self, item: ItemExpressao) -> None:
        if item.texto.get().strip():
            return

        item.placeholder_ativo = True
        item.texto.set("Insira uma expressão")
        item.erro.set("")
        if item.entrada is not None:
            item.entrada.config(fg=Tema.COR_TEXTO_SECUNDARIO)

    def atualizar_estado_item(self, item: ItemExpressao) -> None:
        if item.frame is None or item.entrada is None:
            return

        foco = self.controlador.item_ativo == item
        cor_borda = (
            Tema.COR_ERRO
            if item.erro.get()
            else Tema.COR_BOTAO_IGUAL
            if foco
            else Tema.COR_BOTAO_HOVER
        )
        item.frame.config(highlightbackground=cor_borda)

    def focar_entrada_ativa(self) -> None:
        item = self.controlador.item_ativo
        if item is not None and item.entrada is not None:
            item.entrada.focus_set()
            if item.placeholder_ativo:
                item.entrada.selection_range(0, tk.END)

    def entrada_ativa(self) -> tk.Entry | None:
        item = self.controlador.item_ativo
        if item is None:
            return None
        return item.entrada

    def inserir_texto(
        self,
        texto: str,
        deslocamento_cursor: int = 0,
    ) -> None:
        item = self.controlador.item_ativo
        entrada = self.entrada_ativa()
        if item is None or entrada is None:
            item = self.controlador.adicionar_expressao()
            entrada = item.entrada

        if item.placeholder_ativo:
            item.placeholder_ativo = False
            item.texto.set("")
            entrada.config(fg=Tema.COR_TEXTO)

        inicio = entrada.index(tk.INSERT)
        entrada.insert(tk.INSERT, texto)
        destino = inicio + len(texto) + deslocamento_cursor
        entrada.icursor(max(0, destino))
        entrada.focus_set()
        self.controlador.validar_item(item, silencioso=True)

    def apagar_ultimo(self) -> None:
        entrada = self.entrada_ativa()
        if entrada is None:
            return

        posicao = entrada.index(tk.INSERT)
        if posicao > 0:
            entrada.delete(posicao - 1, posicao)

    def limpar_entrada(self) -> None:
        item = self.controlador.item_ativo
        entrada = self.entrada_ativa()
        if item is None or entrada is None:
            return

        item.placeholder_ativo = False
        item.texto.set("")
        item.compilada = None
        item.erro.set("")
        entrada.config(fg=Tema.COR_TEXTO)
        entrada.focus_set()
        self.controlador.grafico.redesenhar()


class TecladoMatematico(tk.Frame):
    """Teclado virtual do editor gráfico."""

    def __init__(
        self,
        parent: tk.Widget,
        controlador: CalculadoraRepresentacaoGrafica,
    ) -> None:
        super().__init__(parent, bg=Tema.COR_FUNDO)
        self.controlador = controlador
        self.menu_aberto: tk.Frame | None = None
        self.bind_clique_fora: str | None = None
        self.bind_escape: str | None = None
        self.botoes_segundo: dict[str, tk.Button] = {}
        self._configurar_layout()
        self._criar_interface()

    def _configurar_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

    def _criar_interface(self) -> None:
        barra = tk.Frame(self, bg=Tema.COR_FUNDO)
        barra.grid(row=0, column=0, sticky="ew", pady=(0, 3))
        barra.columnconfigure((0, 1, 2), weight=1, uniform="menus")

        for coluna, texto in enumerate(("Trigonometria", "Desigualdades", "Função")):
            botao = tk.Button(
                barra,
                text=f"{texto} ⌄",
                bg=Tema.COR_FUNDO,
                fg=Tema.COR_TEXTO,
                activebackground=Tema.COR_BOTAO_HOVER,
                activeforeground=Tema.COR_TEXTO,
                font=("Segoe UI", 9),
                relief="flat",
                bd=0,
                highlightthickness=0,
                cursor="hand2",
                command=lambda nome=texto, col=coluna: self._abrir_menu(nome, col),
            )
            botao.grid(row=0, column=coluna, sticky="ew", padx=1)

        grade = tk.Frame(self, bg=Tema.COR_FUNDO)
        grade.grid(row=1, column=0, sticky="nsew")
        for coluna in range(5):
            grade.columnconfigure(coluna, weight=1, uniform="teclado_grafico")
        for linha in range(len(GRADE_TECLADO)):
            grade.rowconfigure(linha, weight=1, uniform="teclado_grafico")

        self.botao_segundo: tk.Button | None = None
        for linha, valores in enumerate(GRADE_TECLADO):
            for coluna, texto in enumerate(valores):
                botao = self._criar_botao(grade, texto)
                botao.grid(
                    row=linha,
                    column=coluna,
                    sticky="nsew",
                    padx=1,
                    pady=1,
                )
                if texto == "2nd":
                    self.botao_segundo = botao
                elif texto in ROTULOS_SEGUNDO_TECLADO:
                    self.botoes_segundo[texto] = botao

    def _criar_botao(self, parent: tk.Widget, texto: str) -> tk.Button:
        cor = Tema.COR_BOTAO_IGUAL if texto == "↵" else Tema.COR_BOTAO
        botao = tk.Button(
            parent,
            text=texto,
            bg=cor,
            fg=Tema.COR_TEXTO,
            activebackground=(
                Tema.COR_BOTAO_IGUAL_HOVER if texto == "↵" else Tema.COR_BOTAO_HOVER
            ),
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 13),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        botao.config(command=lambda b=botao: self._acionar(b.cget("text")))
        return botao

    def _acionar(self, valor: str) -> None:
        self.fechar_menu()
        editor = self.controlador.editor

        if valor == "2nd":
            self.controlador.segundo_ativo = not self.controlador.segundo_ativo
            self._atualizar_botao_segundo()
            return
        if valor == "C":
            editor.limpar_entrada()
            return
        if valor == "⌫":
            editor.apagar_ultimo()
            return
        if valor == "↵":
            self.controlador.validar_item_ativo()
            return
        if valor == "+/-":
            editor.inserir_texto("-")
            return

        templates = {
            "x²": ("^2", 0),
            "x³": ("^3", 0),
            "1/x": ("1/()", -1),
            "|x|": ("abs()", -1),
            "√x": ("sqrt()", -1),
            "∛x": ("root(,3)", -3),
            "xʸ": ("^()", -1),
            "ʸ√x": ("root(,)", -2),
            "10ˣ": ("10^()", -1),
            "2ˣ": ("2^()", -1),
            "log": ("log()", -1),
            "logᵧx": ("log(,)", -2),
            "ln": ("ln()", -1),
            "eˣ": ("exp()", -1),
            "×": ("×", 0),
            "÷": ("÷", 0),
            "−": ("−", 0),
        }

        texto, deslocamento = templates.get(valor, (valor, 0))
        editor.inserir_texto(texto, deslocamento)

    def _atualizar_botao_segundo(self) -> None:
        if self.botao_segundo is None:
            return

        ativo = self.controlador.segundo_ativo
        self.botao_segundo.config(
            bg=Tema.COR_BOTAO_IGUAL if ativo else Tema.COR_BOTAO,
            fg=Tema.COR_GRAFICO_TEXTO_ESCURO if ativo else Tema.COR_TEXTO,
        )

        for rotulo_base, botao in self.botoes_segundo.items():
            botao.config(
                text=(
                    ROTULOS_SEGUNDO_TECLADO[rotulo_base]
                    if ativo
                    else rotulo_base
                )
            )

    def _abrir_menu(self, nome: str, coluna: int) -> None:
        self.fechar_menu()

        menu = tk.Frame(
            self,
            bg=Tema.COR_MENU,
            bd=1,
            relief="solid",
        )
        if nome == "Trigonometria":
            menu.place(relx=0, y=28, relwidth=1)
        else:
            menu.place(relx=coluna / 3, y=28, relwidth=1 / 3)
        menu.lift()
        self.menu_aberto = menu

        if nome == "Trigonometria":
            opcoes = self._opcoes_trigonometria()
            colunas_menu = 4
        elif nome == "Desigualdades":
            opcoes = (
                ("=", "="),
                ("<", "<"),
                (">", ">"),
                ("≤", "≤"),
                ("≥", "≥"),
                ("≠", "≠"),
            )
            colunas_menu = 3
        else:
            opcoes = (
                ("abs", "abs()"),
                ("sqrt", "sqrt()"),
                ("floor", "floor()"),
                ("ceil", "ceil()"),
                ("min", "min(,)"),
                ("max", "max(,)"),
                ("mod", "mod(,)"),
            )
            colunas_menu = 3

        for indice, (rotulo, inserir) in enumerate(opcoes):
            linha = indice // colunas_menu
            col = indice % colunas_menu
            ativo = (
                inserir == "__2nd__"
                and self.controlador.segundo_ativo
            ) or (
                inserir == "__hyp__"
                and self.controlador.hiperbolico_ativo
            )
            botao = tk.Button(
                menu,
                text=rotulo,
                bg=Tema.COR_BOTAO_IGUAL if ativo else Tema.COR_BOTAO,
                fg=Tema.COR_GRAFICO_TEXTO_ESCURO if ativo else Tema.COR_TEXTO,
                activebackground=Tema.COR_BOTAO_HOVER,
                activeforeground=Tema.COR_TEXTO,
                font=("Segoe UI", 9),
                relief="flat",
                bd=0,
                highlightthickness=0,
                command=lambda texto=inserir: self._inserir_menu(texto),
            )
            botao.grid(row=linha, column=col, sticky="nsew", padx=1, pady=1)

        for col in range(colunas_menu):
            menu.columnconfigure(col, weight=1)

        janela = self.winfo_toplevel()
        self.bind_clique_fora = janela.bind(
            "<Button-1>",
            self._fechar_menu_ao_clicar_fora,
            add="+",
        )
        self.bind_escape = janela.bind(
            "<Escape>",
            lambda _e: self.fechar_menu(),
            add="+",
        )

    def _opcoes_trigonometria(self) -> tuple[tuple[str, str], ...]:
        if self.controlador.hiperbolico_ativo and self.controlador.segundo_ativo:
            funcoes = (
                ("asinh", "asinh()"),
                ("acosh", "acosh()"),
                ("atanh", "atanh()"),
                ("asech", "asech()"),
                ("acsch", "acsch()"),
                ("acoth", "acoth()"),
            )
        elif self.controlador.hiperbolico_ativo:
            funcoes = (
                ("sinh", "sinh()"),
                ("cosh", "cosh()"),
                ("tanh", "tanh()"),
                ("sech", "sech()"),
                ("csch", "csch()"),
                ("coth", "coth()"),
            )
        elif self.controlador.segundo_ativo:
            funcoes = (
                ("sin⁻¹", "asin()"),
                ("cos⁻¹", "acos()"),
                ("tan⁻¹", "atan()"),
                ("sec⁻¹", "asec()"),
                ("csc⁻¹", "acsc()"),
                ("cot⁻¹", "acot()"),
            )
        else:
            funcoes = (
                ("sin", "sin()"),
                ("cos", "cos()"),
                ("tan", "tan()"),
                ("sec", "sec()"),
                ("csc", "csc()"),
                ("cot", "cot()"),
            )

        return (
            ("2nd", "__2nd__"),
            *funcoes[:3],
            ("hyp", "__hyp__"),
            *funcoes[3:],
        )

    def _inserir_menu(self, texto: str) -> None:
        if texto == "__2nd__":
            self.controlador.segundo_ativo = not self.controlador.segundo_ativo
            self._atualizar_botao_segundo()
            self.fechar_menu()
            self._abrir_menu("Trigonometria", 0)
            return

        if texto == "__hyp__":
            self.controlador.hiperbolico_ativo = not self.controlador.hiperbolico_ativo
            self.fechar_menu()
            self._abrir_menu("Trigonometria", 0)
            return

        deslocamento = -1 if texto.endswith("()") else 0
        if texto in {"min(,)", "max(,)", "mod(,)"}:
            deslocamento = -2

        self.controlador.editor.inserir_texto(texto, deslocamento)
        self.fechar_menu()

    def _fechar_menu_ao_clicar_fora(self, evento: tk.Event) -> None:
        if self.menu_aberto is None:
            return

        widget = evento.widget
        while widget is not None:
            if widget == self.menu_aberto:
                return
            widget = getattr(widget, "master", None)

        self.fechar_menu()

    def fechar_menu(self) -> None:
        janela = self.winfo_toplevel()
        if self.bind_clique_fora is not None:
            janela.unbind("<Button-1>", self.bind_clique_fora)
            self.bind_clique_fora = None

        if self.bind_escape is not None:
            janela.unbind("<Escape>", self.bind_escape)
            self.bind_escape = None

        if self.menu_aberto is not None and self.menu_aberto.winfo_exists():
            self.menu_aberto.destroy()
        self.menu_aberto = None
