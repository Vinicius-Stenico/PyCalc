from tkinter import ttk
import tkinter as tk
from operacoes import somar, subtrair, dividir, multiplicar, potencia, porcentagem, raiz, fracao
# Criação da classe
class Calculadora(tk.Frame): # Cria classe Calculadora que herda de tk.Frame
    def __init__(self, master): # Método construtor do objeto
        super().__init__(master) # Inicializador do Frame do objeto
        self.pack(fill="both", expand=True) #Coloca o Frame dentro da janela 
# fill="both", faz o Frame prencher o espaço disponível horizontalmente e verticalmente
# expand=True, permite o Frame aumentar junto com a janela

        self.texto_visor = tk.StringVar(value="0")
        self.texto_expressao = tk.StringVar(value=None)
        self.substituir_visor = False
        self.memorias = []
        self.painel_memoria = None

        # Métodos que chamam as funções
        self.configurar_layout()
        self.criar_visor()
        self.criar_botoes()

    def formatar_numero(self, numero):
        numero = float(numero)

        if numero.is_integer():
            return str(int(numero))
        
        return str(numero)

    def configurar_layout(self):
        # Configura as 4 colunas
        for coluna in range(4):
            self.columnconfigure(coluna, weight=1)
            
        self.rowconfigure(0, weight=1) # Label da expressão
        self.rowconfigure(1, weight=2) # Visor principal
        self.rowconfigure(2, weight=4) # Botões de memória

        for linha in range(3, 9):
            self.rowconfigure(linha, weight=2)

    # Cria o visor
    def criar_visor(self):
        self.label_expressao = tk.Label(
            self,
            textvariable=self.texto_expressao,
            font=("Arial", 15),
            anchor="w",
        )

        self.label_expressao.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="nsew"
        )

        self.visor = tk.Entry(
            self,
            textvariable=self.texto_visor,
            font=("Arial", 24),
            justify="right",
            state="readonly"
        )

        self.visor.grid(
            row=1,
            column=0,
            columnspan=4,
            padx=3,
            pady=3,
            sticky="nsew"
        )

    # Criação em Grid de botões
    def criar_botoes(self):

        # Cria o frame para os botões de memória
        frame_memoria = tk.Frame(self)

        frame_memoria.grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="nsew"
        )

        # Cria os botões de memória
        botoes_memoria = ["MC", "MR", "M+", "M-", "MS", "M⌄"]

        for coluna, texto in enumerate(botoes_memoria):
            frame_memoria.columnconfigure(coluna, weight=4)

            botao = tk.Button(
                frame_memoria,
                text=texto,
                font=("Arial", 11),
                relief="flat",
                command=lambda valor=texto: self.ao_clicar(valor)
            )

            botao.grid(
                row=0,
                column=coluna,
                sticky="nsew",
                padx=1,
                pady=1
            )

        # Lista dos botões
        botoes = [
            ["%", "CE", "C", "⌫"],
            ["1/x", "x²", "√x", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["+/-", "0", ".", "="]
        ]

        for linha, valores in enumerate(botoes, start=3): # Percorre lista e entrega índice e valor, linhas começam em 1
            for coluna, texto in enumerate(valores): # Percorre os elementos de cada linha
                botao = tk.Button( # Criação do Botão
                    self, # Botão criado dentro de Frame
                    text=texto, # Texto do botão é o mesmo da lista
                    font=("Arial", 18),
                    command=lambda valor=texto: self.ao_clicar(valor) # função que será executada quando botão for pressionado
                    # lambda é uma função pequena e anônima, quando botão for clicado ela irá chamar o botão que foi pressionado
                    # valor = texto, faz com que cada botão guarde seu próprio texto
                )
                # Posicionamento no grid
                botao.grid(
                    row=linha, # Define linha
                    column=coluna, # Define coluna
                    padx=3, # Espaço Horizontal
                    pady=3, # Espaço Vertical
                    sticky="nsew" # faz botão preencher toda a célula do grid
                    # letras significam: n = norte, s = sul, e = leste, w = oeste  botão se expande para todas as direções
                )
    
    def mostrar_painel_memoria(self):
        # Se o painel já estiver aberto, fecha
        if (
            self.painel_memoria is not None
            and self.painel_memoria.winfo_exists()
        ):
            self.painel_memoria.destroy()
            self.painel_memoria = None
            return
        
        self.painel_memoria = tk.Frame(
            self,
            bg="#202020",
            bd=0
        )

        self.painel_memoria.place(
            relx=0,
            rely=0.26,
            relwidth=1,
            relheight=0.74
        )

        if not self.memorias:
            label_vazio = tk.Label(
                self.painel_memoria,
                text="Não há nada salvo na memória",
                bg="#202020",
                fg="white",
                font=("Arial", 13)
            )

            label_vazio.pack(
                pady=30
            )
        
        else:
            # Reversed mostra os valores mais recentes primeiro
            for numero in reversed(self.memorias):
                texto_numero = self.formatar_numero(numero)

                botao_numero = tk.Button(
                    self.painel_memoria,
                    text=texto_numero,
                    bg="#202020",
                    fg="white",
                    activebackground="#323232",
                    activeforeground="white",
                    font=("Arial", 17, "bold"),
                    relief="flat",
                    anchor="e",
                    command=lambda n=numero: self.recuperar_memoria(n)
                )

                botao_numero.pack(
                    fill="x",
                    padx=15,
                    pady=5,
                    ipady=7
                )

        botao_limpar = tk.Button(
            self.painel_memoria,
            text="🗑",
            bg="#202020",
            fg="white",
            activebackground="#323232",
            activeforeground="white",
            font=("Arial", 16),
            relief="flat",
            command=self.limpar_historico_memoria
        )

        botao_limpar.pack(
        side="bottom",
        anchor="e",
        padx=15,
        pady=12
    )

    def recuperar_memoria(self, numero):
        self.texto_visor.set(
            self.formatar_numero(numero)
        )

        self.substituir_visor = True

        if (
            self.painel_memoria is not None
            and self.painel_memoria.winfo_exists()
        ):
            self.painel_memoria.destroy()
            self.painel_memoria = None

    def limpar_historico_memoria(self):
        self.memorias.clear()

        if (
            self.painel_memoria is not None
            and self.painel_memoria.winfo_exists()
        ):
            self.painel_memoria.destroy()
            self.painel_memoria = None

        print("Histórico da memória apagado")

    def ao_clicar(self, valor):
        texto_atual = self.texto_visor.get()
        expressao = self.texto_expressao.get() 

        if valor in ["+", "-", "×", "÷"]:
            expressao = self.texto_expressao.get()
            texto_atual = self.texto_visor.get()

            # Verificador de Cálculo após clicar em um operador
            if expressao:
                partes = expressao.split()
                
                if len(partes) >= 2: 
                    operador_anterior = partes[1]


                    if self.substituir_visor:
                        numero = partes[0]

                        self.texto_expressao.set(f"{numero} {valor}")
                        print(
                            f"Operador alterado de "
                            f"{operador_anterior} para {valor}"
                        )
                        return
                    
                    if texto_atual:
                        self.calcular_resultado()

                        resultado = self.texto_visor.get()

                        self.texto_expressao.set(
                            f"{resultado} {valor}"
                        )
                        self.texto_visor.set(resultado)
                        self.substituir_visor = True
                        return
                    

                
                operador = partes[1]
                print("Operador:", operador)
                
                if valor in ["+", "-", "×", "÷"] and operador == valor:
                    self.calcular_resultado()
                    resultado = self.texto_visor.get()
                    self.texto_expressao.set(f"{resultado} {valor}")
                    self.texto_visor.set(resultado)

                    self.substituir_visor = True # Váriavel vira True para substituir o visor após o cálculo
                    return
        
        if valor in ["MC", "MR", "MS", "M+", "M-", "M⌄"]:
            if valor == "MC":
                if self.memorias:
                    removido = self.memorias.pop()
                    print("Memória removida:", removido)

                return
            
            elif valor == "MR":
                if self.memorias:
                    numero = self.memorias[-1]

                    self.texto_visor.set(
                        self.formatar_numero(numero)
                    )

                    self.substituir_visor = True

                return
            
            elif valor == "MS":
                numero = float(self.texto_visor.get())

                self.memorias.append(numero)

                self.substituir_visor = True
                print("Valor salvo na memória:", numero)
                print("Memórias:", self.memorias)
                return
            
            elif valor == "M+":
                numero_atual = float(self.texto_visor.get())

                if self.memorias:
                    self.memorias[-1] += numero_atual
                else:
                    self.memorias.append(numero_atual)

                print("Memória atual:", self.memorias[-1])
                return
            
            elif valor == "M-":
                numero_atual = float(self.texto_visor.get())

                if self.memorias:
                    self.memorias[-1] -= numero_atual
                else:
                    self.memorias.append(-numero_atual)

                print("Memória atual:", self.memorias[-1])
                return
            
            elif valor == "M⌄":
                self.mostrar_painel_memoria()
                return

        if valor in ["+", "-", "×", "÷"]:
            expressao = self.texto_expressao.get()
            texto_atual = self.texto_visor.get()

            if expressao:
                partes = expressao.split()

                self.calcular_resultado()

                resultado = self.texto_visor.get()

                self.texto_expressao.set(f"{resultado} {valor}")
                self.texto_visor.set(resultado)

            else:
                self.texto_expressao.set(f"{texto_atual} {valor}")
                self.texto_visor.set("")

            return
    
        if valor in ["x²", "√x", "%", "1/x"]:
            if valor == "x²":
                n1 = self.texto_visor.get()
                print("Número 1: ", n1)
                self.texto_expressao.set(f"sqr({n1})")

                resultado = potencia(float(n1))
                self.texto_visor.set(resultado)

                self.substituir_visor = True
            if valor == "√x":
                n1 = self.texto_visor.get()
                print("Número 1: ", n1)
                self.texto_expressao.set(f"√{n1}")

                resultado = raiz(float(n1))
                self.texto_visor.set(resultado)

                self.substituir_visor = True

            if valor == "%":
                expressao = self.texto_expressao.get()
                n1 = expressao.split()[0]
                operador = expressao.split()[1]
                print("Número 1: ", n1)
                n2 = self.texto_visor.get()
                print("Número 2: ", n2)
                resultado = porcentagem(float(n1), float(n2))
                self.texto_visor.set(resultado)
                self.substituir_visor = True
                self.texto_expressao.set(n1 + " " + operador + " " + str(resultado))

            if valor == "1/x":
                n1 = self.texto_visor.get()
                print("Número 1: ", n1)
                self.texto_expressao.set(f"1/{n1}")

                resultado = fracao(float(n1))
                self.texto_visor.set(resultado)

                self.substituir_visor = True

        elif valor == "⌫":
            texto_atual = self.texto_visor.get()
            self.texto_visor.set(texto_atual[:-1])
        
        elif valor == "C":
            self.texto_visor.set("")
            self.texto_expressao.set("")
            print("Reiniciado conta")
        
        elif valor == "CE":
            self.texto_visor.set("")
            print("Entrada do visor limpa")
        
        elif valor == "+/-":
            n1 = float(self.texto_visor.get())
            n1 = -n1
            print("Número 1: ", n1)
            print("Alterado o sinal do número")
            self.texto_visor.set(float(n1))

        elif valor == "=":
            print("Calcular resultado")
            self.calcular_resultado()

        elif valor.isdigit():
            if texto_atual == "0" or self.substituir_visor:
                self.texto_visor.set(valor)
                self.substituir_visor = False
            else:
                self.texto_visor.set(texto_atual + valor)
        else:
            texto_atual = self.texto_visor.get()
            self.texto_visor.set(texto_atual + valor)

        print(f"Botão pressionado: {valor}")

    def calcular_resultado(self):
        print("Calculando")

        expressao = self.texto_expressao.get()
        partes = expressao.split()

        n1 = float(partes[0])
        operador = partes[1]
        n2 = float(self.texto_visor.get())

        
        print(
            "Número 1: ", n1, 
            "Número 2: ", n2, 
            "Operador: ", operador
        )

        if operador == "+":
            resultado = somar(n1, n2)

        elif operador == "-":
            resultado = subtrair(n1, n2)

        elif operador == "×":
            resultado = multiplicar(n1, n2)

        elif operador == "÷":
            resultado = dividir(n1, n2)

        self.texto_visor.set(resultado)
        self.texto_expressao.set(f"{n1} {operador} {n2} =")
        self.substituir_visor = True


janela = tk.Tk()
janela.title("Calculadora")
janela.geometry("400x500")
janela.minsize(300, 400)
janela.maxsize(600, 800)



calc = Calculadora(janela) # Cria um objeto da classe Calculadora
# calc = self, janela = master

janela.mainloop() # Ciclo principal de eventos
