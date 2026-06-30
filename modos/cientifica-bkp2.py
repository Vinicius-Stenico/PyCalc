import tkinter as tk

from tema import Tema
from gerenciador_memoria import GerenciadorMemoria
from operacoes import (
    dividir,
    fracao,
    multiplicar,
    potencia,
    porcentagem,
    raiz,
    somar,
    subtrair,
)

OPERADORES_COMUNS = {"+", "-", "×", "÷"}
OPERACOES_ESPECIAIS = {"x²", "√x", "%", "1/x"}

GRADE_BOTOES_CIENTIFICA = (
    ("2ⁿᵈ", "π", "e", "C", "⌫"),
    ("x²", "1/x", "|x|", "exp", "mod"),
    ("²√x", "(", ")", "n!", "÷"),
    ("xʸ", "7", "8", "9", "×"),
    ("10ˣ", "4", "5", "6", "−"),
    ("log", "1", "2", "3", "+"),
    ("ln", "+/−", "0", ",", "="),
)

BOTOES_PERMITIDOS_EM_ERRO = {
    "1", "2", "3", "4", "5",
    "6", "7", "8", "9",
    "CE", "C", "⌫", "=",
}

BOTOES_MEMORIA = ("MC", "MR", "M+", "M−", "MS", "M⌄")


class CalculadoraCientifica(tk.Frame):
    """
    Interface do modo Científica.

    Este arquivo contém apenas a estrutura visual do modo:
    - visor;
    - controles DEG e F-E;
    - botões de memória;
    - menus Trigonometria e Função;
    - teclado científico.

    A janela principal, o cabeçalho e o menu lateral continuam sendo
    controlados por calculadora.py.
    """

    NOME_MODO = "Científica"

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=Tema.COR_FUNDO)
        self.pack(fill="both", expand=True)

        self.botoes: dict[str, tk.Button] = {}
        self.frame_menu_trigonometria: tk.Frame | None = None
        self.frame_menu_funcoes: tk.Frame | None = None

        self._inicializar_estado()
        self._configurar_layout()
        self._criar_interface()
        self._construir_interface()

    # ==========================================================
    # INICIALIZAÇÃO E ESTADO
    # ==========================================================

    def _inicializar_estado(self) -> None:
        self.texto_visor = tk.StringVar(value="0")
        self.texto_expressao = tk.StringVar(value="")

        self.numero_atual = 0.0
        self.operador_atual: str | None = None

        self.substituir_visor = False
        self.resultado_indefinido = False

        self.botoes_principais: dict[str, tk.Button] = {}

    def _configurar_aparencia(self) -> None:
        self.master.configure(bg=Tema.COR_FUNDO)
        self.configure(bg=Tema.COR_FUNDO)

    def _construir_interface(self) -> None:
        self._configurar_layout()
        self._criar_visor()

        self.memoria = GerenciadorMemoria(
            parent=self,
            obter_texto_visor=self.texto_visor.get,
            ao_recuperar_valor=self._recuperar_valor_memoria,
            ao_clicar_botao=self.ao_clicar,
            ao_marcar_substituicao=self._marcar_substituicao,
        )
        self.memoria.criar_botoes(linha=2)

        self._criar_botoes_principais()

    # ==========================================================
    # CONSTRUÇÃO DA INTERFACE PRINCIPAL
    # ==========================================================

    def _configurar_layout(self) -> None:
        """Configura as áreas verticais do modo Científica."""
        self.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=2)  # Visor
        self.rowconfigure(1, weight=0)  # DEG e F-E
        self.rowconfigure(2, weight=0)  # Memória
        self.rowconfigure(3, weight=0)  # Trigonometria e Função
        self.rowconfigure(4, weight=7)  # Teclado

    def _criar_interface(self) -> None:
        """Cria todos os frames do modo Científica."""
        self._criar_frame_visor()
        self._criar_frame_modos_exibicao()
        self._criar_frame_memoria()
        self._criar_frame_funcoes()
        self._criar_frame_teclado()

    # ==========================================================
    # VISOR
    # ==========================================================

    def _criar_frame_visor(self) -> None:
        """Cria o frame da expressão e do valor principal."""
        frame_visor = tk.Frame(
            self,
            bg=Tema.COR_VISOR,
        )
        frame_visor.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=8,
            pady=(2, 0),
        )

        frame_visor.columnconfigure(0, weight=1)
        frame_visor.rowconfigure(0, weight=1)
        frame_visor.rowconfigure(1, weight=2)

        label_expressao = tk.Label(
            frame_visor,
            textvariable=self.texto_expressao,
            bg=Tema.COR_VISOR,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=Tema.FONTE_EXPRESSAO,
            anchor="e",
            padx=8,
        )
        label_expressao.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.label_visor = tk.Label(
            frame_visor,
            textvariable=self.texto_visor,
            bg=Tema.COR_VISOR,
            fg=Tema.COR_TEXTO,
            font=Tema.FONTE_VISOR,
            anchor="e",
            justify="right",
            padx=8,
        )
        self.label_visor.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

    # ==========================================================
    # DEG E F-E
    # ==========================================================

    def _criar_frame_modos_exibicao(self) -> None:
        """Cria os controles de ângulo e notação científica."""
        frame_modos = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        frame_modos.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 2),
        )

        botao_deg = self._criar_botao_texto(
            parent=frame_modos,
            texto="DEG",
            comando=lambda: self.ao_clicar("DEG"),
        )
        botao_deg.pack(
            side="left",
            padx=(2, 14),
            pady=2,
        )

        botao_fe = self._criar_botao_texto(
            parent=frame_modos,
            texto="F-E",
            comando=lambda: self.ao_clicar("F-E"),
        )
        botao_fe.pack(
            side="left",
            padx=4,
            pady=2,
        )

    # ==========================================================
    # MEMÓRIA
    # ==========================================================

    def _criar_frame_memoria(self) -> None:
        """Cria a linha MC, MR, M+, M−, MS e M⌄."""
        frame_memoria = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        frame_memoria.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=8,
            pady=(0, 2),
        )

        for coluna in range(len(BOTOES_MEMORIA)):
            frame_memoria.columnconfigure(coluna, weight=1)

        for coluna, texto in enumerate(BOTOES_MEMORIA):
            desativado = texto in {"MC", "MR"}

            botao = tk.Button(
                frame_memoria,
                text=texto,
                bg=Tema.COR_FUNDO,
                fg=(
                    Tema.COR_TEXTO_DESATIVADO
                    if desativado
                    else Tema.COR_TEXTO
                ),
                activebackground=Tema.COR_BOTAO_HOVER,
                activeforeground=Tema.COR_TEXTO,
                disabledforeground=Tema.COR_TEXTO_DESATIVADO,
                font=Tema.FONTE_BOTAO_MEMORIA,
                relief="flat",
                bd=0,
                highlightthickness=0,
                cursor="arrow" if desativado else "hand2",
                state="disabled" if desativado else "normal",
                command=lambda valor=texto: self.ao_clicar(valor),
            )
            botao.grid(
                row=0,
                column=coluna,
                sticky="nsew",
                padx=1,
                pady=1,
                ipady=5,
            )

            self.botoes[texto] = botao

    # ==========================================================
    # TRIGONOMETRIA E FUNÇÃO
    # ==========================================================

    def _criar_frame_funcoes(self) -> None:
        """Cria os dois seletores acima do teclado."""
        frame_funcoes = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        frame_funcoes.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=8,
            pady=(0, 4),
        )

        frame_funcoes.columnconfigure(0, weight=1)
        frame_funcoes.columnconfigure(1, weight=1)

        botao_trigonometria = tk.Button(
            frame_funcoes,
            text="△  Trigonometria  ⌄",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="w",
            padx=8,
            cursor="hand2",
            command=self._alternar_menu_trigonometria,
        )
        botao_trigonometria.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 2),
            ipady=6,
        )

        botao_funcoes = tk.Button(
            frame_funcoes,
            text="ƒ  Função  ⌄",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="w",
            padx=8,
            cursor="hand2",
            command=self._alternar_menu_funcoes,
        )
        botao_funcoes.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(2, 0),
            ipady=6,
        )

    # ==========================================================
    # TECLADO
    # ==========================================================

    def _criar_frame_teclado(self) -> None:
        """Cria a grade de botões da calculadora científica."""
        frame_teclado = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        frame_teclado.grid(
            row=4,
            column=0,
            sticky="nsew",
            padx=7,
            pady=(0, 6),
        )

        for coluna in range(5):
            frame_teclado.columnconfigure(coluna, weight=1)

        for linha in range(len(GRADE_BOTOES_CIENTIFICA)):
            frame_teclado.rowconfigure(linha, weight=1)

        for linha, valores in enumerate(GRADE_BOTOES_CIENTIFICA):
            for coluna, texto in enumerate(valores):
                botao = self._criar_botao_teclado(
                    parent=frame_teclado,
                    texto=texto,
                )
                botao.grid(
                    row=linha,
                    column=coluna,
                    sticky="nsew",
                    padx=2,
                    pady=2,
                    ipady=5,
                )

                self.botoes[texto] = botao

    def _criar_botao_teclado(
        self,
        parent: tk.Widget,
        texto: str,
    ) -> tk.Button:
        """Cria um botão do teclado com o estilo adequado."""
        if texto == "=":
            cor_fundo = Tema.COR_BOTAO_IGUAL
            cor_hover = Tema.COR_BOTAO_IGUAL_HOVER
            cor_texto = "#000000"
        else:
            cor_fundo = Tema.COR_BOTAO
            cor_hover = Tema.COR_BOTAO_HOVER
            cor_texto = Tema.COR_TEXTO

        return tk.Button(
            parent,
            text=texto,
            bg=cor_fundo,
            fg=cor_texto,
            activebackground=cor_hover,
            activeforeground=cor_texto,
            font=("Segoe UI", 13),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=lambda valor=texto: self.ao_clicar(valor),
        )

    @staticmethod
    def _criar_botao_texto(
        parent: tk.Widget,
        texto: str,
        comando,
    ) -> tk.Button:
        """Cria um botão textual sem fundo destacado."""
        return tk.Button(
            parent,
            text=texto,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=comando,
        )

    # ==========================================================
    # MENUS TEMPORÁRIOS
    # ==========================================================

    def _alternar_menu_trigonometria(self) -> None:
        """Abre ou fecha o painel de funções trigonométricas."""
        if self._painel_existe(self.frame_menu_trigonometria):
            self.frame_menu_trigonometria.destroy()
            self.frame_menu_trigonometria = None
            return

        self._fechar_menu_funcoes()

        self.frame_menu_trigonometria = self._criar_painel_flutuante(
            opcoes=("sin", "cos", "tan", "sec", "csc", "cot"),
            coluna_inicial=0,
        )

    def _alternar_menu_funcoes(self) -> None:
        """Abre ou fecha o painel de funções adicionais."""
        if self._painel_existe(self.frame_menu_funcoes):
            self.frame_menu_funcoes.destroy()
            self.frame_menu_funcoes = None
            return

        self._fechar_menu_trigonometria()

        self.frame_menu_funcoes = self._criar_painel_flutuante(
            opcoes=("abs", "floor", "ceil", "rand"),
            coluna_inicial=1,
        )

    def _criar_painel_flutuante(
        self,
        opcoes: tuple[str, ...],
        coluna_inicial: int,
    ) -> tk.Frame:
        """
        Cria um painel simples sobre o teclado.

        A lógica matemática das opções pode ser adicionada posteriormente.
        """
        painel = tk.Frame(
            self,
            bg=Tema.COR_MENU,
            bd=1,
            relief="solid",
        )

        largura_relativa = 0.5
        posicao_x = 0.0 if coluna_inicial == 0 else 0.5

        painel.place(
            relx=posicao_x,
            rely=0.31,
            relwidth=largura_relativa,
        )
        painel.lift()

        for opcao in opcoes:
            botao = tk.Button(
                painel,
                text=opcao,
                bg=Tema.COR_MENU,
                fg=Tema.COR_TEXTO,
                activebackground=Tema.COR_MENU_HOVER,
                activeforeground=Tema.COR_TEXTO,
                font=("Segoe UI", 10),
                relief="flat",
                bd=0,
                anchor="w",
                padx=12,
                cursor="hand2",
                command=lambda valor=opcao: self._selecionar_funcao(valor),
            )
            botao.pack(
                fill="x",
                padx=2,
                pady=1,
                ipady=5,
            )

        return painel

    def _selecionar_funcao(self, funcao: str) -> None:
        """Recebe a opção de um menu temporário."""
        self.ao_clicar(funcao)
        self._fechar_menus_funcoes()

    def _fechar_menu_trigonometria(self) -> None:
        if self._painel_existe(self.frame_menu_trigonometria):
            self.frame_menu_trigonometria.destroy()

        self.frame_menu_trigonometria = None

    def _fechar_menu_funcoes(self) -> None:
        if self._painel_existe(self.frame_menu_funcoes):
            self.frame_menu_funcoes.destroy()

        self.frame_menu_funcoes = None

    def _fechar_menus_funcoes(self) -> None:
        self._fechar_menu_trigonometria()
        self._fechar_menu_funcoes()

    @staticmethod
    def _painel_existe(painel: tk.Frame | None) -> bool:
        return painel is not None and bool(painel.winfo_exists())

    # ==========================================================
    # EVENTOS E ROTEAMENTO
    # ==========================================================

    def ao_clicar(self, valor: str) -> None:
        """Encaminha o clique para o grupo de ação correspondente."""
        texto_atual = self.texto_visor.get()
        expressao = self.texto_expressao.get().strip()

        if self._tratar_estado_erro_divisao(valor):
            return
        
        if valor != "M⌄":
            self.memoria.fechar_painel()

        if self.memoria.tratar_comando(valor):
            return
        
        if valor in OPERADORES_COMUNS:
            self._tratar_operador_comum(valor, texto_atual, expressao)
            return
        
        if valor in OPERACOES_ESPECIAIS:
            self._tratar_operacao_especial(valor, texto_atual)
            return
        
        if self._tratar_comando_edicao(valor, texto_atual):
            return
        
        if valor == "=":
            self._tratar_igual(expressao)
            return
        
        if valor.isdigit():
            self._tratar_numero(valor)
            return
        
        if valor == ".":
            self._tratar_ponto_decimal()

    # ==========================================================
    # OPERADORES E NÚMEROS
    # ==========================================================

    def _tratar_operador_comum(
            self,
            operador_novo: str,
            texto_atual: str,
            expressao: str,
    ) -> None:
        if expressao:
            partes = expressao.split()

            if len(partes) >= 2:
                numero_anterior = partes[0]
                operador_anterior = partes[1]

                if self.substituir_visor:
                    self.operador_atual = operador_novo
                    self.texto_expressao.set(
                        f"{numero_anterior} {operador_novo}"
                    )
                    print(
                        "Operador alterado:",
                        operador_anterior,
                        "para",
                        operador_novo
                    )
                    return
            
            resultado = self.calcular_resultado()
            if resultado is None:
                return
            
            resultado_formatado = self.formatar_numero(resultado)
            self.numero_atual = float(resultado)
            self.operador_atual = operador_novo
            self.texto_expressao.set(
                f"{resultado_formatado} {operador_novo}"
            )
            self.texto_visor.set(resultado_formatado)
            self.substituir_visor = True
            return
        
        if texto_atual:
            self.numero_atual = float(texto_atual)
            self.operador_atual = operador_novo
            self.texto_expressao.set(f"{texto_atual} {operador_novo}")
            self.texto_visor.set(texto_atual)
            self.substituir_visor = True

    def _tratar_numero(self, valor: str) -> None:
        texto_atual = self.texto_visor.get()
        
        if (
            texto_atual == "0"
            or self.substituir_visor
            or texto_atual == "Erro"
        ):
            self.texto_visor.set(valor)
            self.substituir_visor = False
        else:
            self.texto_visor.set(texto_atual + valor)

        self.numero_atual = float(self.texto_visor.get())

    def _tratar_ponto_decimal(self) -> None:
        texto_atual = self.texto_visor.get()

        if self.substituir_visor or texto_atual == "Erro":
            self.texto_visor.set("0.")
            self.substituir_visor = False
        elif "." not in texto_atual:
            self.texto_visor.set(texto_atual + ".")
    
    def _tratar_igual(self, expressao: str) -> None:
        if expressao and not self.substituir_visor:
            self.calcular_resultado()

    # ==========================================================
    # OPERAÇÕES ESPECIAIS
    # ==========================================================

    def _tratar_operacao_especial(
            self,
            valor: str,
            texto_atual: str,
    ) -> None:
        if valor == "x²":
            self._calcular_quadrado(texto_atual)
        elif valor == "√x":
            self._calcular_raiz(texto_atual)
        elif valor == "1/x":
            self._calcular_fracao(texto_atual)
        elif valor == "%":
            self._calcular_porcentagem()

    def _calcular_quadrado(self, texto_atual: str) -> None:
        try:
            numero = float(texto_atual)
            resultado = potencia(numero)

            self.texto_expressao.set(
                f"sqr({self.formatar_numero(numero)})"
            )
            self._mostrar_resultado(resultado)
        except (ValueError, TypeError):
            self._mostrar_erro()

    def _calcular_raiz(self, texto_atual: str) -> None:
        try:
            numero = float(texto_atual)

            if numero < 0:
                self._mostrar_erro()
                return
            
            resultado = raiz(numero)
            self.texto_expressao.set(f"√{self.formatar_numero(numero)}")
            self._mostrar_resultado(resultado)
        except (ValueError, TypeError):
            self._mostrar_erro()
    
    def _calcular_fracao(self, texto_atual: str) -> None:
        try:
            numero = float(texto_atual)

            if numero == 0:
                self._mostrar_erro()
                return
            
            resultado = fracao(numero)
            self.texto_expressao.set(f"1/{self.formatar_numero(numero)}")
            self._mostrar_resultado(resultado)
        except (ValueError, TypeError, ZeroDivisionError):
            self._mostrar_erro()
    
    def _calcular_porcentagem(self) -> None:
        try:
            partes = self.texto_expressao.get().strip().split()
            if len(partes) < 2:
                return
            
            primeiro_numero = float(partes[0])
            operador = partes[1]
            segundo_numero = float(self.texto_visor.get())
            resultado = porcentagem(primeiro_numero, segundo_numero)

            self.texto_expressao.set(
                f"{self.formatar_numero(primeiro_numero)} "
                f"{operador} "
                f"{self.formatar_numero(segundo_numero)}"
            )
            self._mostrar_resultado(resultado)
        except (ValueError, TypeError):
            self._mostrar_erro()

    # ==========================================================
    # COMANDOS DE EDIÇÃO
    # ==========================================================

    def _tratar_comando_edicao(
            self,
            valor: str,
            texto_atual: str,
    ) -> bool:
        if valor == "⌫":
            self._apagar_ultimo_digito(texto_atual)
            return True
        
        if valor == "C":
            self._limpar_tudo()
            return True
        
        if valor == "CE":
            self._limpar_entrada()
            return True
        
        if valor == "+/-":
            self._trocar_sinal(texto_atual)
            return True
        
        return False
    
    def _apagar_ultimo_digito(self, texto_atual: str) -> None:
        if self.substituir_visor:
            return
        
        novo_texto = "0" if len(texto_atual) <= 1 else texto_atual[:-1]
        self.texto_visor.set(novo_texto)
        self.numero_atual = float(novo_texto)

    def _limpar_tudo(self) -> None:
        self.texto_visor.set("0")
        self.texto_expressao.set("")
        self.numero_atual = 0.0
        self.operador_atual = None
        self.substituir_visor = False
        print("Conta reiniciada")
    
    def _limpar_entrada(self) -> None:
        self.texto_visor.set("0")
        self.numero_atual = 0.0
        self.substituir_visor = False
        print("Entrada do visor limpa")
    
    def _trocar_sinal(self, texto_atual: str) -> None:
        try:
            numero = -float(texto_atual)
            self.numero_atual = numero
            self.texto_visor.set(self.formatar_numero(numero))
        except ValueError:
            self._mostrar_erro()

    # ==========================================================
    # CÁLCULOS BINÁRIOS
    # ==========================================================

    def calcular_resultado(self) -> float | None:
        try:
            partes = self.texto_expressao.get().strip().split()
            if len(partes) < 2:
                return None
            
            primeiro_numero = float(partes[0])
            operador = partes[1]
            segundo_numero = float(self.texto_visor.get())

            if operador == "+":
                resultado = somar(primeiro_numero, segundo_numero)
            elif operador == "-":
                resultado = subtrair(primeiro_numero, segundo_numero)
            elif operador == "×":
                resultado = multiplicar(primeiro_numero, segundo_numero)
            elif operador == "÷":
                resultado = self.calcular_divisao(
                    primeiro_numero,
                    segundo_numero,
                )
                if resultado is None:
                    return None
            else:
                return None
            
            self._mostrar_resultado(resultado, limpar_expressao=True)
            self.operador_atual = None
            return float(resultado)
        
        except (ValueError, TypeError, IndexError, ZeroDivisionError):
            self._mostrar_erro()
            return None
    
    def _calcular_divisao(
            self,
            primeiro_numero: float,
            segundo_numero: float,
    ) -> float | None:
        if primeiro_numero == 0 and segundo_numero == 0:
            self._mostrar_erro_divisao(
                mensagem="Resultado indefinido",
                expressao="0 ÷",
            )
            return None
        
        if segundo_numero == 0:
            self._mostrar_erro_divisao(
                mensagem="Resultado indefinido",
                expressao="0 ÷",
            )
            return None
        
        return dividir(primeiro_numero, segundo_numero)
    
    def _mostrar_resultado(
            self,
            resultado: float,
            limpar_expressao: bool = False,
    ) -> None:
        self.numero_atual = float(resultado)
        self.texto_visor.set(self.formatar_numero(resultado))

        if limpar_expressao:
            self.texto_expressao.set("")

        self.substituir_visor = True

    # ==========================================================
    # INTEGRAÇÃO COM OS COMPONENTES
    # ==========================================================

    def _recuperar_valor_memoria(self, numero: float) -> None:
        self.numero_atual = float(numero)
        self.texto_visor.set(self.formatar_numero(numero))
        self.substituir_visor = True

    def _marcar_substituicao(self) -> None:
        self.substituir_visor = True

    def fechar_paineis(self) -> None:
        """Fecha menus temporários antes da troca de modo."""
        self._fechar_menus_funcoes()
    
    # ==========================================================
    # ESTADOS DE ERRO
    # ==========================================================

    def _tratar_estado_erro_divisao(self, valor: str) -> bool:
        if not self.resultado_indefinido:
            return False
        
        if valor in {"1", "2", "3", "4", "5", "6", "7", "8", "9"}:
            self._limpar_resultado_indefinido(valor)
            return True
        
        return True
    
    def _mostrar_erro_divisao(
            self,
            mensagem: str,
            expressao: str,
    ) -> None:
        self.texto_visor.set(mensagem)
        self.texto_expressao.set(expressao)
        self.resultado_indefinido = True
        self.substituir_visor = True

        fonte = (
            Tema.FONTE_VISOR_ERRO_CURTO
            if mensagem == "Resultado indefinido"
            else Tema.FONTE_VISOR_ERRO_LONGO
        )
        self.visor.config(font=fonte)

        self._bloquear_botoes_erro()

    def _limpar_resultado_indefinido(
        self,
        novo_valor: str = "0",
    ) -> None:
        self.texto_visor.set(novo_valor)
        self.texto_expressao.set("")
        self.numero_atual = float(novo_valor)
        self.operador_atual = None
        self.resultado_indefinido = False
        self.substituir_visor = False

        self.visor.config(font=Tema.FONTE_VISOR)
        self._desbloquear_botoes_erro()

    def _bloquear_botoes_erro(self) -> None:
        for nome, botao in self.botoes_principais.items():
            if nome in BOTOES_PERMITIDOS_EM_ERRO:
                botao.config(state="normal")
            else:
                botao.config(
                    state="disabled",
                    bg=Tema.COR_BOTAO_DESATIVADO,
                    disabledforeground=Tema.COR_TEXTO_DESATIVADO,
                )

        self.memoria.bloquear_por_erro()

    def _desbloquear_botoes_erro(self) -> None:
        for nome, botao in self.botoes_principais.items():
            if nome == "=":
                botao.config(
                    state="normal",
                    bg=Tema.COR_BOTAO_IGUAL,
                    fg="#000000",
                    disabledforeground="#000000",
                )
            else:
                botao.config(
                    state="normal",
                    bg=Tema.COR_BOTAO,
                    fg=Tema.COR_TEXTO,
                    disabledforeground=Tema.COR_TEXTO,
                )

        self.memoria.desbloquear_apos_erro()

    def _mostrar_erro(self) -> None:
        self.texto_visor.set("Erro")
        self.texto_expressao.set("")
        self.operador_atual = None
        self.substituir_visor = True

    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    @staticmethod
    def formatar_numero(numero: float) -> str:
        numero = float(numero)
        return str(int(numero)) if numero.is_integer() else str(numero)
