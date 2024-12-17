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
        if self.token_atual[1] in ("int", "boo"):
            self.parametro()
            while self.token_atual[1] == ",":
                self.consumir("DELIMITADOR")
                self.parametro()
        self.consumir("DELIMITADOR")  # Consome ')'
        self.consumir("DELIMITADOR")  # Consome '{'

        self.entrar_escopo("funcao")  # Entra no escopo de função
        while self.token_atual[1] != "}":
            self.declaracao()
        self.sair_escopo()  # Sai do escopo de função
        self.consumir("DELIMITADOR")  # Consome '}'
        self.tabela_simbolos.adicionar(nome, tipo)


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
        if self.token_atual[0] == "ATRIBUICAO":
            self.consumir("ATRIBUICAO")
            valor = self.expressao()
            self.tabela_simbolos.atualizar(identificador, valor)
            self.consumir("DELIMITADOR")
        elif self.token_atual[0] == "DELIMITADOR" and self.token_atual[1] == "(":
            self.chamada()

    def chamada(self):
        self.consumir("DELIMITADOR")
        if self.token_atual[0] != "DELIMITADOR" or self.token_atual[1] != ")":
            self.argumentos()
        self.consumir("DELIMITADOR")
        self.consumir("DELIMITADOR")

    def argumentos(self):
        self.expressao()
        while self.token_atual[1] == ",":
            self.consumir("DELIMITADOR")
            self.expressao()

    def comandos_simples(self):
        self.consumir("RESERVADA")
        if self.token_atual[1] == "(":
            self.consumir("DELIMITADOR")
            self.expressao()  # qualquer expressão dentro do leia, escreva
            self.consumir("DELIMITADOR")
        self.consumir("DELIMITADOR")

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
        self.expressao()
        self.consumir("DELIMITADOR")  # Consome ')'
        self.consumir("DELIMITADOR")  # Consome '{'
        
        self.entrar_escopo("laco")  # Entra no escopo de laço
        while self.token_atual[1] != "}":
            self.declaracao()
        self.sair_escopo()  # Sai do escopo de laço
        self.consumir("DELIMITADOR")  # Consome '}'


    def expressao(self):
        self.expressao_simples()
        if self.token_atual[0] == 'RELACIONAIS':
            self.consumir('RELACIONAIS')
            self.expressao_simples()

    def expressao_simples(self):
        self.termo()
        while self.token_atual[0] == 'ARITMETICOS':
            self.consumir('ARITMETICOS')
            self.termo()

    def termo(self):
        self.fator()
        while self.token_atual[0] == 'ARITMETICOS':
            self.consumir('ARITMETICOS')
            self.fator()

    def fator(self):
        if self.token_atual[0] == 'IDENTIFICADOR':
            # Verifica se o identificador foi declarado
            if not self.identificador_declarado(self.token_atual[1]):
                raise SyntaxError(f"Identificador '{self.token_atual[1]}' não declarado na linha {self.token_atual[2]}.")
            self.consumir('IDENTIFICADOR')
        elif self.token_atual[0] == 'BOOLEANO':
            # Verifica se o valor é um booleano válido (VERDADEIRO ou FALSO)
            if self.token_atual[1] not in ['VERDADEIRO', 'FALSO']:
                raise SyntaxError(f"Valor booleano inválido '{self.token_atual[1]}' na linha {self.token_atual[2]}.")
            self.consumir('BOOLEANO')
        elif self.token_atual[0] == 'INTEIRO':
            self.consumir('INTEIRO')
        elif self.token_atual[0] == 'DELIMITADOR' and self.token_atual[1] == '(':
            self.consumir('DELIMITADOR')  # Consome '('
            self.expressao()
            self.consumir('DELIMITADOR')  # Consome ')'
        else:
            raise SyntaxError(f"Fator inválido {self.token_atual[0]} '{self.token_atual[1]}' na linha {self.token_atual[2]}.")


    def identificador_declarado(self, identificador):
        return any(simbolo['identificador'] == identificador for simbolo in self.tabela_simbolos.simbolos)
