from __future__ import annotations

import json
import platform
import webbrowser
from collections.abc import Callable
from pathlib import Path
import tkinter as tk

from recursos import caminho_configuracoes_usuario
from tema import Tema


PREFERENCIAS_TEMA = {"claro", "escuro", "sistema"}
URL_GITHUB = "https://github.com/Vinicius-Stenico/pycalc"
URL_FEEDBACK = "https://github.com/Vinicius-Stenico/pycalc/issues/new"


class ConfiguracoesApp:
    """Carrega, salva e resolve as preferências gerais da aplicação."""

    def __init__(self, caminho: Path | None = None) -> None:
        self.caminho = caminho or caminho_configuracoes_usuario()
        self.preferencia_tema = "sistema"
        self.carregar()

    def carregar(self) -> None:
        precisa_salvar = False

        try:
            with self.caminho.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            dados = {}
            precisa_salvar = True

        preferencia = dados.get("tema") if isinstance(dados, dict) else None
        if preferencia in PREFERENCIAS_TEMA:
            self.preferencia_tema = preferencia
        else:
            self.preferencia_tema = "sistema"
            precisa_salvar = True

        if precisa_salvar:
            self.salvar()

    def salvar(self) -> None:
        try:
            with self.caminho.open("w", encoding="utf-8") as arquivo:
                json.dump(
                    {"tema": self.preferencia_tema},
                    arquivo,
                    ensure_ascii=False,
                    indent=4,
                )
        except OSError:
            return

    def definir_tema(self, preferencia: str) -> None:
        if preferencia not in PREFERENCIAS_TEMA:
            return

        self.preferencia_tema = preferencia
        self.salvar()

    def tema_efetivo(self) -> str:
        if self.preferencia_tema == "sistema":
            return self.detectar_tema_sistema()

        return self.preferencia_tema

    def aplicar_preferencia(self) -> None:
        Tema.aplicar(self.tema_efetivo())

    @staticmethod
    def detectar_tema_sistema() -> str:
        if platform.system() != "Windows":
            return "escuro"

        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            ) as chave:
                valor, _tipo = winreg.QueryValueEx(chave, "AppsUseLightTheme")
        except OSError:
            return "escuro"

        return "claro" if int(valor) == 1 else "escuro"


class CartaoExpansivel(tk.Frame):
    """Cartão de configurações com cabeçalho clicável e conteúdo recolhível."""

    def __init__(
        self,
        parent: tk.Widget,
        titulo: str,
        descricao: str = "",
        expandido: bool = True,
    ) -> None:
        super().__init__(
            parent,
            bg=Tema.COR_MENU,
            highlightthickness=1,
            highlightbackground=Tema.COR_MENU_HOVER,
        )
        self.expandido = expandido
        self.titulo_texto = titulo
        self.descricao_texto = descricao

        self.columnconfigure(0, weight=1)
        self._criar_interface()
        self.aplicar_tema()
        self._atualizar_estado()

    def _criar_interface(self) -> None:
        self.cabecalho = tk.Frame(self, bg=Tema.COR_MENU, cursor="hand2")
        self.cabecalho.grid(row=0, column=0, sticky="ew")
        self.cabecalho.columnconfigure(0, weight=1)

        bloco_texto = tk.Frame(self.cabecalho, bg=Tema.COR_MENU)
        bloco_texto.grid(row=0, column=0, sticky="ew", padx=16, pady=14)
        bloco_texto.columnconfigure(0, weight=1)

        self.label_titulo = tk.Label(
            bloco_texto,
            text=self.titulo_texto,
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 10),
            anchor="w",
        )
        self.label_titulo.grid(row=0, column=0, sticky="ew")

        self.label_descricao = tk.Label(
            bloco_texto,
            text=self.descricao_texto,
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
        )
        self.label_descricao.grid(row=1, column=0, sticky="ew", pady=(2, 0))

        self.label_seta = tk.Label(
            self.cabecalho,
            text="⌃",
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI Symbol", 12),
            cursor="hand2",
        )
        self.label_seta.grid(row=0, column=1, padx=(4, 16), sticky="e")

        self.divisoria = tk.Frame(self, bg=Tema.COR_MENU_HOVER, height=1)
        self.divisoria.grid(row=1, column=0, sticky="ew")

        self.conteudo = tk.Frame(self, bg=Tema.COR_MENU)
        self.conteudo.grid(row=2, column=0, sticky="ew")
        self.conteudo.columnconfigure(0, weight=1)

        for widget in (
            self.cabecalho,
            bloco_texto,
            self.label_titulo,
            self.label_descricao,
            self.label_seta,
        ):
            widget.bind("<Button-1>", lambda _evento: self.alternar())

    def alternar(self) -> None:
        self.expandido = not self.expandido
        self._atualizar_estado()

    def _atualizar_estado(self) -> None:
        self.label_seta.config(text="⌃" if self.expandido else "⌄")

        if self.expandido:
            self.divisoria.grid()
            self.conteudo.grid()
        else:
            self.divisoria.grid_remove()
            self.conteudo.grid_remove()

    def aplicar_tema(self) -> None:
        self.config(bg=Tema.COR_MENU, highlightbackground=Tema.COR_MENU_HOVER)
        self.cabecalho.config(bg=Tema.COR_MENU)
        self.conteudo.config(bg=Tema.COR_MENU)
        self.divisoria.config(bg=Tema.COR_MENU_HOVER)

        for widget in self.cabecalho.winfo_children():
            widget.config(bg=Tema.COR_MENU)
            for filho in getattr(widget, "winfo_children", lambda: [])():
                filho.config(bg=Tema.COR_MENU)

        self.label_titulo.config(bg=Tema.COR_MENU, fg=Tema.COR_TEXTO)
        self.label_descricao.config(
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO_SECUNDARIO,
        )
        self.label_seta.config(bg=Tema.COR_MENU, fg=Tema.COR_TEXTO)


class TelaConfiguracoes(tk.Frame):
    """Tela de configurações inspirada na Calculadora do Windows."""

    def __init__(
        self,
        parent: tk.Widget,
        preferencia_tema: str,
        ao_alterar_tema: Callable[[str], None],
        ao_voltar: Callable[[], None],
    ) -> None:
        super().__init__(parent, bg=Tema.COR_FUNDO)
        self.ao_alterar_tema = ao_alterar_tema
        self.ao_voltar = ao_voltar
        self.tema_var = tk.StringVar(value=preferencia_tema)
        self.cartoes: list[CartaoExpansivel] = []
        self.radios_tema: dict[str, tk.Canvas] = {}
        self.links: list[tk.Label] = []
        self.labels_quebraveis: list[tk.Label] = []
        self.rolagem_ativa = False

        self._configurar_layout()
        self._criar_interface()
        self.atualizar_tema()

    def _configurar_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def _criar_interface(self) -> None:
        self.canvas = tk.Canvas(
            self,
            bg=Tema.COR_FUNDO,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.barra_rolagem = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.canvas.configure(yscrollcommand=self._ao_rolar_canvas)

        self.conteudo = tk.Frame(self.canvas, bg=Tema.COR_FUNDO)
        self.janela_conteudo = self.canvas.create_window(
            (0, 0),
            window=self.conteudo,
            anchor="nw",
        )
        self.conteudo.columnconfigure(0, weight=1)

        self.canvas.bind("<Configure>", self._redimensionar_conteudo)
        self.conteudo.bind("<Configure>", lambda _e: self._atualizar_scrollregion())
        self._criar_conteudo()
        self._vincular_rolagem_widgets(self)

    def _criar_conteudo(self) -> None:
        self.titulo = tk.Label(
            self.conteudo,
            text="Configurações",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 17, "bold"),
            anchor="w",
        )
        self.titulo.grid(row=0, column=0, sticky="ew", padx=24, pady=(18, 24))

        self._criar_secao_aparencia(1)
        self._criar_secao_sobre(3)

    def _criar_secao_aparencia(self, linha: int) -> None:
        self._criar_titulo_secao("Aparência", linha)

        cartao = CartaoExpansivel(
            self.conteudo,
            "Tema do aplicativo",
            "Selecionar o tema do aplicativo a ser exibido",
            expandido=True,
        )
        cartao.grid(row=linha + 1, column=0, sticky="ew", padx=24, pady=(8, 30))
        self.cartoes.append(cartao)

        for valor, texto in (
            ("claro", "Claro"),
            ("escuro", "Escuro"),
            ("sistema", "Usar configuração do sistema"),
        ):
            self._criar_linha_tema(cartao.conteudo, valor, texto)

    def _criar_secao_sobre(self, linha: int) -> None:
        self._criar_titulo_secao("Sobre", linha)

        descricao = (
            "© 2026 PyCalc. Todos os direitos reservados.\n"
            f"Versão: {Tema.VERSAO_APLICACAO}"
        )
        cartao = CartaoExpansivel(
            self.conteudo,
            "Calculadora",
            descricao,
            expandido=False,
        )
        cartao.grid(row=linha + 1, column=0, sticky="ew", padx=24, pady=(8, 24))
        self.cartoes.append(cartao)

        self._criar_texto_sobre(cartao.conteudo)

    def _criar_titulo_secao(self, texto: str, linha: int) -> None:
        label = tk.Label(
            self.conteudo,
            text=texto,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        label.grid(row=linha, column=0, sticky="ew", padx=24, pady=(0, 0))

    def _criar_linha_tema(
        self,
        parent: tk.Widget,
        valor: str,
        texto: str,
    ) -> None:
        linha = tk.Frame(parent, bg=Tema.COR_MENU, cursor="hand2")
        linha.grid(sticky="ew", padx=0, pady=0)
        linha.columnconfigure(1, weight=1)

        canvas_radio = tk.Canvas(
            linha,
            width=26,
            height=26,
            bg=Tema.COR_MENU,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        canvas_radio.grid(row=0, column=0, padx=(56, 12), pady=12)
        self.radios_tema[valor] = canvas_radio

        label = tk.Label(
            linha,
            text=texto,
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
            cursor="hand2",
        )
        label.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=12)
        self.labels_quebraveis.append(label)

        for widget in (linha, canvas_radio, label):
            widget.bind("<Button-1>", lambda _e, v=valor: self._selecionar_tema(v))

    def _criar_texto_sobre(self, parent: tk.Widget) -> None:
        textos = (
            "PyCalc é uma calculadora desktop desenvolvida em Python e Tkinter, "
            "inspirada visualmente e funcionalmente na Calculadora do Windows.",
            "Desenvolvedor:\nVinícius Stenico",
            "Projeto:\nPyCalc",
            "Tecnologias:\nPython e Tkinter",
        )

        for texto in textos:
            label = tk.Label(
                parent,
                text=texto,
                bg=Tema.COR_MENU,
                fg=Tema.COR_TEXTO,
                font=("Segoe UI", 9),
                anchor="w",
                justify="left",
            )
            label.grid(sticky="ew", padx=16, pady=(10, 0))
            self.labels_quebraveis.append(label)

        link_feedback = self._criar_link(parent, "Enviar feedback", URL_FEEDBACK)
        link_feedback.grid(sticky="w", padx=16, pady=(22, 8))

        frame_github = tk.Frame(parent, bg=Tema.COR_MENU)
        frame_github.grid(sticky="ew", padx=16, pady=(10, 18))
        frame_github.columnconfigure(0, weight=1)

        texto_inicio = tk.Label(
            frame_github,
            text=(
                "Para saber como você pode contribuir com a PyCalc, "
                "consulte o projeto no "
            ),
            bg=Tema.COR_MENU,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 9),
            anchor="w",
            justify="left",
        )
        texto_inicio.grid(row=0, column=0, sticky="ew")
        self.labels_quebraveis.append(texto_inicio)

        link_github = self._criar_link(frame_github, "GitHub.", URL_GITHUB)
        link_github.grid(row=1, column=0, sticky="w", pady=(0, 0))

    def _criar_link(self, parent: tk.Widget, texto: str, url: str) -> tk.Label:
        link = tk.Label(
            parent,
            text=texto,
            bg=Tema.COR_MENU,
            fg=Tema.COR_BOTAO_IGUAL,
            font=("Segoe UI", 9),
            cursor="hand2",
        )
        link.bind("<Button-1>", lambda _e: webbrowser.open(url))
        link.bind(
            "<Enter>",
            lambda _e, l=link: l.config(fg=Tema.COR_BOTAO_IGUAL_HOVER),
        )
        link.bind(
            "<Leave>",
            lambda _e, l=link: l.config(fg=Tema.COR_BOTAO_IGUAL),
        )
        self.links.append(link)
        return link

    def _selecionar_tema(self, valor: str) -> None:
        if valor not in PREFERENCIAS_TEMA:
            return

        self.tema_var.set(valor)
        self._atualizar_radios()
        self.ao_alterar_tema(valor)

    def atualizar_preferencia(self, valor: str) -> None:
        if valor in PREFERENCIAS_TEMA:
            self.tema_var.set(valor)
            self._atualizar_radios()

    def atualizar_tema(self) -> None:
        self.config(bg=Tema.COR_FUNDO)
        self.canvas.config(bg=Tema.COR_FUNDO)
        self.conteudo.config(bg=Tema.COR_FUNDO)
        self.titulo.config(bg=Tema.COR_FUNDO, fg=Tema.COR_TEXTO)

        for widget in self.conteudo.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=Tema.COR_FUNDO, fg=Tema.COR_TEXTO)

        for cartao in self.cartoes:
            cartao.aplicar_tema()
            self._atualizar_filhos_cartao(cartao.conteudo)

        for link in self.links:
            link.config(bg=Tema.COR_MENU, fg=Tema.COR_BOTAO_IGUAL)

        self._atualizar_radios()
        self._atualizar_wraplengths()

    def _atualizar_filhos_cartao(self, parent: tk.Widget) -> None:
        for widget in parent.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.config(bg=Tema.COR_MENU)
                self._atualizar_filhos_cartao(widget)
            elif isinstance(widget, tk.Canvas):
                widget.config(bg=Tema.COR_MENU)
            elif isinstance(widget, tk.Label):
                cor = Tema.COR_BOTAO_IGUAL if widget in self.links else Tema.COR_TEXTO
                widget.config(bg=Tema.COR_MENU, fg=cor)

    def _atualizar_radios(self) -> None:
        selecionado = self.tema_var.get()

        for valor, canvas in self.radios_tema.items():
            canvas.delete("all")
            canvas.create_oval(
                4,
                4,
                22,
                22,
                outline=(
                    Tema.COR_BOTAO_IGUAL
                    if valor == selecionado
                    else Tema.COR_TEXTO_SECUNDARIO
                ),
                width=3 if valor == selecionado else 1,
            )
            if valor == selecionado:
                canvas.create_oval(
                    10,
                    10,
                    16,
                    16,
                    fill=Tema.COR_BOTAO_IGUAL,
                    outline="",
                )

    def _redimensionar_conteudo(self, evento: tk.Event) -> None:
        self.canvas.itemconfigure(self.janela_conteudo, width=evento.width)
        self._atualizar_wraplengths()
        self._atualizar_scrollregion()

    def _atualizar_wraplengths(self) -> None:
        largura = max(180, self.canvas.winfo_width() - 96)
        for label in self.labels_quebraveis:
            label.config(wraplength=largura)

    def _atualizar_scrollregion(self) -> None:
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._ao_rolar_canvas(*self.canvas.yview())

    def _ao_rolar_canvas(self, primeiro: str, ultimo: str) -> None:
        self.barra_rolagem.set(primeiro, ultimo)
        if float(primeiro) <= 0.0 and float(ultimo) >= 1.0:
            self.barra_rolagem.grid_remove()
        else:
            self.barra_rolagem.grid(row=0, column=1, sticky="ns")

    def _ativar_rolagem_mouse(self) -> None:
        if self.rolagem_ativa:
            return

        self.rolagem_ativa = True
        self.bind_all("<MouseWheel>", self._rolar_mouse, add="+")

    def _desativar_rolagem_mouse(self) -> None:
        if not self.rolagem_ativa:
            return

        self.rolagem_ativa = False
        self.unbind_all("<MouseWheel>")

    def _desativar_rolagem_se_fora(self) -> None:
        if not self._cursor_esta_sobre_tela():
            self._desativar_rolagem_mouse()

    def _vincular_rolagem_widgets(self, widget: tk.Widget) -> None:
        widget.bind(
            "<Enter>",
            lambda _e: self._ativar_rolagem_mouse(),
            add="+",
        )
        widget.bind(
            "<Leave>",
            lambda _e: self.after(50, self._desativar_rolagem_se_fora),
            add="+",
        )

        for filho in widget.winfo_children():
            self._vincular_rolagem_widgets(filho)

    def _rolar_mouse(self, evento: tk.Event) -> str:
        unidades = -1 if evento.delta > 0 else 1
        self.canvas.yview_scroll(unidades * 3, "units")
        return "break"

    def ao_exibir(self) -> None:
        self._atualizar_scrollregion()
        if self._cursor_esta_sobre_tela():
            self._ativar_rolagem_mouse()

    def fechar_paineis(self) -> None:
        self._desativar_rolagem_mouse()

    def processar_tecla(self, evento: tk.Event) -> str | None:
        if evento.keysym == "Escape":
            self.ao_voltar()
            return "break"

        return None

    def _cursor_esta_sobre_tela(self) -> bool:
        x = self.winfo_pointerx()
        y = self.winfo_pointery()
        esquerda = self.winfo_rootx()
        topo = self.winfo_rooty()
        direita = esquerda + self.winfo_width()
        baixo = topo + self.winfo_height()

        return esquerda <= x <= direita and topo <= y <= baixo
