class AnalisadorSintatico:
    def __init__(self, tokens, tabela_simbolos):
        self.tokens = tokens
        self.tabela_simbolos = tabela_simbolos
        self.pos = 0
        self.token_atual = None
        self.escopo = []  # Pilha para rastrear os escopos
        self.avancar()

    def avancar(self):
        if self.pos < len(self.tokens):
            self.token_atual = self.tokens[self.pos]
            self.pos += 1
        else:
            self.token_atual = ('EOF', None, None)

    def consumir(self, tipo):
        if self.token_atual[0] == tipo:
            self.avancar()
        else:
            raise SyntaxError(f"Esperado {tipo}, encontrado {self.token_atual[0]} na linha {self.token_atual[2]}.")
     
    
    def entrar_escopo(self, tipo):
        self.escopo.append(tipo)

    def sair_escopo(self):
        if self.escopo:
            self.escopo.pop()

    def escopo_atual(self):
        return self.escopo[-1] if self.escopo else None


    def analisar(self):
        try:
            while self.token_atual[0] != "EOF":
                self.declaracao()
            print("Análise sintática concluída com sucesso!")
            return True
        except SyntaxError as e:
            print(f"Erro sintático: {e}")
            return False

    def declaracao(self):
        if self.token_atual[0] == "RESERVADA":
            if self.token_atual[1] in ["int", "boo"]:
                if self.tokens[self.pos][1] == "func":
                    self.declaracao_funcao()
                else:
                    self.declaracao_variavel()
            elif self.token_atual[1] == "proc":
                self.declaracao_procedimento()
            elif self.token_atual[1] in ["se", "senao", "enquanto", "leia", "escreva", "retorne", "continue", "pare"]:
                self.comando()
            else:
                raise SyntaxError(f"Comando não reconhecido {self.token_atual[1]} na linha {self.token_atual[2]}.")
        elif self.token_atual[0] == "IDENTIFICADOR":
            self.atribuicao_chamada()
        else:
            raise SyntaxError(f"Token não reconhecido {self.token_atual[0]} na linha {self.token_atual[2]}.")

    def declaracao_variavel(self):
        tipo = self.token_atual[1]
        self.consumir("RESERVADA")  # Consome o tipo
        identificador = self.token_atual[1]
        self.consumir("IDENTIFICADOR")  # Consome o identificador

        valor = None
        if self.token_atual[0] == "ATRIBUICAO":
            self.consumir("ATRIBUICAO")
            valor = self.expressao()
        self.tabela_simbolos.adicionar(identificador, tipo, valor)
        self.consumir("DELIMITADOR")  # Consome o ponto e vírgula

    def declaracao_procedimento(self):
        self.consumir("RESERVADA")  # Consome 'proc'
        nome = self.token_atual[1]
        self.consumir("IDENTIFICADOR")
        self.consumir("DELIMITADOR")  # Consome '('
        if self.token_atual[1] in ("int", "boo"):
            self.parametro()
            while self.token_atual[1] == ",":
                self.consumir("DELIMITADOR")
                self.parametro()
        self.consumir("DELIMITADOR")  # Consome ')'
        self.consumir("DELIMITADOR")  # Consome '{'
        while self.token_atual[1] != "}":
            self.declaracao()
        self.consumir("DELIMITADOR")  # Consome '}'
        self.tabela_simbolos.adicionar(nome, "proc")

    def declaracao_funcao(self):
        tipo = self.token_atual[1]  # Tipo da função
        self.consumir("RESERVADA")  # Consome tipo
        self.consumir("RESERVADA")  # Consome 'func'
        nome = self.token_atual[1]
        self.consumir("IDENTIFICADOR")
        self.consumir("DELIMITADOR")  # Consome '('
        if self.token_atual[0] == "RESERVADA":
            self.parametro()
            while self.token_atual[1] == ",":
                self.consumir("DELIMITADOR")
                self.parametro()
        self.consumir("DELIMITADOR")  # Consome ')'
        self.consumir("DELIMITADOR")  # Consome '{'

        self.entrar_escopo("funcao")  # Entra no escopo de função
        retorno = None
        while self.token_atual[1] != "}":
            if self.token_atual[0] == "RESERVADA" and self.token_atual[1] == "retorne":
                self.consumir("RESERVADA")  # Consome 'retorne'
                retorno = self.expressao()  # Avalia o valor a ser retornado
                self.consumir("DELIMITADOR")  # Consome o ponto e vírgula ';'
            else:
                self.declaracao()
        self.sair_escopo()  # Sai do escopo de função
        self.consumir("DELIMITADOR")  # Consome '}'
        self.tabela_simbolos.adicionar(nome, tipo, retorno)


    def parametro(self):
        tipo = self.token_atual[1]
        self.consumir("RESERVADA")
        identificador = self.token_atual[1]
        self.consumir("IDENTIFICADOR")
        self.tabela_simbolos.adicionar(identificador, tipo)

    def atribuicao_chamada(self):
        identificador = self.token_atual[1]
        if not self.identificador_declarado(identificador):
            raise SyntaxError(f"Identificador '{identificador}' não declarado.")
        self.consumir("IDENTIFICADOR")

        # Verifica se é uma chamada de função ou procedimento
        if self.token_atual[0] == "DELIMITADOR" and self.token_atual[1] == "(":
            retorno = self.chamada(identificador)  # Chama a função ou procedimento
            # Verifica se é uma atribuição válida
            for simbolo in self.tabela_simbolos.simbolos:
                if simbolo['identificador'] == identificador and simbolo['tipo'] == 'proc':
                    self.consumir("DELIMITADOR")  # Consome o ponto e vírgula após a chamada
                    return  # Procedimentos não retornam valores
            # Se for uma função, pode usar o retorno
            if retorno is not None:
                self.tabela_simbolos.atualizar(identificador, retorno)
            self.consumir("DELIMITADOR")  # Consome o ponto e vírgula após a atribuição
        elif self.token_atual[0] == "ATRIBUICAO":
            self.consumir("ATRIBUICAO")
            valor = self.expressao()
            self.tabela_simbolos.atualizar(identificador, valor)
            self.consumir("DELIMITADOR")  # Consome o ponto e vírgula


    def chamada(self, nome_funcao):
        self.consumir("DELIMITADOR")  # Consome '('
        argumentos = []
        if self.token_atual[0] != "DELIMITADOR" or self.token_atual[1] != ")":
            argumentos.append(self.expressao())
            while self.token_atual[1] == ",":
                self.consumir("DELIMITADOR")
                argumentos.append(self.expressao())
        self.consumir("DELIMITADOR")  # Consome ')'

        for simbolo in self.tabela_simbolos.simbolos:
            if simbolo['identificador'] == nome_funcao:
                if simbolo['tipo'] == 'proc':
                    return None
                elif simbolo['tipo'] == 'int':
                    return simbolo['valor'] if 'valor' in simbolo else 0  # Retorna valor
                elif simbolo['tipo'] == 'boo':
                    return simbolo['valor'] if 'valor' in simbolo else 'VERDADEIRO'
        raise SyntaxError(f"Função '{nome_funcao}' não declarada.")


    def argumentos(self):
        expressoes = [self.expressao()]
        while self.token_atual[1] == ",":
            self.consumir("DELIMITADOR")
            expressoes.append(self.expressao())
        return expressoes

    def comandos_simples(self):
        comando = self.token_atual[1]
        self.consumir("RESERVADA")
        self.consumir("DELIMITADOR")  # Consome '('
        
        if self.token_atual[0] != "IDENTIFICADOR":
            if comando == "leia":
                raise SyntaxError(f"Comando 'leia' espera um identificador na linha {self.token_atual[2]}.")
            else:
                raise SyntaxError(f"Comando 'escreva' espera um identificador na linha {self.token_atual[2]}.")
        identificador = self.token_atual[1]
        if not self.identificador_declarado(identificador):
            raise SyntaxError(f"Identificador '{identificador}' não declarado na linha {self.token_atual[2]}.")
        self.consumir("IDENTIFICADOR")
        self.consumir("DELIMITADOR")  # Consome ')'
        self.consumir("DELIMITADOR")  # Consome ';'

    def comando(self):
        if self.token_atual[1] == "se":
            self.tratar_condicional()
        elif self.token_atual[1] == "senao":
            self.tratar_condicional()
        elif self.token_atual[1] == "enquanto":
            self.tratar_laco()
        elif self.token_atual[1] == "retorne":
            if self.escopo_atual() != "funcao":
                raise SyntaxError(f"'retorne' só pode ser usado em funções na linha {self.token_atual[2]}.")
            self.consumir("RESERVADA")
            self.expressao()
            self.consumir("DELIMITADOR")
        elif self.token_atual[1] in ["continue", "pare"]:
            if self.escopo_atual() != "laco":
                raise SyntaxError(f"'{self.token_atual[1]}' só pode ser usado em laços na linha {self.token_atual[2]}.")
            self.consumir("RESERVADA")
            self.consumir("DELIMITADOR")
        elif self.token_atual[1] in ["leia", "escreva"]:
            self.comandos_simples()
        else:
            raise SyntaxError(f"Comando inválido '{self.token_atual[1]}' na linha {self.token_atual[2]}.")

    def tratar_condicional(self):
        if self.token_atual[1] == "se":
            self.consumir("RESERVADA")
            self.consumir("DELIMITADOR")
            self.expressao()
            self.consumir("DELIMITADOR")
            self.consumir("DELIMITADOR")
            while self.token_atual[1] != "}":
                self.declaracao()
            self.consumir("DELIMITADOR")
        else:
            self.consumir("RESERVADA")
            self.consumir("DELIMITADOR")
            while self.token_atual[1] != "}":
                self.declaracao()
            self.consumir("DELIMITADOR")

    def tratar_laco(self):
        self.consumir("RESERVADA")  # Consome 'enquanto'
        self.consumir("DELIMITADOR")  # Consome '('
        self.expressao()  # Avalia a condição do laço
        self.consumir("DELIMITADOR")  # Consome ')'
        self.consumir("DELIMITADOR")  # Consome '{'

        self.entrar_escopo("laco")  # Entra no escopo de laço
        try:
            while self.token_atual[0] != "DELIMITADOR" or self.token_atual[1] != "}":
                if self.token_atual[0] == "EOF":
                    raise SyntaxError(f"Fim inesperado ao processar o laço na linha {self.token_atual[2]}.")
                self.declaracao()  # Processa as declarações dentro do laço
        finally:
            self.sair_escopo()  # Sai do escopo de laço, mesmo em caso de erro

        self.consumir("DELIMITADOR")  # Consome '}'


    def expressao(self):
        valor = self.expressao_simples()
        while self.token_atual[0] == 'RELACIONAIS':
            operador = self.token_atual[1]
            self.consumir('RELACIONAIS')
            proximo_valor = self.expressao_simples()

            try:
                if operador == '>':
                    valor = "VERDADEIRO" if valor > proximo_valor else "FALSO"
                elif operador == '<':
                    valor = "VERDADEIRO" if valor < proximo_valor else "FALSO"
                elif operador == '==':
                    valor = "VERDADEIRO" if valor == proximo_valor else "FALSO"
                elif operador == '!=':
                    valor = "VERDADEIRO" if valor != proximo_valor else "FALSO"
                elif operador == '>=':
                    valor = "VERDADEIRO" if valor >= proximo_valor else "FALSO"
                elif operador == '<=':
                    valor = "VERDADEIRO" if valor <= proximo_valor else "FALSO"
            except TypeError:
                raise SyntaxError(f"Tipos incompatíveis na comparação '{operador}' na linha {self.token_atual[2]}.")
        return valor



    def expressao_simples(self):
        # Trata o sinal unário opcional
        if self.token_atual[0] == 'ARITMETICOS' and self.token_atual[1] in ('+', '-'):
            sinal = self.token_atual[1]
            self.consumir('ARITMETICOS')
            valor = self.termo()
            if sinal == '-':
                valor = -valor
        else:
            valor = self.termo()
            
        while (self.token_atual[0] == 'ARITMETICOS' and self.token_atual[1] in ('+', '-')) or \
            (self.token_atual[0] == 'LOGICOS' and self.token_atual[1] == 'ou'):
            operador = self.token_atual[1]
            self.consumir(self.token_atual[0])  # Consome o token correto
            proximo_valor = self.termo()
            try:
                if operador == '+':
                    valor += proximo_valor
                elif operador == '-':
                    valor -= proximo_valor
                elif operador == 'ou':
                    valor = valor or proximo_valor
            except TypeError:
                raise SyntaxError(f"Tipos incompatíveis na operação '{operador}' na linha {self.token_atual[2]}.")
        return valor

    def termo(self):
        valor = self.fator()
        while (self.token_atual[0] == 'ARITMETICOS' and self.token_atual[1] in ('*', '/')) or \
            (self.token_atual[0] == 'LOGICOS' and self.token_atual[1] == 'e'):
            operador = self.token_atual[1]
            self.consumir(self.token_atual[0])  # Consome o token correto (ARITMETICOS ou LOGICOS)
            proximo_valor = self.fator()
            try:
                if operador == '*':
                    valor *= proximo_valor
                elif operador == '/':
                    if proximo_valor == 0:
                        raise ZeroDivisionError(f"Divisão por zero na linha {self.token_atual[2]}.")
                    valor //= proximo_valor
                elif operador == 'e':
                    valor = valor and proximo_valor
            except TypeError:
                raise SyntaxError(f"Tipos incompatíveis na operação '{operador}' na linha {self.token_atual[2]}.")
            except ZeroDivisionError as zde:
                raise SyntaxError(f"{zde}")
        return valor

    def fator(self):
        if self.token_atual[0] == 'IDENTIFICADOR':
            identificador = self.token_atual[1]
            
            # Verifica se o identificador foi declarado
            if not self.identificador_declarado(identificador):
                raise SyntaxError(f"Identificador '{identificador}' não declarado na linha {self.token_atual[2]}.")

            self.consumir('IDENTIFICADOR')

            # Verifica se é uma chamada de função
            if self.token_atual[0] == 'DELIMITADOR' and self.token_atual[1] == '(':
                self.consumir('DELIMITADOR')  # Consome '('
                if self.token_atual[0] != 'DELIMITADOR' or self.token_atual[1] != ')':
                    self.argumentos()
                self.consumir('DELIMITADOR')  # Consome ')'

                # Retorna um valor simbólico dependendo do tipo da função
                for simbolo in self.tabela_simbolos.simbolos:
                    if simbolo['identificador'] == identificador and simbolo['tipo'] == 'int':
                        return 0  # Retorna um valor padrão para funções do tipo int
                    elif simbolo['identificador'] == identificador and simbolo['tipo'] == 'boo':
                        return 'FALSO'  # Retorna um valor padrão para funções do tipo boo
                return None  # Caso não encontre o tipo, retorna None

            # Caso contrário, é apenas um identificador
            for simbolo in self.tabela_simbolos.simbolos:
                if simbolo['identificador'] == identificador:
                    return simbolo['valor']
            raise ValueError(f"Identificador '{identificador}' não possui valor associado.")

        elif self.token_atual[0] == 'BOOLEANO':
            valor = self.token_atual[1]
            self.consumir('BOOLEANO')
            return valor
        elif self.token_atual[0] == 'INTEIRO':
            valor = int(self.token_atual[1])
            self.consumir('INTEIRO')
            return valor
        elif self.token_atual[0] == 'DELIMITADOR' and self.token_atual[1] == '(':
            self.consumir('DELIMITADOR')  # Consome '('
            valor = self.expressao()
            self.consumir('DELIMITADOR')  # Consome ')'
            return valor
        else:
            raise SyntaxError(f"Fator inválido {self.token_atual[0]} '{self.token_atual[1]}' na linha {self.token_atual[2]}.")


    def identificador_declarado(self, identificador):
        return any(simbolo['identificador'] == identificador for simbolo in self.tabela_simbolos.simbolos)
