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
            if valor:
                simbolo = self.tabela_simbolos.obter(valor)
                if simbolo and simbolo['valor'] and valor not in self.temp_geradas:
                    self.tabela_simbolos.adicionar_cte(f"{valor} = {simbolo['valor']}")
                    self.temp_geradas.add(valor)
                self.tabela_simbolos.adicionar_cte(f"{identificador} = {valor}")
            else:
                self.tabela_simbolos.adicionar_cte(f"decl {identificador} {tipo}")
        elif tipo == "proc":
            # Declaração de procedimento
            _, nome, params, corpo = estrutura
            self.tabela_simbolos.adicionar_cte(f"proc {nome}:")
            for param in params:
                self.tabela_simbolos.adicionar_cte(f"param {param[1]} {param[0]}")
            for decl in corpo:
                if decl[0] in ("int", "boo") and decl[2] is None:
                    self.tabela_simbolos.adicionar_cte(f"decl {decl[1]} {decl[0]}")
                else:
                    self.gerar_estrutura(decl)
        elif tipo == "func":
            # Declaração de função
            _, nome, tipo_retorno, params, corpo = estrutura
            self.tabela_simbolos.adicionar_cte(f"func {nome}:")
            for param in params:
                self.tabela_simbolos.adicionar_cte(f"param {param[1]} {param[0]}")
            for decl in corpo:
                if decl[0] in ("int", "boo") and decl[2] is None:
                    self.tabela_simbolos.adicionar_cte(f"decl {decl[1]} {decl[0]}")
                elif decl[0] == "atribuicao":
                    _, identificador, valor = decl
                    self.tabela_simbolos.adicionar_cte(f"{identificador} = {valor}")
                elif decl[0] == "retorne":
                    _, valor = decl
                    self.tabela_simbolos.adicionar_cte(f"return {valor}")
        elif tipo == "atribuicao":
            # Atribuição de valor a uma variável
            _, identificador, valor = estrutura
            simbolo = self.tabela_simbolos.obter(valor)
            if simbolo and simbolo['valor'] and valor not in self.temp_geradas:
                self.tabela_simbolos.adicionar_cte(f"{valor} = {simbolo['valor']}")
                self.temp_geradas.add(valor)
            self.tabela_simbolos.adicionar_cte(f"{identificador} = {valor}")
        elif tipo == "chamada":
            # Chamada de função ou procedimento
            _, nome, resultado = estrutura
            if resultado:
                if nome == resultado.split('(')[0]:  # Procedimento
                    self.tabela_simbolos.adicionar_cte(f"call {resultado}")
                else:  # Função
                    simbolo = self.tabela_simbolos.obter(resultado)
                    if simbolo and simbolo['valor'] and resultado not in self.temp_geradas:
                        self.tabela_simbolos.adicionar_cte(f"{resultado} = {simbolo['valor']}")
                        self.temp_geradas.add(resultado)
        elif tipo == "se":
            self.gerar_condicional(estrutura)
        elif tipo == "enquanto":
            self.gerar_laco(estrutura)
        elif tipo == "retorne":
            # Comando de retorno
            _, valor = estrutura
            self.tabela_simbolos.adicionar_cte(f"return {valor}")
        elif tipo in ("continue", "pare"):
            # Comandos de controle de fluxo
            self.tabela_simbolos.adicionar_cte(tipo)
        elif tipo in ("leia", "escreva"):
            # Comandos de entrada/saída
            _, identificador = estrutura
            self.tabela_simbolos.adicionar_cte(f"{tipo} {identificador}")

    def gerar_condicional(self, estrutura):
        # Gera CTE para uma estrutura condicional (se/senão)
        _, condicao, bloco_se, bloco_senao = estrutura
        simbolo = self.tabela_simbolos.obter(condicao)
        if simbolo and simbolo['valor'] and condicao not in self.temp_geradas:
            self.tabela_simbolos.adicionar_cte(f"{condicao} = {simbolo['valor']}")
            self.temp_geradas.add(condicao)
        label_else = self.novo_label()
        label_end = self.novo_label()
        self.tabela_simbolos.adicionar_cte(f"if {condicao} == FALSO goto {label_else}")
        for decl in bloco_se:
            self.gerar_estrutura(decl)
        self.tabela_simbolos.adicionar_cte(f"goto {label_end}")
        self.tabela_simbolos.adicionar_cte(f"{label_else}:")
        for decl in bloco_senao:
            self.gerar_estrutura(decl)
        self.tabela_simbolos.adicionar_cte(f"{label_end}:")

    def gerar_laco(self, estrutura):
        # Gera CTE para uma estrutura de laço (enquanto)
        _, condicao, corpo = estrutura
        label_start = self.novo_label()
        label_end = self.novo_label()
        self.tabela_simbolos.adicionar_cte(f"{label_start}:")
        simbolo = self.tabela_simbolos.obter(condicao)
        if simbolo and simbolo['valor'] and condicao not in self.temp_geradas:
            self.tabela_simbolos.adicionar_cte(f"{condicao} = {simbolo['valor']}")
            self.temp_geradas.add(condicao)
        self.tabela_simbolos.adicionar_cte(f"if {condicao} == FALSO goto {label_end}")
        for decl in corpo:
            self.gerar_estrutura(decl)
        self.tabela_simbolos.adicionar_cte(f"goto {label_start}")
        self.tabela_simbolos.adicionar_cte(f"{label_end}:")