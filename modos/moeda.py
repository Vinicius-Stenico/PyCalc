import json
import queue
import threading
import tkinter as tk
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.error import URLError
from urllib.request import urlopen

from tema import Tema


MOEDAS = {
    "USD": ("Estados Unidos - Dólar", "$"),
    "EUR": ("Europa - Euro", "€"),
    "BRL": ("Brasil - Real", "R$"),
    "GBP": ("Reino Unido - Libra", "£"),
    "JPY": ("Japao - Iene", "¥"),
    "CAD": ("Canadá - Dólar", "C$"),
    "AUD": ("Austrália - Dólar", "A$"),
    "CHF": ("Suíça - Franco", "CHF"),
    "CNY": ("China - Yuan", "¥"),
    "ARS": ("Argentina - Peso", "$"),
    "BGN": ("Bulgária - Lev", "лв"),
    "CZK": ("Tchéquia - Coroa", "Kč"),
    "DKK": ("Dinamarca - Coroa Dinamarquesa", "kr"),
    "HKD": ("Hong Kong - Dólar", "HK$"),
    "HUF": ("Hungria - Forint", "Ft"),
    "IDR": ("Indonésia - Rupia", "Rp"),
    "ILS": ("Israel - Novo Shekel", "₪"),
    "INR": ("Índia - Rúpia", "₹"),
    "ISK": ("Islândia - Coroa", "kr"),
    "KRW": ("Coreia do Sul - Won", "₩"),
    "MXN": ("México - Peso", "$"),
    "MYR": ("Malásia - Ringgit", "RM"),
    "NOK": ("Noruega - Coroa", "kr"),
    "NZD": ("Nova Zelândia - Dólar", "NZ$"),
    "PHP": ("Filipinas - Peso", "₱"),
    "PLN": ("Polônia - Zlóti", "zł"),
    "RON": ("Romênia - Leu", "lei"),
    "SEK": ("Suécia - Coroa", "kr"),
    "SGD": ("Singapura - Dólar", "S$"),
    "THB": ("Tailândia - Baht", "฿"),
    "TRY": ("Turquia - Lira", "₺"),
    "ZAR": ("África do Sul - Rand", "R"),
}

TAXAS_PADRAO_USD = {
    "USD": Decimal("1"),
    "EUR": Decimal("0.8756"),
    "BRL": Decimal("5.50"),
    "GBP": Decimal("0.74"),
    "JPY": Decimal("144.00"),
    "CAD": Decimal("1.37"),
    "AUD": Decimal("1.53"),
    "CHF": Decimal("0.82"),
    "CNY": Decimal("7.17"),
    "ARS": Decimal("1200"),
    "BGN": Decimal("1.71"),
    "CZK": Decimal("21.30"),
    "DKK": Decimal("6.53"),
    "HKD": Decimal("7.85"),
    "HUF": Decimal("345"),
    "IDR": Decimal("16200"),
    "ILS": Decimal("3.55"),
    "INR": Decimal("86"),
    "ISK": Decimal("123"),
    "KRW": Decimal("1360"),
    "MXN": Decimal("18.80"),
    "MYR": Decimal("4.25"),
    "NOK": Decimal("10.20"),
    "NZD": Decimal("1.65"),
    "PHP": Decimal("56.50"),
    "PLN": Decimal("3.75"),
    "RON": Decimal("4.35"),
    "SEK": Decimal("9.55"),
    "SGD": Decimal("1.28"),
    "THB": Decimal("32.50"),
    "TRY": Decimal("39.50"),
    "ZAR": Decimal("17.80"),
}

MOEDAS_ATUALIZAVEIS = (
    "USD",
    "EUR",
    "BRL",
    "GBP",
    "JPY",
    "CAD",
    "AUD",
    "CHF",
    "CNY",
    "BGN",
    "CZK",
    "DKK",
    "HKD",
    "HUF",
    "IDR",
    "ILS",
    "INR",
    "ISK",
    "KRW",
    "MXN",
    "MYR",
    "NOK",
    "NZD",
    "PHP",
    "PLN",
    "RON",
    "SEK",
    "SGD",
    "THB",
    "TRY",
    "ZAR",
)

MOEDAS = {
    "AFN": ("Afeganistão - Afghani", "AFN"),
    "ZAR": ("África do Sul - Rand", "R"),
    "ALL": ("Albânia - Lek", "ALL"),
    "AOA": ("Angola - Angolan Kwanza", "Kz"),
    "SAR": ("Arábia Saudita - Riyal", "SAR"),
    "DZD": ("Argélia - Dinar", "DZD"),
    "ARS": ("Argentina - Peso", "$"),
    "AMD": ("Armênia - Dram", "AMD"),
    "AWG": ("Aruba - Florim", "AWG"),
    "AUD": ("Austrália - Dólar", "A$"),
    "AZN": ("Azerbaijão - Novo Manat", "AZN"),
    "BSD": ("Bahamas - Dólar", "B$"),
    "BHD": ("Bahrain - Dinar", "BHD"),
    "BDT": ("Bangladesh - Taka", "BDT"),
    "BBD": ("Barbados - Dólar", "Bds$"),
    "BYN": ("Belarus - Rublo", "BYN"),
    "BZD": ("Belize - Dólar", "BZ$"),
    "BMD": ("Bermudas - Dólar", "BD$"),
    "BOB": ("Bolívia - Boliviano", "Bs"),
    "BAM": ("Bósnia e Herzegovina - Marka Conversível", "BAM"),
    "BWP": ("Botsuana - Pula", "BWP"),
    "BRL": ("Brasil - Real", "R$"),
    "BND": ("Brunei - Dólar", "B$"),
    "BGN": ("Bulgária - Lev", "BGN"),
    "BIF": ("Burundi - Franco", "BIF"),
    "BTN": ("Butão - Ngultrum Butanês", "BTN"),
    "CVE": ("Cabo Verde - Escudo", "CVE"),
    "KHR": ("Camboja - Riel", "KHR"),
    "CAD": ("Canadá - Dólar", "C$"),
    "QAR": ("Catar - Riyal", "QAR"),
    "KZT": ("Cazaquistão - Tenge", "KZT"),
    "CNH": ("China - Yuan (offshore)", "CNH"),
    "CNY": ("China - Yuan", "¥"),
    "SGD": ("Cingapura - Dólar", "S$"),
    "COP": ("Colômbia - Peso", "$"),
    "XAF": (
        "Communauté Financière Africaine (BEAC) - Franco CFA da África Central BEAC",
        "XAF",
    ),
    "KMF": ("Comores - Franco", "KMF"),
    "CDF": ("Congo - Franco", "CDF"),
    "KRW": ("Coreia do Sul - Won", "₩"),
    "CRC": ("Costa Rica - Colon", "₡"),
    "CUP": ("Cuba - Peso", "$"),
    "DKK": ("Dinamarca - Coroa Dinamarquesa", "kr"),
    "DJF": ("Djibuti - Franco", "DJF"),
    "EGP": ("Egito - Libra", "EGP"),
    "AED": ("Emirados Árabes Unidos - Dirham", "AED"),
    "USD": ("Estados Unidos - Dólar", "$"),
    "ETB": ("Etiópia - Birr", "ETB"),
    "EUR": ("Europa - Euro", "€"),
    "FJD": ("Fiji - Dólar", "FJ$"),
    "PHP": ("Filipinas - Peso", "₱"),
    "XPF": ("French overseas collectivities - Franco da África Central", "XPF"),
    "GMD": ("Gâmbia - Dalasi", "GMD"),
    "GHS": ("Gana - Cedi", "GHS"),
    "GEL": ("Geórgia - Lari", "GEL"),
    "GTQ": ("Guatemala - Quetzal", "GTQ"),
    "GYD": ("Guiana - Dólar da Guiana", "GY$"),
    "GNF": ("Guiné - Franco", "GNF"),
    "HTG": ("Haiti - Gourde", "HTG"),
    "HNL": ("Honduras - Lempira", "HNL"),
    "HUF": ("Hungria - Forinte", "Ft"),
    "YER": ("Iêmen - Rial", "YER"),
    "KYD": ("Ilhas Cayman - Dólar", "CI$"),
    "INR": ("Índia - Rúpia", "₹"),
    "IDR": ("Indonésia - Rúpia", "Rp"),
    "IRR": ("Irã - Rial", "IRR"),
    "IQD": ("Iraque - Dinar", "IQD"),
    "ISK": ("Islândia - Coroa", "kr"),
    "ILS": ("Israel - Shekel", "₪"),
    "JMD": ("Jamaica - Dólar", "J$"),
    "JPY": ("Japão - Iene", "¥"),
    "JOD": ("Jordânia - Dinar", "JOD"),
    "KWD": ("Kuwait - Dinar", "KWD"),
    "LAK": ("Laos - Kip", "LAK"),
    "LSL": ("Lesoto - Loti", "LSL"),
    "LBP": ("Líbano - Libra", "LBP"),
    "LRD": ("Libéria - Dólar", "L$"),
    "LYD": ("Líbia - Dinar", "LYD"),
    "MKD": ("Macedônia do Norte - Denar", "MKD"),
    "MGA": ("Madagascar - Ariary de Madagascar", "MGA"),
    "MYR": ("Malásia - Ringgit", "RM"),
    "MWK": ("Maláui - Quacha", "MWK"),
    "MVR": ("Maldivas - Rúpia", "MVR"),
    "MAD": ("Marrocos - Dirham", "MAD"),
    "MUR": ("Maurício - Rúpia", "MUR"),
    "MRU": ("Mauritânia - Ouguiya", "MRU"),
    "MXN": ("México - Peso", "$"),
    "MZN": ("Moçambique - Metical", "MZN"),
    "MDL": ("Moldova - Leu", "MDL"),
    "MNT": ("Mongólia - Tughrik Mongol", "MNT"),
    "MMK": ("Myanmar - Kyat", "MMK"),
    "NAD": ("Namíbia - Dólar", "N$"),
    "NPR": ("Nepal - Rúpia", "NPR"),
    "NIO": ("Nicarágua - Córdoba", "NIO"),
    "NGN": ("Nigéria - Naira", "₦"),
    "NOK": ("Noruega - Coroa Norueguesa", "kr"),
    "NZD": ("Nova Zelândia - Dólar", "NZ$"),
    "OMR": ("Omã - Rial", "OMR"),
    "PAB": ("Panamá - Balboa", "B/."),
    "PGK": ("Papua Nova Guiné - Kina", "PGK"),
    "PKR": ("Paquistão - Rúpia", "PKR"),
    "PYG": ("Paraguai - Guarani", "PYG"),
    "PEN": ("Peru - Nuevo Sol", "S/"),
    "PLN": ("Polônia - Zloty", "zł"),
    "KES": ("Quênia - Xelim", "KES"),
    "HKD": ("RAE de Hong Kong - Dólar", "HK$"),
    "MOP": ("RAE de Macau - Pataca", "MOP"),
    "GBP": ("Reino Unido - Libra", "£"),
    "CLP": ("República do Chile - Peso", "$"),
    "DOP": ("República Dominicana - Peso", "RD$"),
    "CZK": ("República Tcheca - Coroa", "Kč"),
    "RON": ("Romênia - Leu novo", "lei"),
    "RWF": ("Ruanda - Franco", "RWF"),
    "RUB": ("Rússia - Rublo", "₽"),
    "SHP": ("Santa Helena, Ascensão e Tristão da Cunha - Libra", "£"),
    "STN": ("São Tomé e Príncipe - Dobra de São Tomé", "STN"),
    "SCR": ("Seicheles - Rúpia", "SCR"),
    "RSD": ("Sérvia - Dinar", "RSD"),
    "SYP": ("Síria - Libra", "SYP"),
    "SOS": ("Somália - Xelim", "SOS"),
    "LKR": ("Sri Lanka - Rúpia", "LKR"),
    "SZL": ("Suazilândia - Lilangeni", "SZL"),
    "SDG": ("Sudão - Libra", "SDG"),
    "SEK": ("Suécia - Coroa", "kr"),
    "CHF": ("Suíça - Franco", "CHF"),
    "THB": ("Tailândia - Baht", "฿"),
    "TWD": ("Taiwan - Novo Dólar", "NT$"),
    "TZS": ("Tanzânia - Xelim", "TZS"),
    "TTD": ("Trinidad e Tobago - Dólar", "TT$"),
    "TND": ("Tunísia - Dinar", "TND"),
    "TMT": ("Turcomenistão - Manat", "TMT"),
    "TRY": ("Turquia - Lira", "₺"),
    "UAH": ("Ucrânia - Hryvna", "UAH"),
    "UGX": ("Uganda - Xelim", "UGX"),
    "UYU": ("Uruguai - Peso", "$U"),
    "UZS": ("Uzbequistão - Som", "UZS"),
    "VUV": ("Vanuatu - Vatu", "VUV"),
    "VES": ("Venezuela - Bolivar Soberano", "VES"),
    "VND": ("Vietnã - Dong", "₫"),
    "ZMW": ("Zâmbia - Quacha", "ZMW"),
}

TAXAS_PADRAO_USD = {codigo: Decimal("1") for codigo in MOEDAS}
TAXAS_PADRAO_USD.update(
    {
        "USD": Decimal("1"),
        "EUR": Decimal("0.8756"),
        "BRL": Decimal("5.50"),
        "GBP": Decimal("0.74"),
        "JPY": Decimal("144.00"),
        "CAD": Decimal("1.37"),
        "AUD": Decimal("1.53"),
        "CHF": Decimal("0.82"),
        "CNY": Decimal("7.17"),
        "CNH": Decimal("7.17"),
        "ARS": Decimal("1200"),
        "BGN": Decimal("1.71"),
        "CZK": Decimal("21.30"),
        "DKK": Decimal("6.53"),
        "HKD": Decimal("7.85"),
        "HUF": Decimal("345"),
        "IDR": Decimal("16200"),
        "ILS": Decimal("3.55"),
        "INR": Decimal("86"),
        "ISK": Decimal("123"),
        "KRW": Decimal("1360"),
        "MXN": Decimal("18.80"),
        "MYR": Decimal("4.25"),
        "NOK": Decimal("10.20"),
        "NZD": Decimal("1.65"),
        "PHP": Decimal("56.50"),
        "PLN": Decimal("3.75"),
        "RON": Decimal("4.35"),
        "SEK": Decimal("9.55"),
        "SGD": Decimal("1.28"),
        "THB": Decimal("32.50"),
        "TRY": Decimal("39.50"),
        "ZAR": Decimal("17.80"),
    }
)

TECLADO_MOEDA = (
    ("CE", "⌫"),
    ("7", "8", "9"),
    ("4", "5", "6"),
    ("1", "2", "3"),
    ("", "0", ","),
)


class CalculadoraMoeda(tk.Frame):
    """Conversor de moeda."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=Tema.COR_FUNDO)

        self.moeda_origem = "USD"
        self.moeda_destino = "EUR"
        self.valor_digitado = "0"
        self.campo_ativo = "origem"
        self.atualizando_campos = False
        self.taxas_usd = TAXAS_PADRAO_USD.copy()
        self.atualizado_em = datetime.now()
        self.atualizando_taxas = False
        self.fila_resultado_taxas: queue.Queue[
            tuple[str, dict[str, Decimal] | Exception]
        ] = queue.Queue()

        self.frame_menu_moeda: tk.Frame | None = None
        self.alvo_menu_moeda: str | None = None
        self.canvas_menu_moeda: tk.Canvas | None = None
        self.scrollbar_menu_moeda: tk.Canvas | None = None
        self.thumb_menu_moeda: int | None = None
        self.scroll_drag_y = 0
        self.scroll_drag_inicio = 0.0
        self.bind_clique_fora_moeda: str | None = None

        self.texto_origem = tk.StringVar(value="0")
        self.texto_destino = tk.StringVar(value="0")
        self.texto_taxa = tk.StringVar()
        self.texto_atualizacao = tk.StringVar()
        self.texto_status = tk.StringVar()
        self.texto_origem.trace_add(
            "write",
            lambda *_args: self._ao_editar_valor("origem"),
        )
        self.texto_destino.trace_add(
            "write",
            lambda *_args: self._ao_editar_valor("destino"),
        )

        self._configurar_layout()
        self._criar_interface()
        self._atualizar_tela()
        self.after(100, self._processar_resultados_taxas)

    # ==========================================================
    # CONSTRUCAO
    # ==========================================================

    def _configurar_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)

    def _criar_interface(self) -> None:
        self.frame_conteudo = tk.Frame(
            self,
            bg=Tema.COR_FUNDO,
        )
        self.frame_conteudo.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(8, 2),
        )
        self.frame_conteudo.columnconfigure(0, weight=0)
        self.frame_conteudo.columnconfigure(1, weight=1)

        self._criar_linha_valor(
            linha=0,
            simbolo_var=lambda: MOEDAS[self.moeda_origem][1],
            texto_var=self.texto_origem,
            destaque=True,
        )
        self.botao_origem = self._criar_botao_moeda(
            linha=1,
            comando=lambda: self._alternar_menu_moeda("origem"),
        )

        self._criar_linha_valor(
            linha=2,
            simbolo_var=lambda: MOEDAS[self.moeda_destino][1],
            texto_var=self.texto_destino,
            destaque=False,
        )
        self.botao_destino = self._criar_botao_moeda(
            linha=3,
            comando=lambda: self._alternar_menu_moeda("destino"),
        )

        label_taxa = tk.Label(
            self.frame_conteudo,
            textvariable=self.texto_taxa,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 9),
            anchor="w",
        )
        label_taxa.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(4, 0),
        )

        label_atualizacao = tk.Label(
            self.frame_conteudo,
            textvariable=self.texto_atualizacao,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 9),
            anchor="w",
        )
        label_atualizacao.grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="ew",
        )

        botao_atualizar = tk.Button(
            self.frame_conteudo,
            text="Atualizar taxas",
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_BOTAO_IGUAL,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_BOTAO_IGUAL,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="w",
            padx=0,
            pady=4,
            cursor="hand2",
            command=self._atualizar_taxas,
        )
        botao_atualizar.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="ew",
        )

        label_status = tk.Label(
            self.frame_conteudo,
            textvariable=self.texto_status,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO_SECUNDARIO,
            font=("Segoe UI", 8),
            anchor="w",
        )
        label_status.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="ew",
        )

        self._criar_teclado()

    def _criar_linha_valor(
        self,
        linha: int,
        simbolo_var,
        texto_var: tk.StringVar,
        destaque: bool,
    ) -> None:
        simbolo = tk.Label(
            self.frame_conteudo,
            text=simbolo_var(),
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            font=("Segoe UI", 14),
            anchor="w",
        )
        simbolo.grid(
            row=linha,
            column=0,
            sticky="w",
            pady=(0 if linha == 0 else 6, 0),
        )

        valor = tk.Entry(
            self.frame_conteudo,
            textvariable=texto_var,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            insertbackground=Tema.COR_FUNDO,
            insertontime=0,
            insertofftime=0,
            selectbackground="#0078d7",
            selectforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 30 if destaque else 25),
            relief="flat",
            bd=0,
            highlightthickness=0,
            justify="left",
        )
        valor.grid(
            row=linha,
            column=1,
            sticky="ew",
            padx=(10, 0),
            pady=(0 if linha == 0 else 6, 0),
        )

        if destaque:
            self.label_simbolo_origem = simbolo
            self.entrada_origem = valor
            valor.bind(
                "<FocusIn>",
                lambda _evento: self._selecionar_campo("origem"),
            )
        else:
            self.label_simbolo_destino = simbolo
            self.entrada_destino = valor
            valor.bind(
                "<FocusIn>",
                lambda _evento: self._selecionar_campo("destino"),
            )

    def _criar_botao_moeda(self, linha: int, comando) -> tk.Button:
        botao = tk.Button(
            self.frame_conteudo,
            bg=Tema.COR_FUNDO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            highlightthickness=0,
            anchor="w",
            padx=0,
            pady=4,
            cursor="hand2",
            command=comando,
        )
        botao.grid(
            row=linha,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(0, 4),
        )
        return botao

    def _criar_teclado(self) -> None:
        frame = tk.Frame(self, bg=Tema.COR_FUNDO)
        frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=5,
            pady=(0, 5),
        )
        frame.grid_propagate(False)
        frame.configure(height=220)

        for coluna in range(3):
            frame.columnconfigure(
                coluna,
                weight=1,
                uniform="teclado_moeda",
                minsize=96,
            )

        for linha in range(len(TECLADO_MOEDA)):
            frame.rowconfigure(linha, weight=1, uniform="teclado_moeda")

        for linha, valores in enumerate(TECLADO_MOEDA):
            deslocamento = 1 if linha == 0 else 0
            largura = 1 if linha else 1
            for coluna, texto in enumerate(valores):
                if texto == "":
                    continue

                botao = self._criar_botao_teclado(frame, texto)
                botao.grid(
                    row=linha,
                    column=coluna + deslocamento,
                    sticky="nsew",
                    padx=1,
                    pady=1,
                    columnspan=largura,
                )

    def _criar_botao_teclado(
        self,
        parent: tk.Widget,
        texto: str,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=texto,
            bg=Tema.COR_BOTAO,
            fg=Tema.COR_TEXTO,
            activebackground=Tema.COR_BOTAO_HOVER,
            activeforeground=Tema.COR_TEXTO,
            font=("Segoe UI", 17),
            width=4,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            command=lambda valor=texto: self.ao_clicar(valor),
        )

    # ==========================================================
    # EVENTOS
    # ==========================================================

    def ao_clicar(self, valor: str) -> None:
        self._fechar_menu_moeda()

        if valor.isdigit():
            self._inserir_digito(valor)
            return

        if valor == ",":
            self._inserir_decimal()
            return

        if valor == "CE":
            self.valor_digitado = "0"
            self._atualizar_tela()
            return

        if valor == "⌫":
            self._apagar_ultimo()

    def processar_tecla(self, event: tk.Event) -> str | None:
        if self.focus_get() in {self.entrada_origem, self.entrada_destino}:
            return None

        if event.keysym in {"Alt_L", "Alt_R", "Control_L", "Control_R"}:
            return None

        if event.keysym == "Escape":
            self.ao_clicar("CE")
            return "break"

        if event.keysym == "BackSpace":
            self.ao_clicar("⌫")
            return "break"

        if event.char and event.char.isdigit():
            self.ao_clicar(event.char)
            return "break"

        if event.char in {",", "."}:
            self.ao_clicar(",")
            return "break"

        return None

    def _inserir_digito(self, digito: str) -> None:
        if self._campo_ativo_tem_selecao() or self.valor_digitado == "0":
            self.valor_digitado = digito
        else:
            self.valor_digitado += digito

        self._atualizar_tela()

    def _selecionar_campo(self, alvo: str) -> None:
        self.campo_ativo = alvo
        entrada = (
            self.entrada_origem
            if alvo == "origem"
            else self.entrada_destino
        )
        self.valor_digitado = self._normalizar_texto_valor(
            entrada.get()
        )
        entrada.after_idle(lambda: entrada.select_range(0, "end"))

    def _ao_editar_valor(self, alvo: str) -> None:
        if self.atualizando_campos:
            return

        self.campo_ativo = alvo
        texto = (
            self.texto_origem.get()
            if alvo == "origem"
            else self.texto_destino.get()
        )
        self.valor_digitado = self._normalizar_texto_valor(texto)
        self._atualizar_tela()

    def _inserir_decimal(self) -> None:
        if self._campo_ativo_tem_selecao():
            self.valor_digitado = "0,"
            self._atualizar_tela()
            return

        if "," not in self.valor_digitado:
            self.valor_digitado += ","

        self._atualizar_tela()

    def _apagar_ultimo(self) -> None:
        if self._campo_ativo_tem_selecao() or len(self.valor_digitado) <= 1:
            self.valor_digitado = "0"
        else:
            self.valor_digitado = self.valor_digitado[:-1]
            if self.valor_digitado.endswith(","):
                self.valor_digitado = self.valor_digitado[:-1] or "0"

        self._atualizar_tela()

    def _campo_ativo_tem_selecao(self) -> bool:
        entrada = (
            self.entrada_origem
            if self.campo_ativo == "origem"
            else self.entrada_destino
        )
        try:
            return bool(entrada.selection_present())
        except tk.TclError:
            return False

    # ==========================================================
    # MOEDAS E TAXAS
    # ==========================================================

    def _alternar_menu_moeda(self, alvo: str) -> None:
        if self._painel_existe(self.frame_menu_moeda):
            self._fechar_menu_moeda()
            return

        self.alvo_menu_moeda = alvo
        referencia = (
            self.botao_origem
            if alvo == "origem"
            else self.botao_destino
        )
        self.frame_menu_moeda = self._criar_painel_moeda(alvo)
        self._posicionar_painel(self.frame_menu_moeda, referencia)

    def _criar_painel_moeda(self, alvo: str) -> tk.Frame:
        painel = tk.Frame(
            self,
            bg=Tema.COR_MENU,
            bd=0,
        )
        painel.columnconfigure(0, weight=1)
        painel.rowconfigure(0, weight=1)

        canvas = tk.Canvas(
            painel,
            bg=Tema.COR_MENU,
            highlightthickness=0,
            bd=0,
        )
        canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas_menu_moeda = canvas

        barra = tk.Canvas(
            painel,
            bg=Tema.COR_MENU,
            highlightthickness=0,
            bd=0,
            width=8,
        )
        barra.grid(row=0, column=1, sticky="ns")
        self.scrollbar_menu_moeda = barra
        self.thumb_menu_moeda = barra.create_rectangle(
            2,
            2,
            6,
            40,
            fill="#f4f4f4",
            outline="",
        )
        barra.tag_bind(
            self.thumb_menu_moeda,
            "<ButtonPress-1>",
            self._iniciar_arraste_scroll_moeda,
        )
        barra.tag_bind(
            self.thumb_menu_moeda,
            "<B1-Motion>",
            self._arrastar_scroll_moeda,
        )
        barra.bind(
            "<ButtonPress-1>",
            self._clicar_scrollbar_moeda,
        )
        barra.bind(
            "<B1-Motion>",
            self._arrastar_scroll_moeda,
        )
        canvas.configure(
            yscrollcommand=lambda primeiro, ultimo: (
                self._atualizar_scrollbar_moeda(primeiro, ultimo)
            )
        )

        conteudo = tk.Frame(canvas, bg=Tema.COR_MENU)
        janela = canvas.create_window(
            (0, 0),
            window=conteudo,
            anchor="nw",
        )

        conteudo.bind(
            "<Configure>",
            lambda _evento: canvas.configure(
                scrollregion=canvas.bbox("all")
            ),
        )
        canvas.bind(
            "<Configure>",
            lambda evento: canvas.itemconfigure(
                janela,
                width=evento.width,
            ),
        )
        canvas.bind(
            "<MouseWheel>",
            self._rolar_menu_moeda,
        )
        painel.bind("<MouseWheel>", self._rolar_menu_moeda)
        conteudo.bind("<MouseWheel>", self._rolar_menu_moeda)
        barra.bind("<MouseWheel>", self._rolar_menu_moeda)

        moeda_atual = (
            self.moeda_origem
            if alvo == "origem"
            else self.moeda_destino
        )

        for linha, codigo in enumerate(MOEDAS):
            nome, simbolo = MOEDAS[codigo]
            selecionado = codigo == moeda_atual
            cor_fundo = Tema.COR_BOTAO_HOVER if selecionado else Tema.COR_MENU

            item = tk.Frame(conteudo, bg=cor_fundo)
            item.grid(row=linha, column=0, sticky="ew", padx=7, pady=1)
            item.columnconfigure(1, weight=1)
            conteudo.columnconfigure(0, weight=1)
            item.bind("<MouseWheel>", self._rolar_menu_moeda)

            indicador = tk.Frame(
                item,
                bg=Tema.COR_BOTAO_IGUAL if selecionado else cor_fundo,
                width=3,
            )
            indicador.grid(row=0, column=0, sticky="ns")

            botao = tk.Button(
                item,
                text=nome,
                bg=cor_fundo,
                fg=Tema.COR_TEXTO,
                activebackground=Tema.COR_BOTAO_HOVER,
                activeforeground=Tema.COR_TEXTO,
                font=("Segoe UI", 10),
                relief="flat",
                bd=0,
                highlightthickness=0,
                anchor="w",
                padx=10,
                pady=8,
                cursor="hand2",
                command=lambda moeda=codigo: self._selecionar_moeda(
                    alvo,
                    moeda,
                ),
            )
            botao.grid(row=0, column=1, sticky="ew")
            botao.bind("<MouseWheel>", self._rolar_menu_moeda)

        return painel

    def _selecionar_moeda(self, alvo: str, moeda: str) -> None:
        if alvo == "origem":
            self.moeda_origem = moeda
        else:
            self.moeda_destino = moeda

        self._fechar_menu_moeda()
        self._atualizar_tela()

    def _rolar_menu_moeda(self, evento: tk.Event) -> str:
        if self.canvas_menu_moeda is None:
            return "break"

        unidades = int(-1 * (evento.delta / 120))
        if unidades == 0:
            unidades = -1 if evento.delta > 0 else 1

        self.canvas_menu_moeda.yview_scroll(unidades, "units")
        return "break"

    def _clicar_scrollbar_moeda(self, evento: tk.Event) -> str:
        if (
            self.canvas_menu_moeda is None
            or self.scrollbar_menu_moeda is None
        ):
            return "break"

        altura = max(1, self.scrollbar_menu_moeda.winfo_height())
        destino = max(0.0, min(1.0, evento.y / altura))
        self.canvas_menu_moeda.yview_moveto(destino)
        self._iniciar_arraste_scroll_moeda(evento)
        return "break"

    def _iniciar_arraste_scroll_moeda(self, evento: tk.Event) -> str:
        self.scroll_drag_y = evento.y
        if self.canvas_menu_moeda is not None:
            self.scroll_drag_inicio = self.canvas_menu_moeda.yview()[0]
        else:
            self.scroll_drag_inicio = 0.0

        return "break"

    def _arrastar_scroll_moeda(self, evento: tk.Event) -> str:
        if (
            self.canvas_menu_moeda is None
            or self.scrollbar_menu_moeda is None
        ):
            return "break"

        altura = max(1, self.scrollbar_menu_moeda.winfo_height())
        delta = evento.y - self.scroll_drag_y
        destino = self.scroll_drag_inicio + (delta / altura)
        self.canvas_menu_moeda.yview_moveto(max(0.0, min(1.0, destino)))
        return "break"

    def _atualizar_scrollbar_moeda(
        self,
        primeiro: str,
        ultimo: str,
    ) -> None:
        if (
            self.scrollbar_menu_moeda is None
            or self.thumb_menu_moeda is None
        ):
            return

        inicio = float(primeiro)
        fim = float(ultimo)
        altura = max(1, self.scrollbar_menu_moeda.winfo_height())
        y1 = max(2, int(inicio * altura))
        y2 = min(altura - 2, int(fim * altura))
        if y2 - y1 < 28:
            y2 = min(altura - 2, y1 + 28)

        self.scrollbar_menu_moeda.coords(
            self.thumb_menu_moeda,
            2,
            y1,
            6,
            y2,
        )

    def _atualizar_taxas(self) -> None:
        if self.atualizando_taxas:
            return

        self.atualizando_taxas = True
        self.texto_status.set("Atualizando...")
        thread = threading.Thread(
            target=self._baixar_taxas,
            daemon=True,
        )
        thread.start()

    def _baixar_taxas(self) -> None:
        url = "https://open.er-api.com/v6/latest/USD"

        try:
            with urlopen(url, timeout=8) as resposta:
                dados = json.loads(resposta.read().decode("utf-8"))

            if dados.get("result") != "success":
                raise ValueError("Resposta sem sucesso")

            resposta_taxas = dados.get("rates", {})
            if not isinstance(resposta_taxas, dict):
                raise ValueError("Resposta sem taxas")

            taxas = {"USD": Decimal("1")}
            for codigo in MOEDAS:
                valor = resposta_taxas.get(codigo)
                if valor is not None:
                    taxas[codigo] = Decimal(str(valor))

            if len(taxas) < 2:
                raise ValueError("Resposta sem taxas")

            self.fila_resultado_taxas.put(("sucesso", taxas))
        except (
            URLError,
            TimeoutError,
            ValueError,
            InvalidOperation,
            json.JSONDecodeError,
        ) as erro:
            self.fila_resultado_taxas.put(("erro", erro))

    def _processar_resultados_taxas(self) -> None:
        try:
            while True:
                tipo, resultado = self.fila_resultado_taxas.get_nowait()
                if tipo == "sucesso" and isinstance(resultado, dict):
                    self._aplicar_taxas(resultado)
                elif isinstance(resultado, Exception):
                    self._falha_atualizar_taxas(resultado)
        except queue.Empty:
            pass

        if self.winfo_exists():
            self.after(100, self._processar_resultados_taxas)

    def _aplicar_taxas(self, taxas: dict[str, Decimal]) -> None:
        self.taxas_usd.update(taxas)
        self.atualizado_em = datetime.now()
        self.atualizando_taxas = False
        self.texto_status.set("")
        self._atualizar_tela()

    def _falha_atualizar_taxas(self, _erro: Exception) -> None:
        self.atualizando_taxas = False
        self.texto_status.set("")
        self._atualizar_tela()

    # ==========================================================
    # FORMATACAO E ESTADO
    # ==========================================================

    def _atualizar_tela(self) -> None:
        valor = self._valor_decimal()
        taxa = self._taxa(self.moeda_origem, self.moeda_destino)
        convertido = (
            valor * taxa
            if self.campo_ativo == "origem"
            else self._converter_reverso(valor)
        )

        self.label_simbolo_origem.config(text=MOEDAS[self.moeda_origem][1])
        self.label_simbolo_destino.config(text=MOEDAS[self.moeda_destino][1])
        self.botao_origem.config(
            text=f"{MOEDAS[self.moeda_origem][0]}  ⌄"
        )
        self.botao_destino.config(
            text=f"{MOEDAS[self.moeda_destino][0]}  ⌄"
        )
        self.atualizando_campos = True
        if self.campo_ativo == "origem":
            self.texto_origem.set(self._formatar_entrada())
            self.texto_destino.set(self._formatar_decimal(convertido))
        else:
            self.texto_destino.set(self._formatar_entrada())
            self.texto_origem.set(self._formatar_decimal(convertido))
        self.atualizando_campos = False
        self.texto_taxa.set(
            f"1 {self.moeda_origem} = "
            f"{self._formatar_decimal(taxa, casas=4)} "
            f"{self.moeda_destino}"
        )
        self.texto_atualizacao.set(
            "Atualizado "
            f"{self.atualizado_em.strftime('%d/%m/%Y %H:%M')}"
        )

    def _valor_decimal(self) -> Decimal:
        texto = self.valor_digitado.replace(",", ".")
        try:
            return Decimal(texto)
        except InvalidOperation:
            return Decimal("0")

    def _converter(self, valor: Decimal) -> Decimal:
        return valor * self._taxa(self.moeda_origem, self.moeda_destino)

    def _converter_reverso(self, valor: Decimal) -> Decimal:
        taxa = self._taxa(self.moeda_origem, self.moeda_destino)
        if taxa == 0:
            return Decimal("0")

        return valor / taxa

    def _taxa(self, origem: str, destino: str) -> Decimal:
        taxa_origem = self.taxas_usd.get(origem, Decimal("1"))
        taxa_destino = self.taxas_usd.get(destino, Decimal("1"))
        if taxa_origem == 0:
            return Decimal("0")

        return taxa_destino / taxa_origem

    def _formatar_entrada(self) -> str:
        return self.valor_digitado

    @staticmethod
    def _normalizar_texto_valor(texto: str) -> str:
        texto = texto.strip().replace(".", ",")
        filtrado = []
        decimal_usado = False

        for caractere in texto:
            if caractere.isdigit():
                filtrado.append(caractere)
            elif caractere == "," and not decimal_usado:
                filtrado.append(",")
                decimal_usado = True

        resultado = "".join(filtrado)
        if resultado in {"", ","}:
            return "0"

        return resultado

    @staticmethod
    def _formatar_decimal(
        valor: Decimal,
        casas: int = 2,
    ) -> str:
        quantizador = Decimal("1").scaleb(-casas)
        valor = valor.quantize(quantizador, rounding=ROUND_HALF_UP)
        texto = f"{valor:f}"

        if "." in texto:
            texto = texto.rstrip("0").rstrip(".")

        return texto.replace(".", ",") or "0"

    def _posicionar_painel(
        self,
        painel: tk.Frame,
        referencia: tk.Widget,
    ) -> None:
        self.update_idletasks()
        referencia.update_idletasks()

        x = referencia.winfo_rootx() - self.winfo_rootx()
        y_referencia = (
            referencia.winfo_rooty()
            - self.winfo_rooty()
            + referencia.winfo_height()
            + 2
        )
        y = max(8, min(y_referencia, 78))
        largura = max(300, self.winfo_width() - 8)
        altura = max(180, self.winfo_height() - y - 8)

        painel.place(
            x=max(4, min(x, self.winfo_width() - largura - 4)),
            y=y,
            width=largura,
            height=altura,
        )
        painel.lift()
        self._registrar_clique_fora_moeda()

    # ==========================================================
    # INTEGRACAO
    # ==========================================================

    def fechar_paineis(self) -> None:
        self._fechar_menu_moeda()

    def ao_exibir(self) -> None:
        self._atualizar_taxas()

    def alternar_historico(self) -> None:
        self.fechar_paineis()

    def _focar_visor_para_teclado(self) -> None:
        self.focus_set()

    def _fechar_menu_moeda(self) -> None:
        if self._painel_existe(self.frame_menu_moeda):
            self.frame_menu_moeda.destroy()

        self.frame_menu_moeda = None
        self.alvo_menu_moeda = None
        self.canvas_menu_moeda = None
        self.scrollbar_menu_moeda = None
        self.thumb_menu_moeda = None
        self._remover_clique_fora_moeda()

    def _registrar_clique_fora_moeda(self) -> None:
        if self.bind_clique_fora_moeda is not None:
            return

        self.bind_clique_fora_moeda = self.winfo_toplevel().bind(
            "<Button-1>",
            self._fechar_moeda_ao_clicar_fora,
            add="+",
        )

    def _remover_clique_fora_moeda(self) -> None:
        if self.bind_clique_fora_moeda is None:
            return

        try:
            self.winfo_toplevel().unbind(
                "<Button-1>",
                self.bind_clique_fora_moeda,
            )
        except tk.TclError:
            pass

        self.bind_clique_fora_moeda = None

    def _fechar_moeda_ao_clicar_fora(
        self,
        evento: tk.Event,
    ) -> str | None:
        if not self._painel_existe(self.frame_menu_moeda):
            self._remover_clique_fora_moeda()
            return None

        if self._ponto_dentro_widget(
            self.frame_menu_moeda,
            evento.x_root,
            evento.y_root,
        ):
            return None

        if self._ponto_dentro_widget(
            self.botao_origem,
            evento.x_root,
            evento.y_root,
        ):
            return None

        if self._ponto_dentro_widget(
            self.botao_destino,
            evento.x_root,
            evento.y_root,
        ):
            return None

        self._fechar_menu_moeda()
        return "break"

    @staticmethod
    def _ponto_dentro_widget(
        widget: tk.Widget,
        x_root: int,
        y_root: int,
    ) -> bool:
        if not widget.winfo_exists():
            return False

        x = widget.winfo_rootx()
        y = widget.winfo_rooty()
        largura = widget.winfo_width()
        altura = widget.winfo_height()

        return x <= x_root < x + largura and y <= y_root < y + altura

    @staticmethod
    def _painel_existe(painel: tk.Frame | None) -> bool:
        return painel is not None and bool(painel.winfo_exists())
