import tkinter as tk

from gerenciador_historico import GerenciadorHistorico
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
from tema import Tema


OPERADORES_COMUNS = {"+", "-", "×", "÷"}
OPERACOES_ESPECIAIS = {"x²", "√x", "%", "1/x"}

GRADE_BOTOES = (
    ("%", "CE", "C", "⌫"),
    ("1/x", "x²", "√x", "÷"),
    ("7", "8", "9", "×"),
    ("4", "5", "6", "-"),
    ("1", "2", "3", "+"),
    ("+/-", "0", ".", "="),
)

BOTOES_PERMITIDOS_EM_ERRO = {
    "1", "2", "3", "4", "5",
    "6", "7", "8", "9",
    "CE", "C", "⌫", "=",
}


class CalculadoraPadrao(tk.Frame):
    """
    Implementa exclusivamente o modo Padrão da calculadora.

    Responsabilidades:
    - estado atual do visor e da expressão;
    - operador e números da conta atual;
    - tratamento dos botões principais;
    - execução das operações de operacoes.py;
    - integração com memória e tema;
    - estados de erro.

    A janela principal, o cabeçalho, o menu lateral e a troca de modos
    devem permanecer em calculadora.py.
    """

    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self._inicializar_estado()
        self._configurar_aparencia()
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

        self.historico = GerenciadorHistorico(
            parent=self,
            frame_referencia=self.memoria.frame_memoria,
            ao_recuperar_resultado=self._recuperar_valor_historico,
            ao_abrir_painel=self.memoria.fechar_painel,
        )

        self._criar_botoes_principais()


    # ==========================================================
    # CONSTRUÇÃO DA INTERFACE PRINCIPAL
    # ==========================================================

    def _configurar_layout(self) -> None:
        for coluna in range(4):
            self.columnconfigure(coluna, weight=1)

        self.rowconfigure(0, weight=1)  # Expressão
        self.rowconfigure(1, weight=2)  # Visor
        self.rowconfigure(2, weight=0)  # Memória

        for linha in range(3, 9):
            self.rowconfigure(linha, weight=2)

    def _criar_visor(self) -> None:
        label_expressao = tk.Label(
            self,
            textvariable=self.texto_expressao,
            font=Tema.FONTE_EXPRESSAO,
            anchor="e",
            bg=Tema.COR_VISOR,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            padx=12,
        )
        label_expressao.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="nsew",
            padx=8,
            pady=(6, 0),
        )

        self.visor = tk.Label(
            self,
            textvariable=self.texto_visor,
            font=Tema.FONTE_VISOR,
            anchor="e",
            justify="right",
            bg=Tema.COR_VISOR,
            fg=Tema.COR_TEXTO,
            padx=12,
            pady=8,
        )
        self.visor.grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="nsew",
            padx=8,
            pady=(0, 4),
        )

    def _criar_botoes_principais(self) -> None:
        for linha, valores in enumerate(GRADE_BOTOES, start=3):
            for coluna, texto in enumerate(valores):
                cor_fundo = Tema.COR_BOTAO
                cor_hover = Tema.COR_BOTAO_HOVER
                cor_texto = Tema.COR_TEXTO

                if texto == "=":
                    cor_fundo = Tema.COR_BOTAO_IGUAL
                    cor_hover = Tema.COR_BOTAO_IGUAL_HOVER
                    cor_texto = "#000000"

                botao = tk.Button(
                    self,
                    text=texto,
                    font=Tema.FONTE_BOTAO,
                    bg=cor_fundo,
                    fg=cor_texto,
                    activebackground=cor_hover,
                    activeforeground=cor_texto,
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                    cursor="hand2",
                    command=lambda valor=texto: self.ao_clicar(valor),
                )
                botao.grid(
                    row=linha,
                    column=coluna,
                    padx=2,
                    pady=2,
                    sticky="nsew",
                    ipady=16,
                )

                self.botoes_principais[texto] = botao

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

        self.historico.fechar_painel()

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
                        operador_novo,
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
                f"{self.formatar_numero(segundo_numero)}%"
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
                resultado = self._calcular_divisao(
                    primeiro_numero,
                    segundo_numero,
                )
                if resultado is None:
                    return None
            else:
                return None
            
            self.historico.adicionar(
                primeiro_numero=primeiro_numero,
                operador=operador,
                segundo_numero=segundo_numero,
                resultado=resultado,
            )

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
                mensagem="Não é possível dividir por zero",
                expressao=f"{self.formatar_numero(primeiro_numero)} ÷",
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
        """Fecha painéis temporários antes de o aplicativo trocar de modo."""
        self.memoria.fechar_painel()
        self.historico.fechar_painel()

    def alternar_historico(self) -> None:
        """Abre ou fecha o painel de histórico do modo padrão."""
        self.memoria.fechar_painel()
        self.historico.alternar_painel()

    # ==========================================================
    # ESTADOS DE ERRO
    # ==========================================================

    def _tratar_estado_erro_divisao(self, valor: str) -> bool:
        if not self.resultado_indefinido:
            return False

        if valor in {"1", "2", "3", "4", "5", "6", "7", "8", "9"}:
            self._limpar_resultado_indefinido(valor)
            return True

        if valor in {"=", "CE", "C", "⌫"}:
            self._limpar_resultado_indefinido("0")
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
    # HISTÓRICO
    # ==========================================================

    def _recuperar_valor_historico(
        self,
        resultado: float,
    ) -> None:
        self.numero_atual = float(resultado)
        self.texto_visor.set(
            self.formatar_numero(resultado)
        )
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
