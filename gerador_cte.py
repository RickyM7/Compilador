class GeradorCTE:
    def __init__(self, tabela_simbolos):
        # Inicializa o gerador de código de três endereços (CTE) com a tabela de símbolos
        self.tabela_simbolos = tabela_simbolos
        self.labels = 0  # Contador para gerar rótulos únicos
        self.temp_geradas = set()  # Conjunto para rastrear variáveis temporárias geradas

    def novo_label(self):
        # Gera um novo rótulo único (ex.: L1, L2)
        self.labels += 1
        return f"L{self.labels}"

    def gerar(self, estruturas):
        # Gera o código CTE a partir das estruturas fornecidas
        self.temp_geradas.clear()  # Limpa temporárias antes de começar
        self.tabela_simbolos.cte.clear()  # Limpa o CTE anterior
        for estrutura in estruturas:
            self.gerar_estrutura(estrutura)

    def gerar_estrutura(self, estrutura):
        # Processa cada estrutura (declaração, comando, etc.) para gerar CTE
        if not isinstance(estrutura, tuple):
            return
        tipo = estrutura[0]
        if tipo in ("int", "boo"):
            # Declaração de variável com ou sem inicialização
            _, identificador, valor = estrutura
            if valor and isinstance(valor, str):
                simbolo = self.tabela_simbolos.obter(valor)
                if simbolo and simbolo.get('valor') and '(' in str(simbolo.get('valor')):
                    chamada = simbolo['valor']
                    nome_funcao = chamada.split("(")[0]
                    args = [arg.strip() for arg in chamada.split("(")[1].rstrip(")").split(",") if arg.strip()]
                    for arg in args:
                        self.tabela_simbolos.adicionar_cte(f"param {arg}")
                    self.tabela_simbolos.adicionar_cte(f"{valor} := call {nome_funcao}, {len(args)}")
                    self.tabela_simbolos.adicionar_cte(f"{identificador} := {valor}")
                else:
                    self.gerar_valor(valor)
                    self.tabela_simbolos.adicionar_cte(f"{identificador} := {valor}")
        elif tipo == "proc":
            # Declaração de procedimento
            _, nome, params, corpo = estrutura
            self.tabela_simbolos.adicionar_cte(f"proc {nome}")
            for param in params:
                self.tabela_simbolos.adicionar_cte(f"param {param[1]} {param[0]}")
            for decl in corpo:
                self.gerar_estrutura(decl)
            self.tabela_simbolos.adicionar_cte("endproc")
        elif tipo == "func":
            # Declaração de função
            _, nome, tipo_retorno, params, corpo = estrutura
            self.tabela_simbolos.adicionar_cte(f"func {nome}")
            for param in params:
                self.tabela_simbolos.adicionar_cte(f"param {param[1]} {param[0]}")
            for decl in corpo:
                if decl[0] in ("int", "boo") and decl[2] is None:
                    self.tabela_simbolos.adicionar_cte(f"decl {decl[1]} {decl[0]}")
                else:
                    self.gerar_estrutura(decl)
            self.tabela_simbolos.adicionar_cte("endfunc")
        elif tipo == "atribuicao":
            # Atribuição de valor a uma variável
            _, identificador, valor = estrutura
            self.gerar_valor(valor)
            self.tabela_simbolos.adicionar_cte(f"{identificador} := {valor}")
        elif tipo == "se":
            self.gerar_condicional(estrutura)
        elif tipo == "enquanto":
            self.gerar_laco(estrutura)
        elif tipo == "retorne":
            # Comando de retorno
            _, valor = estrutura
            self.gerar_valor(valor)
            self.tabela_simbolos.adicionar_cte(f"return {valor}")
        elif tipo == "pare":
            self.tabela_simbolos.adicionar_cte(f"goto {self.label_fim_laco}")
        elif tipo == "continue":
            self.tabela_simbolos.adicionar_cte(f"goto {self.label_inicio_laco}")
        elif tipo == "escreva":
            # Comandos de entrada/saída
            _, identificador = estrutura
            self.tabela_simbolos.adicionar_cte(f"escreva {identificador}")

    def gerar_valor(self, valor):
        simbolo = self.tabela_simbolos.obter(valor)
        if simbolo and simbolo['valor'] and valor not in self.temp_geradas:
            if isinstance(simbolo['valor'], str) and any(op in simbolo['valor'] for op in ['+', '-', '*', '/', '>', '<', '>=', '<=', '==', '!=']):
                self.tabela_simbolos.adicionar_cte(f"{valor} := {simbolo['valor']}")
                self.temp_geradas.add(valor)

    def gerar_condicional(self, estrutura):
        # Gera CTE para uma estrutura condicional (se/senão)
        _, condicao, bloco_se, bloco_senao = estrutura
        self.gerar_valor(condicao)
        self.tabela_simbolos.adicionar_cte(f"if {condicao} == 1 goto {self.label_fim_laco}")
        for decl in bloco_senao:
            self.gerar_estrutura(decl)

    def gerar_laco(self, estrutura):
        # Gera CTE para uma estrutura de laço (enquanto)
        _, condicao, corpo = estrutura
        self.label_inicio_laco = self.novo_label()
        self.label_fim_laco = self.novo_label()
        self.tabela_simbolos.adicionar_cte(f"{self.label_inicio_laco}:")
        self.gerar_valor(condicao)
        self.tabela_simbolos.adicionar_cte(f"if {condicao} == 0 goto {self.label_fim_laco}")
        for decl in corpo:
            self.gerar_estrutura(decl)
        if not (corpo and isinstance(corpo[-1], tuple) and corpo[-1][0] == "se" and 
                corpo[-1][3] and isinstance(corpo[-1][3][-1], tuple) and corpo[-1][3][-1][0] == "continue"):
            self.tabela_simbolos.adicionar_cte(f"goto {self.label_inicio_laco}")
        self.tabela_simbolos.adicionar_cte(f"{self.label_fim_laco}:")