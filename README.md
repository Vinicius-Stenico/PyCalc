<div align="center">

# PyCalc

**Uma calculadora desktop modular desenvolvida em Python, inspirada na experiência visual e funcional da Calculadora do Windows.**

![Python](https://img.shields.io/badge/Python-aplicação%20desktop-blue)
![Interface](https://img.shields.io/badge/Interface-Tkinter-informational)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

</div>

> [!IMPORTANT]
> O PyCalc está em desenvolvimento. Algumas funcionalidades e modos de cálculo ainda podem estar incompletos ou sujeitos a alterações.

<div align="center">

### Demonstração

[ADICIONAR IMAGEM OU GIF DA CALCULADORA]

</div>

---

## Índice

* [Sobre o projeto](#sobre-o-projeto)
* [Principais funcionalidades](#principais-funcionalidades)
* [Tecnologias utilizadas](#tecnologias-utilizadas)
* [Estrutura do projeto](#estrutura-do-projeto)
* [Requisitos](#requisitos)
* [Instalação](#instalação)
* [Como executar](#como-executar)
* [Exemplos de uso](#exemplos-de-uso)
* [Atalhos de teclado](#atalhos-de-teclado)
* [Arquitetura](#arquitetura)
* [Roadmap](#roadmap)
* [Melhorias futuras](#melhorias-futuras)
* [Como contribuir](#como-contribuir)
* [Problemas e sugestões](#problemas-e-sugestões)
* [Autor](#autor)
* [Licença](#licença)
* [Agradecimentos](#agradecimentos)

---

## Sobre o projeto

O **PyCalc** é uma aplicação desktop de calculadora desenvolvida com **Python** e **Tkinter**.

O projeto foi inspirado na Calculadora do Windows e tem como objetivo oferecer uma interface familiar, organizada e funcional, reunindo diferentes modos de cálculo em uma única aplicação.

Além das operações matemáticas tradicionais, o PyCalc busca disponibilizar recursos como histórico de cálculos, sistema de memória, interação pelo teclado, cálculos científicos e operações com datas.

A aplicação foi estruturada de forma modular para facilitar a manutenção do código e permitir que novos modos e funcionalidades sejam adicionados sem concentrar toda a lógica em um único arquivo.

---

## Principais funcionalidades

### Modos de cálculo

* Calculadora padrão
* Calculadora científica
* Cálculos com datas
* Menu lateral para alternar entre os modos

### Operações matemáticas

* Adição
* Subtração
* Multiplicação
* Divisão
* Porcentagem
* Raiz quadrada
* Potência ao quadrado
* Inverso de um número
* Alteração de sinal

### Memória

* `MC` — limpa os valores armazenados
* `MR` — recupera um valor da memória
* `MS` — armazena o valor atual
* `M+` — adiciona o valor atual à memória
* `M-` — subtrai o valor atual da memória
* Lista de valores armazenados

### Outros recursos

* Histórico de cálculos
* Entrada de valores pelo teclado
* Tratamento de erros matemáticos
* Interface inspirada na Calculadora do Windows
* Código organizado em módulos independentes

---

## Tecnologias utilizadas

| Tecnologia | Utilização                           |
| ---------- | ------------------------------------ |
| Python     | Linguagem principal da aplicação     |
| Tkinter    | Construção da interface gráfica      |
| Git        | Controle de versão                   |
| GitHub     | Hospedagem e documentação do projeto |

O PyCalc utiliza principalmente recursos da biblioteca padrão do Python. Dependências adicionais devem ser verificadas diretamente nos arquivos do projeto.

---

## Estrutura do projeto

A estrutura pode sofrer alterações durante o desenvolvimento.

```text
PyCalc/
├── assets/
│   └── [ícones, imagens e recursos visuais]
│
├── modos/
│   ├── cientifica.py
│   ├── data.py
│   └── padrao.py
│
├── calculadora.py
├── gerenciador_memoria.py
├── interacao_teclado_visor.py
├── menu_lateral.py
├── operacoes.py
├── operacoes_cientificas.py
├── tema.py
├── .gitignore
└── README.md
```

### Responsabilidade dos principais arquivos

| Arquivo                      | Responsabilidade                                                                 |
| ---------------------------- | -------------------------------------------------------------------------------- |
| `calculadora.py`             | Inicialização da aplicação, gerenciamento dos modos e integração dos componentes |
| `gerenciador_memoria.py`     | Gerenciamento das funções e dos valores armazenados na memória                   |
| `interacao_teclado_visor.py` | Comunicação entre o teclado, o visor e as ações da calculadora                   |
| `menu_lateral.py`            | Criação e funcionamento do menu lateral                                          |
| `operacoes.py`               | Operações matemáticas utilizadas no modo padrão                                  |
| `operacoes_cientificas.py`   | Operações específicas do modo científico                                         |
| `tema.py`                    | Cores, fontes e configurações visuais                                            |
| `modos/padrao.py`            | Interface e lógica do modo padrão                                                |
| `modos/cientifica.py`        | Interface e lógica do modo científico                                            |
| `modos/data.py`              | Interface e lógica dos cálculos com datas                                        |
| `assets/`                    | Ícones, imagens e outros recursos visuais                                        |

---

## Requisitos

Para executar o projeto, é necessário ter:

* Python instalado no computador
* Tkinter disponível na instalação do Python
* Git, caso o projeto seja clonado pelo terminal

Para verificar se o Python está instalado:

```bash
python --version
```

Em alguns sistemas Linux ou macOS, o comando utilizado pode ser:

```bash
python3 --version
```

Para verificar se o Tkinter está disponível:

```bash
python -m tkinter
```

Caso uma pequena janela seja aberta, o Tkinter está funcionando corretamente.

---

## Instalação

### 1. Clone o repositório

```bash
git clone [URL DO REPOSITÓRIO]
```

### 2. Acesse a pasta do projeto

```bash
cd pycalc
```

### 3. Ambiente virtual — opcional

O uso de um ambiente virtual ajuda a isolar as dependências do projeto.

#### Windows

```cmd
python -m venv venv
venv\Scripts\activate
```

#### Linux ou macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instale as dependências, caso necessário

Execute o comando abaixo somente se o repositório possuir um arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Caso o arquivo não exista, essa etapa pode ser ignorada.

---

## Como executar

Na pasta principal do projeto, execute:

### Windows

```cmd
python calculadora.py
```

### Linux ou macOS

```bash
python3 calculadora.py
```

A janela principal do PyCalc será aberta após a execução.

---

## Exemplos de uso

### Operação básica

Para calcular uma soma:

```text
25 + 17 =
```

Resultado:

```text
42
```

### Operação adicional

Para calcular a raiz quadrada de um número:

```text
√ 144
```

Resultado:

```text
12
```

### Uso da memória

Um fluxo possível para armazenar e recuperar valores é:

```text
1. Digite um número
2. Pressione MS
3. Realize outros cálculos
4. Pressione MR para recuperar o valor armazenado
```

### Histórico

Os cálculos realizados podem ser consultados por meio do botão de histórico da interface.

---

## Atalhos de teclado

Os atalhos podem ser alterados durante o desenvolvimento.

| Ação                    | Tecla                             |
| ----------------------- | --------------------------------- |
| Inserir números         | `0` a `9`                         |
| Adição                  | `+`                               |
| Subtração               | `-`                               |
| Multiplicação           | `*` ou `[CONFIRMAR ATALHO]`       |
| Divisão                 | `/`                               |
| Calcular resultado      | `Enter` ou `=`                    |
| Separador decimal       | `,` ou `.` — `[CONFIRMAR ATALHO]` |
| Apagar último caractere | `Backspace`                       |
| Limpar entrada          | `[CONFIRMAR ATALHO]`              |
| Limpar cálculo          | `Esc` ou `[CONFIRMAR ATALHO]`     |
| Abrir histórico         | `[CONFIRMAR ATALHO]`              |
| Abrir menu lateral      | `[CONFIRMAR ATALHO]`              |

---

## Arquitetura

O PyCalc utiliza uma organização modular, separando a interface, as operações matemáticas e os componentes de interação em arquivos distintos.

```text
Interface dos modos
        │
        ▼
Gerenciamento principal
        │
        ├── Operações matemáticas
        ├── Gerenciador de memória
        ├── Histórico
        ├── Interação com o teclado
        ├── Menu lateral
        └── Tema da interface
```

Essa divisão oferece algumas vantagens:

* reduz a quantidade de responsabilidades de cada arquivo;
* facilita a localização e a correção de erros;
* permite reutilizar componentes entre diferentes modos;
* torna mais simples adicionar novos tipos de calculadora;
* melhora a legibilidade e a manutenção do código;
* evita que toda a aplicação dependa de uma única classe ou arquivo.

Cada modo pode possuir sua própria interface e lógica, enquanto recursos compartilhados, como memória, tema e navegação, permanecem centralizados.

---

## Roadmap

### Implementado

* [x] Estrutura modular inicial
* [x] Modo de calculadora padrão
* [x] Modo de calculadora científico
* [x] Modo de calculadora de datas
* [x] Operações matemáticas básicas
* [x] Operações adicionais do modo padrão
* [x] Sistema de memória
* [x] Menu lateral
* [x] Histórico de cálculos
* [x] Integração com o teclado
* [x] Tratamento de erros matemáticos
* [x] Interface inspirada na Calculadora do Windows

### Em desenvolvimento ou planejado

* [ ] Adicionar modo programador
* [ ] Adicionar conversores de unidades
* [ ] Melhorar o histórico de cálculos
* [ ] Aprimorar os atalhos de teclado
* [ ] Implementar temas claro e escuro
* [ ] Criar testes automatizados
* [ ] Gerar um executável para Windows
* [ ] Criar um instalador
* [ ] Adicionar suporte a múltiplos idiomas

---

## Melhorias futuras

Além dos itens presentes no roadmap, o projeto poderá receber:

* configurações personalizáveis;
* persistência do histórico entre execuções;
* persistência dos valores armazenados na memória;
* melhorias de acessibilidade;
* navegação completa utilizando apenas o teclado;
* documentação técnica dos principais componentes;
* validação automática da formatação do código;
* publicação de versões estáveis na área de releases do GitHub.

Essas funcionalidades são possibilidades futuras e ainda não fazem parte necessariamente da versão atual do projeto.

---

## Como contribuir

Contribuições são bem-vindas.

Para contribuir:

1. Faça um fork do repositório.
2. Crie uma branch para sua alteração:

```bash
git checkout -b feature/nome-da-funcionalidade
```

3. Faça as alterações necessárias.
4. Adicione os arquivos modificados:

```bash
git add .
```

5. Registre suas alterações:

```bash
git commit -m "feat: adiciona nova funcionalidade"
```

6. Envie a branch para o seu fork:

```bash
git push origin feature/nome-da-funcionalidade
```

7. Abra um Pull Request descrevendo as alterações realizadas.

Antes de enviar uma contribuição, verifique se a modificação mantém a organização modular e não interfere no funcionamento dos outros modos da calculadora.

---

## Problemas e sugestões

Encontrou um erro ou possui uma sugestão?

Abra uma **Issue** no repositório e inclua, quando possível:

* descrição clara do problema ou sugestão;
* etapas necessárias para reproduzir o erro;
* comportamento esperado;
* comportamento apresentado;
* capturas de tela;
* sistema operacional utilizado;
* versão do Python;
* mensagens de erro exibidas no terminal.

[ABRIR UMA ISSUE — ADICIONAR LINK]

---

## Autor

Desenvolvido por **Vinícius Gabriel**.

* GitHub: [ADICIONAR_USUARIO_DO_GITHUB]
* LinkedIn: [ADICIONAR_LINK_DO_LINKEDIN]

---

## Licença

Este projeto ainda não possui uma licença definida.

`[DEFINIR LICENÇA]`

Até que uma licença seja adicionada, consulte o autor antes de copiar, modificar ou distribuir partes significativas do projeto.

---

## Agradecimentos

* À documentação oficial do Python e do Tkinter.
* À Calculadora do Windows, utilizada como referência visual e funcional.
* À comunidade de desenvolvimento Python, responsável por materiais, exemplos e discussões que auxiliam no aprendizado e na evolução do projeto.

---

<div align="center">

**PyCalc — uma calculadora modular construída para evoluir.**

</div>
