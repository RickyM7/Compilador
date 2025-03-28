class AnalisadorSintatico:
    def __init__(self, tokens):
        # Inicializa o analisador sintático com a lista de tokens
        self.tokens = tokens
        self.pos = 0
        self.token_atual = None
        self.avancar()

    def avancar(self):
        # Avança para o próximo token, ou define EOF se acabar
        if self.pos < len(self.tokens):
            self.token_atual = self.tokens[self.pos]
            self.pos += 1
        else:
            ultima_linha = self.token_atual[2] if self.token_atual else None
            self.token_atual = ('EOF', None, ultima_linha)

    def consumir(self, tipo):
        # Consome um token esperado, ou levanta erro
        if self.token_atual[0] == tipo:
            self.avancar()
        else:
            raise SyntaxError(f"Esperado '{tipo}', encontrado '{self.token_atual[0]}' na linha {self.token_atual[2]}.")

    def analisar(self):
        # Analisa todos os tokens até o EOF
        while self.token_atual[0] != "EOF":
            self.declaracao()
        return True

    def declaracao(self):
        # Identifica e processa declarações ou comandos
        if self.token_atual[0] == "RESERVADA":
            if self.token_atual[1] in ["int", "boo"]:
                if self.pos < len(self.tokens) and self.tokens[self.pos][1] == "func":
                    self.declaracao_funcao()
                else:
                    self.declaracao_variavel()
            elif self.token_atual[1] == "proc":
                self.declaracao_procedimento()
            elif self.token_atual[1] in ["se", "enquanto", "leia", "escreva", "retorne", "continue", "pare"]:
                self.comando()
            else:
                raise SyntaxError(f"Comando não reconhecido {self.token_atual[1]} na linha {self.token_atual[2]}.")
        elif self.token_atual[0] == "IDENTIFICADOR":
            self.atribuicao_chamada()
        else:
            raise SyntaxError(f"Token não reconhecido {self.token_atual[0]} na linha {self.token_atual[2]}.")

    def declaracao_variavel(self):
        # Processa a declaração de uma variável
        self.consumir("RESERVADA")  # Tipo (int, boo)
        self.consumir("IDENTIFICADOR")
        if self.token_atual[0] == "ATRIBUICAO":
            self.consumir("ATRIBUICAO")
            self.expressao()
        self.consumir("DELIMITADOR")  # ";"

    def declaracao_procedimento(self):
        # Processa a declaração de um procedimento
        self.consumir("RESERVADA")  # "proc"
        self.consumir("IDENTIFICADOR")
        self.consumir("DELIMITADOR")  # "("
        if self.token_atual[1] in ("int", "boo"):
            self.parametro()
            while self.token_atual[1] == ",":
                self.consumir("DELIMITADOR")
                self.parametro()
        self.consumir("DELIMITADOR")  # ")"
        self.consumir("DELIMITADOR")  # "{"
        while self.token_atual[1] != "}":
            self.declaracao()
        self.consumir("DELIMITADOR")  # "}"

    def declaracao_funcao(self):
        # Processa a declaração de uma função
        self.consumir("RESERVADA")  # Tipo de retorno
        self.consumir("RESERVADA")  # "func"
        self.consumir("IDENTIFICADOR")
        self.consumir("DELIMITADOR")  # "("
        if self.token_atual[1] in ("int", "boo"):
            self.parametro()
            while self.token_atual[1] == ",":
                self.consumir("DELIMITADOR")
                self.parametro()
        self.consumir("DELIMITADOR")  # ")"
        self.consumir("DELIMITADOR")  # "{"
        while self.token_atual[1] != "}":
            if self.token_atual[0] == "RESERVADA" and self.token_atual[1] == "retorne":
                self.consumir("RESERVADA")
                self.expressao()
                self.consumir("DELIMITADOR")
            else:
                self.declaracao()
        self.consumir("DELIMITADOR")  # "}"

    def parametro(self):
        # Processa um parâmetro de função ou procedimento
        self.consumir("RESERVADA")  # Tipo
        self.consumir("IDENTIFICADOR")

    def atribuicao_chamada(self):
        # Processa uma atribuição ou chamada
        self.consumir("IDENTIFICADOR")
        if self.token_atual[0] == "DELIMITADOR" and self.token_atual[1] == "(":
            self.chamada()
            self.consumir("DELIMITADOR")  # ";"
        elif self.token_atual[0] == "ATRIBUICAO":
            self.consumir("ATRIBUICAO")
            self.expressao()
            self.consumir("DELIMITADOR")  # ";"

    def chamada(self):
        # Processa uma chamada de função ou procedimento
        self.consumir("DELIMITADOR")  # "("
        if self.token_atual[1] != ")":
            self.expressao()
            while self.token_atual[1] == ",":
                self.consumir("DELIMITADOR")
                self.expressao()
        self.consumir("DELIMITADOR")  # ")"

    def comando(self):
        # Identifica e processa comandos da linguagem
        if self.token_atual[1] == "se":
            self.tratar_condicional()
        elif self.token_atual[1] == "enquanto":
            self.tratar_laco()
        elif self.token_atual[1] == "retorne":
            self.consumir("RESERVADA")
            self.expressao()
            self.consumir("DELIMITADOR")
        elif self.token_atual[1] in ["continue", "pare"]:
            self.consumir("RESERVADA")
            self.consumir("DELIMITADOR")
        elif self.token_atual[1] in ["leia", "escreva"]:
            self.comandos_simples()

    def tratar_condicional(self):
        # Processa uma estrutura condicional (se/senão)
        self.consumir("RESERVADA")  # "se"
        self.consumir("DELIMITADOR")  # "("
        self.expressao()
        self.consumir("DELIMITADOR")  # ")"
        self.consumir("DELIMITADOR")  # "{"
        while self.token_atual[1] != "}":
            self.declaracao()
        self.consumir("DELIMITADOR")  # "}"
        if self.token_atual[1] == "senao":
            self.consumir("RESERVADA")
            self.consumir("DELIMITADOR")  # "{"
            while self.token_atual[1] != "}":
                self.declaracao()
            self.consumir("DELIMITADOR")  # "}"

    def tratar_laco(self):
        # Processa uma estrutura de laço (enquanto)
        self.consumir("RESERVADA")  # "enquanto"
        self.consumir("DELIMITADOR")  # "("
        self.expressao()
        self.consumir("DELIMITADOR")  # ")"
        self.consumir("DELIMITADOR")  # "{"
        while self.token_atual[1] != "}":
            self.declaracao()
        self.consumir("DELIMITADOR")  # "}"

    def comandos_simples(self):
        # Processa comandos simples como leia/escreva
        self.consumir("RESERVADA")
        self.consumir("DELIMITADOR")  # "("
        self.consumir("IDENTIFICADOR")
        self.consumir("DELIMITADOR")  # ")"
        self.consumir("DELIMITADOR")  # ";"

    def expressao(self):
        # Processa uma expressão com operadores relacionais
        self.expressao_simples()
        while self.token_atual[0] == "RELACIONAIS":
            self.consumir("RELACIONAIS")
            self.expressao_simples()

    def expressao_simples(self):
        # Processa uma expressão simples com operadores aritméticos ou lógicos
        if self.token_atual[0] == "ARITMETICOS" and self.token_atual[1] in ("+", "-"):
            self.consumir("ARITMETICOS")
            self.termo()
        else:
            self.termo()
        while (self.token_atual[0] == "ARITMETICOS" and self.token_atual[1] in ("+", "-")) or \
              (self.token_atual[0] == "LOGICOS" and self.token_atual[1] == "ou"):
            self.consumir(self.token_atual[0])
            self.termo()

    def termo(self):
        # Processa um termo com operadores de multiplicação ou lógico "e"
        self.fator()
        while (self.token_atual[0] == "ARITMETICOS" and self.token_atual[1] in ("*", "/")) or \
              (self.token_atual[0] == "LOGICOS" and self.token_atual[1] == "e"):
            self.consumir(self.token_atual[0])
            self.fator()

    def fator(self):
        # Processa um fator (identificador, literal ou expressão entre parênteses)
        if self.token_atual[0] in ("IDENTIFICADOR", "BOOLEANO", "INTEIRO"):
            self.consumir(self.token_atual[0])
            if self.token_atual[0] == "DELIMITADOR" and self.token_atual[1] == "(":
                self.chamada()
        elif self.token_atual[0] == "DELIMITADOR" and self.token_atual[1] == "(":
            self.consumir("DELIMITADOR")
            self.expressao()
            self.consumir("DELIMITADOR")
        else:
            raise SyntaxError(f"Fator inválido {self.token_atual[1]} na linha {self.token_atual[2]}.")